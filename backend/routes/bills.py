from collections import defaultdict
from datetime import datetime

from flask import Blueprint, jsonify, request
from extensions import db
from models import Bill, BillParticipant

bills_bp = Blueprint("bills", __name__)


def _split_equally(total_amount, participants):
    """Split an amount into equal shares, spreading leftover cents so shares sum to the total."""
    total_cents = round(total_amount * 100)
    base, remainder = divmod(total_cents, len(participants))
    return [(base + (1 if i < remainder else 0)) / 100 for i in range(len(participants))]


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

    participants = data.get("participants")
    if not isinstance(participants, list) or not participants:
        errors["participants"] = "At least one participant is required."
    else:
        participants = [p.strip() for p in participants if isinstance(p, str) and p.strip()]
        if not participants:
            errors["participants"] = "At least one participant is required."
        elif len(set(participants)) != len(participants):
            errors["participants"] = "Participants must be unique."

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
        "created_at":   created_at,
    }, None


# ── US01: Add a Shared Bill ──────────────────────────────────────────────────
@bills_bp.route("/bills", methods=["POST"])
def add_bill():
    """
    Create a new shared bill and split it equally among participants.
    Body JSON: { title, total_amount, paid_by, group_id, participants: [name, ...],
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
    )
    if cleaned["created_at"]:
        bill.created_at = cleaned["created_at"]

    shares = _split_equally(cleaned["total_amount"], cleaned["participants"])
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

    net_cents = defaultdict(int)
    for bill in Bill.query.filter_by(group_id=group_id).all():
        for p in bill.participants:
            if p.settled or p.user_name == bill.paid_by:
                continue
            cents = round(p.share * 100)
            net_cents[bill.paid_by] += cents
            net_cents[p.user_name] -= cents

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

    members = {name: cents / 100 for name, cents in sorted(net_cents.items()) if cents != 0}
    body = {
        "group_id":    group_id,
        "balances":    balances,
        "net":         members,
        "all_settled": not balances,
    }
    if not balances:
        body["message"] = "All settled up"
    return jsonify(body), 200
