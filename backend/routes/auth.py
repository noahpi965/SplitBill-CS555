import re
import secrets
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from mailer import send_email
from models import PasswordReset, User

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")


MAX_AVATAR_CHARS = 700_000  # roughly 500 KB of image data
RESET_TTL = timedelta(hours=1)


def _new_token():
    return secrets.token_urlsafe(32)


def current_user():
    """Return the User identified by the Authorization header, or None."""
    header = request.headers.get("Authorization", "")
    token = header.split(" ", 1)[-1].strip() if header else ""
    return User.query.filter_by(token=token).first() if token else None


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
    user = current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"user": user.to_dict()}), 200


# ── US14: Password Reset via Email ───────────────────────────────────────────
@auth_bp.route("/auth/forgot-password", methods=["POST"])
def forgot_password():
    """
    Email a reset link to a registered address.
    Body JSON: { email }
    The response is identical whether or not the account exists, so the
    endpoint cannot be used to discover registered emails.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Please enter a valid email address."}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        reset = PasswordReset(
            user_id=user.id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + RESET_TTL,
        )
        db.session.add(reset)
        db.session.commit()
        link = f"{request.host_url.rstrip('/')}/reset-password?token={reset.token}"
        send_email(
            user.email,
            "Reset your SplitBill password",
            f"Hi {user.name},\n\nUse this link to choose a new password "
            f"(valid for 1 hour):\n{link}\n\n"
            "If you did not request this, you can ignore this email.",
        )
    return jsonify({
        "message": "If that email is registered, a reset link is on its way.",
    }), 200


@auth_bp.route("/auth/reset-password", methods=["POST"])
def reset_password():
    """Body JSON: { token, password }"""
    data = request.get_json(silent=True) or {}
    token = data.get("token") or ""
    password = data.get("password") or ""

    if not PASSWORD_RE.match(password):
        return jsonify({
            "error": "Password must be at least 8 characters and include a letter and a number.",
        }), 400

    reset = PasswordReset.query.filter_by(token=token).first() if token else None
    if not reset or reset.used or reset.expires_at < datetime.utcnow():
        return jsonify({"error": "This reset link is invalid or has expired."}), 400

    user = db.session.get(User, reset.user_id)
    user.password_hash = generate_password_hash(password)
    user.token = None  # sign out existing sessions
    reset.used = True
    db.session.commit()
    return jsonify({"message": "Password updated. You can now log in."}), 200


# ── US15: Update Profile & Avatar ────────────────────────────────────────────
@auth_bp.route("/auth/profile", methods=["PUT"])
def update_profile():
    """
    Update display name and/or avatar.
    Body JSON: { name?, avatar? }  (avatar is a data:image/... URL, or null/"" to remove)
    """
    user = current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = data["name"]
        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "Display name cannot be empty."}), 400
        if len(name.strip()) > 80:
            return jsonify({"error": "Display name must be 80 characters or fewer."}), 400
        user.name = name.strip()

    if "avatar" in data:
        avatar = data["avatar"]
        if avatar in (None, ""):
            user.avatar = None
        elif (not isinstance(avatar, str)
              or not avatar.startswith("data:image/")
              or ";base64," not in avatar[:60]):
            return jsonify({"error": "Avatar must be an image."}), 400
        elif len(avatar) > MAX_AVATAR_CHARS:
            return jsonify({"error": "Avatar image is too large (max 500 KB)."}), 413
        else:
            user.avatar = avatar

    db.session.commit()
    return jsonify({"message": "Profile updated", "user": user.to_dict()}), 200
