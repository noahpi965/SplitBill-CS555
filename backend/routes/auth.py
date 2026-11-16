import re
import secrets

from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")


def _new_token():
    return secrets.token_urlsafe(32)


# ── US11: User Account Registration ──────────────────────────────────────────
@auth_bp.route("/auth/register", methods=["POST"])
def register():
    """
    Create an account with email + strong password.
    Body JSON: { email, password, name? }
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or email.split("@")[0]).strip() or "User"

    if not EMAIL_RE.match(email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if not PASSWORD_RE.match(password):
        return jsonify({
            "error": "Password must be at least 8 characters and include a letter and a number.",
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 409

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        name=name,
        token=_new_token(),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "message": "Account created",
        "user": user.to_dict(),
        "token": user.token,
    }), 201


# ── US12: User Login ─────────────────────────────────────────────────────────
@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """
    Authenticate with email + password.
    Body JSON: { email, password }
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    user.token = _new_token()
    db.session.commit()
    return jsonify({
        "message": "Logged in",
        "user": user.to_dict(),
        "token": user.token,
    }), 200


@auth_bp.route("/auth/me", methods=["GET"])
def me():
    header = request.headers.get("Authorization", "")
    token = header.split(" ", 1)[-1].strip() if header else ""
    user = User.query.filter_by(token=token).first() if token else None
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"user": user.to_dict()}), 200
