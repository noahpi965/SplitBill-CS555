from collections import defaultdict
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from extensions import db
from models import Bill, BillParticipant, Reminder, Settlement

bills_bp = Blueprint("bills", __name__)

RATIO_SUM_TOLERANCE = 0.01


def _split_equally(total_amount, participants):
    """Split an amount into equal shares, spreading leftover cents so shares sum to the total."""
    total_cents = round(total_amount * 100)
    base, remainder = divmod(total_cents, len(participants))
    return [(base + (1 if i < remainder else 0)) / 100 for i in range(len(participants))]


def _split_by_percent(total_amount, percents):
    """Split by percentage list. Last participant absorbs leftover cents."""
    total_cents = round(float(total_amount) * 100)
    shares_cents = []
    allocated = 0
    for i, pct in enumerate(percents):
        if i == len(percents) - 1:
            shares_cents.append(total_cents - allocated)
        else:
            cents = round(total_cents * float(pct) / 100)
            shares_cents.append(cents)
            allocated += cents
    return [c / 100 for c in shares_cents]


def _parse_participants(raw):
    if not isinstance(raw, list) or not raw:
        return None, "At least one participant is required."
    participants = [p.strip() for p in raw if isinstance(p, str) and p.strip()]
    if not participants:
        return None, "At least one participant is required."
    if len(set(participants)) != len(participants):
        return None, "Participants must be unique."
    return participants, None


def _parse_ratios(participants, data):
    """Return a percent list aligned with participants, or an error string."""
    split_type = (data.get("split_type") or "equal").strip().lower()
    if split_type not in ("equal", "custom"):
        return None, None, "split_type must be 'equal' or 'custom'."
    if split_type == "equal":
        return split_type, None, None

    ratios = data.get("ratios")
    if not isinstance(ratios, dict) or not ratios:
        return None, None, "Custom split requires a ratios object mapping each participant to a percentage."

    percents = []
    for name in participants:
        if name not in ratios:
            return None, None, f"Missing ratio for {name}."
        try:
            value = float(ratios[name])
        except (TypeError, ValueError):
            return None, None, "Each ratio must be a number."
        if value < 0:
            return None, None, "Ratios cannot be negative."
        percents.append(round(value, 2))

    extra = set(ratios.keys()) - set(participants)
    if extra:
        return None, None, f"Ratios include unknown participants: {', '.join(sorted(extra))}."

    if abs(sum(percents) - 100) > RATIO_SUM_TOLERANCE:
        return None, None, "Ratios must sum to 100%."

    return split_type, percents, None


def _shares_for(total_amount, participants, split_type, percents):
    if split_type == "custom":
        return _split_by_percent(total_amount, percents)
    return _split_equally(total_amount, participants)


def _replace_participants(bill, participants, shares):
    bill.participants.clear()
    db.session.flush()
    for name, share in zip(participants, shares):
        bill.participants.append(BillParticipant(user_name=name, share=share))


def _validate_bill(data):
    errors = {}

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        errors["title"] = "Title is required."

    amount = data.get("total_amount")
    if amount is None or amount == "":
        errors["total_amount"] = "Amount is required."
    else:
        try:
            amount = float(amount)
            if amount <= 0:
                errors["total_amount"] = "Amount must be greater than 0."
        except (TypeError, ValueError):
            errors["total_amount"] = "Amount must be a number."

    paid_by = data.get("paid_by")
    if not isinstance(paid_by, str) or not paid_by.strip():
        errors["paid_by"] = "Payer is required."

    group_id = data.get("group_id")
    if isinstance(group_id, bool) or not isinstance(group_id, int):
        errors["group_id"] = "group_id must be an integer."

    participants, participant_error = _parse_participants(data.get("participants"))
    if participant_error:
        errors["participants"] = participant_error

    split_type = percents = None
    if participants:
        split_type, percents, ratio_error = _parse_ratios(participants, data)
        if ratio_error:
            errors["ratios"] = ratio_error

    created_at = None
    if data.get("date"):
        try:
            created_at = datetime.strptime(data["date"], "%Y-%m-%d")
        except (TypeError, ValueError):
            errors["date"] = "Date must use YYYY-MM-DD format."

    if errors:
        return None, errors

    return {
        "title":        title.strip(),
        "total_amount": round(amount, 2),
        "paid_by":      paid_by.strip(),
        "group_id":     group_id,
        "category":     (data.get("category") or "General").strip() or "General",
        "participants": participants,
        "split_type":   split_type,
        "percents":     percents,
        "created_at":   created_at,
    }, None


