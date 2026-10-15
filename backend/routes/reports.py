from collections import defaultdict
from datetime import datetime

from flask import Blueprint, jsonify, request
from models import Bill

reports_bp = Blueprint("reports", __name__)


# ── US06: View Monthly Report ────────────────────────────────────────────────
@reports_bp.route("/reports/monthly", methods=["GET"])
def monthly_report():
    """
    Return spending summary for a given month.
    Query params: ?group_id=<int>&year=<int>&month=<int>
    """
    group_id = request.args.get("group_id", type=int)
    year     = request.args.get("year",     type=int)
    month    = request.args.get("month",    type=int)

    if group_id is None or year is None or month is None:
        return jsonify({"error": "group_id, year and month query parameters are required"}), 400
    if not 1 <= month <= 12:
        return jsonify({"error": "month must be between 1 and 12"}), 400
    if not 1 <= year <= 9998:
        return jsonify({"error": "year is out of range"}), 400

    start = datetime(year, month, 1)
    end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

    bills = (
        Bill.query.filter(
            Bill.group_id == group_id,
            Bill.created_at >= start,
            Bill.created_at < end,
        )
        .order_by(Bill.created_at, Bill.id)
        .all()
    )

    category_cents = defaultdict(int)
    for b in bills:
        category_cents[b.category] += round(b.total_amount * 100)
    total_cents = sum(category_cents.values())

    body = {
        "group_id":   group_id,
        "year":       year,
        "month":      month,
        "total":      total_cents / 100,
        "bill_count": len(bills),
        "categories": [
            {"category": c, "amount": cents / 100}
            for c, cents in sorted(category_cents.items(), key=lambda x: (-x[1], x[0]))
        ],
        "items": [
            {
                "id":       b.id,
                "title":    b.title,
                "amount":   b.total_amount,
                "category": b.category,
                "paid_by":  b.paid_by,
                "date":     b.created_at.date().isoformat(),
            }
            for b in bills
        ],
    }
    if not bills:
        body["message"] = "No expenses recorded for this period"
    return jsonify(body), 200
