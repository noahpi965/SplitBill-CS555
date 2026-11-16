import secrets

from flask import Blueprint, jsonify, request

from extensions import db
from models import Group, GroupMember
from routes.auth import current_user

groups_bp = Blueprint("groups", __name__)

GROUP_TYPES = ("Trip", "Home", "Couple", "Event", "Other")


def _membership(group_id, user):
    return GroupMember.query.filter_by(group_id=group_id, user_id=user.id).first()


def _member_balance_cents(group_id, name):
    """Net balance (cents) for a member name, using bills + settlements."""
    from routes.bills import _apply_settlements, _bill_net_cents
    return _apply_settlements(group_id, _bill_net_cents(group_id)).get(name, 0)


def _auth_group(group_id, require_admin=False):
    """Return (user, group, membership, error_response)."""
    user = current_user()
    if not user:
        return None, None, None, (jsonify({"error": "Not authenticated"}), 401)
    group = db.session.get(Group, group_id)
    if not group:
        return user, None, None, (jsonify({"error": "Group not found"}), 404)
    member = _membership(group_id, user)
    if not member:
        return user, group, None, (jsonify({"error": "You are not a member of this group."}), 403)
    if require_admin and member.role != "Admin":
        return user, group, member, (jsonify({"error": "Only group admins can do this."}), 403)
    return user, group, member, None


# ── US16: Create Expense Group ───────────────────────────────────────────────
@groups_bp.route("/groups", methods=["POST"])
def create_group():
    """Body JSON: { name, group_type }. The creator becomes the group's Admin."""
    user = current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    group_type = data.get("group_type") or "Other"

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Group name is required."}), 400
    if len(name.strip()) > 80:
        return jsonify({"error": "Group name must be 80 characters or fewer."}), 400
    if group_type not in GROUP_TYPES:
        return jsonify({"error": f"group_type must be one of: {', '.join(GROUP_TYPES)}."}), 400

    group = Group(
        name=name.strip(),
        group_type=group_type,
        invite_code=secrets.token_urlsafe(8),
    )
    group.members.append(GroupMember(user_id=user.id, role="Admin"))
    db.session.add(group)
    db.session.commit()
    return jsonify({"message": "Group created", "group": group.to_dict()}), 201


@groups_bp.route("/groups", methods=["GET"])
def list_groups():
    user = current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    memberships = GroupMember.query.filter_by(user_id=user.id).all()
    groups = []
    for m in memberships:
        d = m.group.to_dict()
        d["role"] = m.role
        groups.append(d)
    return jsonify({"groups": groups}), 200


@groups_bp.route("/groups/<int:group_id>", methods=["GET"])
def get_group(group_id):
    _, group, member, err = _auth_group(group_id)
    if err:
        return err
    body = group.to_dict()
    body["role"] = member.role
    return jsonify({"group": body}), 200


# ── US18: View Group Members and Roles ───────────────────────────────────────
@groups_bp.route("/groups/<int:group_id>/members", methods=["GET"])
def list_members(group_id):
    _, group, _, err = _auth_group(group_id)
    if err:
        return err
    return jsonify({
        "group_id": group.id,
        "members": [m.to_dict() for m in group.members],
    }), 200


# ── US19: Remove Member from Group ───────────────────────────────────────────
@groups_bp.route("/groups/<int:group_id>/members/<int:member_id>", methods=["DELETE"])
def remove_member(group_id, member_id):
    _, group, _, err = _auth_group(group_id, require_admin=True)
    if err:
        return err

    target = db.session.get(GroupMember, member_id)
    if not target or target.group_id != group.id:
        return jsonify({"error": "Member not found in this group."}), 404

    if target.role == "Admin" and sum(1 for m in group.members if m.role == "Admin") == 1:
        return jsonify({"error": "The only admin cannot be removed."}), 400

    balance = _member_balance_cents(group.id, target.user.name)
    if balance != 0:
        return jsonify({
            "error": f"{target.user.name} still has unsettled balances. "
                     "Settle all debts before removing this member.",
            "balance": balance / 100,
        }), 409

    db.session.delete(target)
    db.session.commit()
    return jsonify({"message": f"{target.user.name} removed", "id": member_id}), 200


# ── US17: Join Group via Invite Link or QR Code ──────────────────────────────
@groups_bp.route("/invites/<code>", methods=["GET"])
def preview_invite(code):
    """Public preview of the group behind an invite code."""
    group = Group.query.filter_by(invite_code=code).first()
    if not group:
        return jsonify({"error": "This invite link is invalid."}), 404
    return jsonify({"group": {
        "id": group.id,
        "name": group.name,
        "group_type": group.group_type,
        "member_count": len(group.members),
    }}), 200


@groups_bp.route("/invites/<code>/join", methods=["POST"])
def join_group(code):
    user = current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    group = Group.query.filter_by(invite_code=code).first()
    if not group:
        return jsonify({"error": "This invite link is invalid."}), 404

    existing = _membership(group.id, user)
    if existing:
        return jsonify({
            "message": "You are already a member of this group.",
            "already_member": True,
            "group": group.to_dict(),
        }), 200

    group.members.append(GroupMember(user_id=user.id, role="Member"))
    db.session.commit()
    return jsonify({"message": f"Joined {group.name}", "group": group.to_dict()}), 201