def _bill_net_cents(group_id):
    net_cents = defaultdict(int)
    for bill in Bill.query.filter_by(group_id=group_id).all():
        for p in bill.participants:
            if p.settled or p.user_name == bill.paid_by:
                continue
            cents = round(p.share * 100)
            net_cents[bill.paid_by] += cents
            net_cents[p.user_name] -= cents
    return net_cents


def _apply_settlements(group_id, net_cents):
    for s in Settlement.query.filter_by(group_id=group_id).order_by(Settlement.id).all():
        cents = round(s.amount * 100)
        net_cents[s.from_user] += cents
        net_cents[s.to_user] -= cents
    return net_cents


def _pair_balances(net_cents):
    creditors = sorted(((n, c) for n, c in net_cents.items() if c > 0), key=lambda x: (-x[1], x[0]))
    debtors   = sorted(((n, -c) for n, c in net_cents.items() if c < 0), key=lambda x: (-x[1], x[0]))

    balances = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debtor, owe = debtors[i]
        creditor, due = creditors[j]
        amount = min(owe, due)
        balances.append({"from": debtor, "to": creditor, "amount": amount / 100})
        debtors[i] = (debtor, owe - amount)
        creditors[j] = (creditor, due - amount)
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1
    return balances


def _balance_payload(group_id):
    net_cents = _apply_settlements(group_id, _bill_net_cents(group_id))
    balances = _pair_balances(net_cents)
    members = {name: cents / 100 for name, cents in sorted(net_cents.items()) if cents != 0}
    history = [
        s.to_dict()
        for s in Settlement.query.filter_by(group_id=group_id).order_by(Settlement.created_at.desc(), Settlement.id.desc())
    ]
    body = {
        "group_id":         group_id,
        "balances":         balances,
        "net":              members,
        "all_settled":      not balances,
        "settled_history":  history,
    }
    if not balances:
        body["message"] = "All settled up"
    return body


def _outstanding_amount(group_id, debtor, creditor):
    for row in _balance_payload(group_id)["balances"]:
        if row["from"] == debtor and row["to"] == creditor:
            return row["amount"]
    return 0


def _unsettled_bill_details(group_id, debtor, creditor):
    titles = []
    for bill in Bill.query.filter_by(group_id=group_id).order_by(Bill.created_at.desc()).all():
        if bill.paid_by != creditor:
            continue
        for p in bill.participants:
            if p.user_name == debtor and not p.settled:
                titles.append(f"{bill.title} (${p.share:.2f})")
                break
    return titles


# ── US01 / US02: Add a Shared Bill (equal or custom split) ───────────────────
@bills_bp.route("/bills", methods=["POST"])
def add_bill():
    """
    Create a new shared bill.
    Body JSON: { title, total_amount, paid_by, group_id, participants: [name, ...],
                 split_type?: "equal"|"custom", ratios?: {name: percent},
                 category?, date? (YYYY-MM-DD) }
    """
    data = request.get_json(silent=True) or {}
    cleaned, errors = _validate_bill(data)
    if errors:
        return jsonify({"error": "Validation failed", "errors": errors}), 400

    bill = Bill(
        title=cleaned["title"],
        total_amount=cleaned["total_amount"],
        paid_by=cleaned["paid_by"],
        group_id=cleaned["group_id"],
        category=cleaned["category"],
        split_type=cleaned["split_type"],
    )
    if cleaned["created_at"]:
        bill.created_at = cleaned["created_at"]

    shares = _shares_for(
        cleaned["total_amount"], cleaned["participants"],
        cleaned["split_type"], cleaned["percents"],
    )
    for name, share in zip(cleaned["participants"], shares):
        bill.participants.append(BillParticipant(user_name=name, share=share))

    db.session.add(bill)
    db.session.commit()

    return jsonify({"message": "Bill created", "bill": bill.to_dict()}), 201


