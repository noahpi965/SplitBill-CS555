from flask import Blueprint, jsonify, request
from app import db
from models import Bill, BillParticipant

bills_bp = Blueprint("bills", __name__)


# ── US01: Add a Shared Bill ──────────────────────────────────────────────────
@bills_bp.route("/bills", methods=["POST"])
def add_bill():
    """
    Create a new shared bill.
    Body JSON: { title, total_amount, paid_by, group_id, participants: [name, ...] }
    """
    data = request.get_json(silent=True) or {}

    # TODO: validate & persist in Sprint 1
    return jsonify({"message": "Bill created (stub)", "data": data}), 201


# ── US04: View Group Bills ───────────────────────────────────────────────────
@bills_bp.route("/bills", methods=["GET"])
def get_bills():
    """
    Return all bills for a group.
    Query param: ?group_id=<int>
    """
    group_id = request.args.get("group_id", type=int)

    # TODO: filter by group_id and return real records in Sprint 1
    return jsonify({"bills": [], "group_id": group_id}), 200


# ── US05: View Balance Summary ───────────────────────────────────────────────
@bills_bp.route("/balance", methods=["GET"])
def get_balance():
    """
    Return how much each member owes / is owed within a group.
    Query param: ?group_id=<int>
    """
    group_id = request.args.get("group_id", type=int)

    # TODO: compute real balances in Sprint 1
    return jsonify({"group_id": group_id, "balances": []}), 200
