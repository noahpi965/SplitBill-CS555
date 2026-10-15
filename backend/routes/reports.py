from flask import Blueprint, jsonify, request

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

    # TODO: aggregate real data in Sprint 1
    return jsonify({
        "group_id": group_id,
        "year":     year,
        "month":    month,
        "total":    0.0,
        "items":    [],
    }), 200