# ── US04: View Group Bills ───────────────────────────────────────────────────
@bills_bp.route("/bills", methods=["GET"])
def get_bills():
    """
    Return all bills for a group, newest first.
    Query param: ?group_id=<int>
    """
    group_id = request.args.get("group_id", type=int)
    if group_id is None:
        return jsonify({"error": "group_id query parameter is required"}), 400

    bills = (
        Bill.query.filter_by(group_id=group_id)
        .order_by(Bill.created_at.desc(), Bill.id.desc())
        .all()
    )
    body = {"group_id": group_id, "bills": [b.to_dict() for b in bills]}
    if not bills:
        body["message"] = "No bills yet. Add one!"
    return jsonify(body), 200


@bills_bp.route("/bills/<int:bill_id>", methods=["GET"])
def get_bill(bill_id):
    bill = db.session.get(Bill, bill_id)
    if not bill:
        return jsonify({"error": "Bill not found"}), 404
    return jsonify({"bill": bill.to_dict()}), 200


# ── US07 / US10: Edit bill or remove a participant ───────────────────────────
@bills_bp.route("/bills/<int:bill_id>", methods=["PUT"])
def update_bill(bill_id):
    """
    Update a bill's amount, details, or participant list.
    Body JSON: same fields as create, plus optional confirm=true to proceed
    after a settled-balance warning.
    """
    bill = db.session.get(Bill, bill_id)
    if not bill:
        return jsonify({"error": "Bill not found"}), 404

    data = request.get_json(silent=True) or {}
    merged = {
        "title":        data.get("title", bill.title),
        "total_amount": data.get("total_amount", bill.total_amount),
        "paid_by":      data.get("paid_by", bill.paid_by),
        "group_id":     data.get("group_id", bill.group_id),
        "category":     data.get("category", bill.category),
        "participants": data.get("participants", [p.user_name for p in bill.participants]),
        "split_type":   data.get("split_type", bill.split_type),
        "ratios":       data.get("ratios"),
        "date":         data.get("date"),
    }
    cleaned, errors = _validate_bill(merged)
    if errors:
        return jsonify({"error": "Validation failed", "errors": errors}), 400

    removed = [p for p in bill.participants if p.user_name not in cleaned["participants"]]
    confirm = bool(data.get("confirm"))

    warnings = []
    if any(p.settled for p in bill.participants):
        warnings.append("Editing may affect settled balances.")
    paid_removed = [
        p.user_name for p in removed
        if p.settled or p.user_name == bill.paid_by
    ]
    if paid_removed:
        warnings.append(
            "Their payment record will be affected: " + ", ".join(paid_removed) + "."
        )

    if warnings and not confirm:
        return jsonify({
            "error": " ".join(warnings),
            "warning": " ".join(warnings),
            "requires_confirm": True,
        }), 409

    bill.title        = cleaned["title"]
    bill.total_amount = cleaned["total_amount"]
    bill.paid_by      = cleaned["paid_by"]
    bill.group_id     = cleaned["group_id"]
    bill.category     = cleaned["category"]
    bill.split_type   = cleaned["split_type"]
    if cleaned["created_at"]:
        bill.created_at = cleaned["created_at"]

    shares = _shares_for(
        cleaned["total_amount"], cleaned["participants"],
        cleaned["split_type"], cleaned["percents"],
    )
    _replace_participants(bill, cleaned["participants"], shares)

    db.session.commit()
    body = {"message": "Bill updated", "bill": bill.to_dict()}
    if warnings:
        body["warning"] = " ".join(warnings)
    return jsonify(body), 200


