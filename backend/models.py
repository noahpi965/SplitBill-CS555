from datetime import datetime

from extensions import db


class User(db.Model):
    """Registered SplitBill account (US11 / US12)."""
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name          = db.Column(db.String(80), nullable=False)
    token         = db.Column(db.String(64), unique=True, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":    self.id,
            "email": self.email,
            "name":  self.name,
        }


class Bill(db.Model):
    """Represents a shared bill within a group."""
    __tablename__ = "bills"

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(120), nullable=False)
    total_amount = db.Column(db.Float,   nullable=False)
    paid_by      = db.Column(db.String(80), nullable=False)
    group_id     = db.Column(db.Integer, nullable=False)
    category     = db.Column(db.String(40), nullable=False, default="General")
    split_type   = db.Column(db.String(20), nullable=False, default="equal")
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    participants = db.relationship(
        "BillParticipant",
        backref="bill",
        cascade="all, delete-orphan",
        order_by="BillParticipant.id",
    )

    def to_dict(self):
        return {
            "id":           self.id,
            "title":        self.title,
            "total_amount": self.total_amount,
            "paid_by":      self.paid_by,
            "group_id":     self.group_id,
            "category":     self.category,
            "split_type":   self.split_type,
            "created_at":   self.created_at.isoformat(),
            "participants": [p.to_dict() for p in self.participants],
            "has_settled_participant": any(p.settled for p in self.participants),
        }


class BillParticipant(db.Model):
    """Stores each participant's share of a bill."""
    __tablename__ = "bill_participants"

    id        = db.Column(db.Integer, primary_key=True)
    bill_id   = db.Column(db.Integer, db.ForeignKey("bills.id"), nullable=False)
    user_name = db.Column(db.String(80), nullable=False)
    share     = db.Column(db.Float, nullable=False)
    settled   = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "user_name": self.user_name,
            "share":     self.share,
            "settled":   self.settled,
        }


class Settlement(db.Model):
    """Records a pairwise debt that was marked settled (US08)."""
    __tablename__ = "settlements"

    id         = db.Column(db.Integer, primary_key=True)
    group_id   = db.Column(db.Integer, nullable=False)
    from_user  = db.Column(db.String(80), nullable=False)
    to_user    = db.Column(db.String(80), nullable=False)
    amount     = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "group_id":   self.group_id,
            "from":       self.from_user,
            "to":         self.to_user,
            "amount":     self.amount,
            "settled_at": self.created_at.isoformat(),
        }


class Reminder(db.Model):
    """Simulated payment-reminder notification (US03)."""
    __tablename__ = "reminders"

    id          = db.Column(db.Integer, primary_key=True)
    group_id    = db.Column(db.Integer, nullable=False)
    from_user   = db.Column(db.String(80), nullable=False)
    to_user     = db.Column(db.String(80), nullable=False)
    amount      = db.Column(db.Float, nullable=False)
    details     = db.Column(db.Text, nullable=False, default="")
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":        self.id,
            "group_id":  self.group_id,
            "from":      self.from_user,
            "to":        self.to_user,
            "amount":    self.amount,
            "details":   self.details,
            "sent_at":   self.created_at.isoformat(),
        }