# ── US09: Delete Erroneous Bill ──────────────────────────────────────────────
@bills_bp.route("/bills/<int:bill_id>", methods=["DELETE"])
def delete_bill(bill_id):
    bill = db.session.get(Bill, bill_id)
    if not bill:
        return jsonify({"error": "Bill not found"}), 404
    db.session.delete(bill)
    db.session.commit()
    return jsonify({"message": "Bill deleted", "id": bill_id}), 200


# ── US05: View Balance Summary ───────────────────────────────────────────────
@bills_bp.route("/balance", methods=["GET"])
def get_balance():
    """
    Return how much each member owes / is owed within a group.
    Query param: ?group_id=<int>
    """
    group_id = request.args.get("group_id", type=int)
    if group_id is None:
        return jsonify({"error": "group_id query parameter is required"}), 400
    return jsonify(_balance_payload(group_id)), 200


# ── US08: Mark Debt as Settled ───────────────────────────────────────────────
@bills_bp.route("/settlements", methods=["POST"])
def mark_settled():
    """
    Mark the outstanding pairwise debt as settled.
    Body JSON: { group_id, from, to }
    """
    data = request.get_json(silent=True) or {}
    group_id = data.get("group_id")
    debtor = (data.get("from") or "").strip()
    creditor = (data.get("to") or "").strip()

    if isinstance(group_id, bool) or not isinstance(group_id, int):
        return jsonify({"error": "group_id must be an integer."}), 400
    if not debtor or not creditor:
        return jsonify({"error": "from and to are required."}), 400

    amount = _outstanding_amount(group_id, debtor, creditor)
    if amount <= 0:
        return jsonify({"error": "No outstanding balance between these members."}), 400

    settlement = Settlement(
        group_id=group_id,
        from_user=debtor,
        to_user=creditor,
        amount=amount,
    )
    db.session.add(settlement)
    db.session.commit()

    payload = _balance_payload(group_id)
    payload["message"] = "Debt marked as settled"
    payload["settlement"] = settlement.to_dict()
    return jsonify(payload), 201


# ── US03: Send Payment Reminder ──────────────────────────────────────────────
@bills_bp.route("/reminders", methods=["POST"])
def send_reminder():
    """
    Send a payment reminder (stored as an in-app notification).
    Body JSON: { group_id, from, to }
    `from` is the creditor; `to` is the person who owes them.
    """
    data = request.get_json(silent=True) or {}
    group_id = data.get("group_id")
    creditor = (data.get("from") or "").strip()
    debtor = (data.get("to") or "").strip()

    if isinstance(group_id, bool) or not isinstance(group_id, int):
        return jsonify({"error": "group_id must be an integer."}), 400
    if not creditor or not debtor:
        return jsonify({"error": "from and to are required."}), 400

    amount = _outstanding_amount(group_id, debtor, creditor)
    if amount <= 0:
        return jsonify({"error": "No unsettled balance to remind about."}), 400

    cutoff = datetime.utcnow() - timedelta(hours=24)
    recent = (
        Reminder.query.filter_by(group_id=group_id, from_user=creditor, to_user=debtor)
        .filter(Reminder.created_at >= cutoff)
        .first()
    )
    if recent:
        return jsonify({
            "error": "A reminder was already sent in the last 24 hours.",
            "cooldown": True,
        }), 429

    details_parts = _unsettled_bill_details(group_id, debtor, creditor)
    details = (
        f"{debtor} owes {creditor} ${amount:.2f}"
        + (": " + "; ".join(details_parts) if details_parts else "")
    )
    reminder = Reminder(
        group_id=group_id,
        from_user=creditor,
        to_user=debtor,
        amount=amount,
        details=details,
    )
    db.session.add(reminder)
    db.session.commit()
    return jsonify({
        "message": f"Reminder sent to {debtor}",
        "notification": reminder.to_dict(),
    }), 201
