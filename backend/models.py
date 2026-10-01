from app import db
from datetime import datetime


class Bill(db.Model):
    """Represents a shared bill within a group."""
    __tablename__ = "bills"

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(120), nullable=False)
    total_amount= db.Column(db.Float,   nullable=False)
    paid_by     = db.Column(db.String(80), nullable=False)   # user who paid
    group_id    = db.Column(db.Integer, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":           self.id,
            "title":        self.title,
            "total_amount": self.total_amount,
            "paid_by":      self.paid_by,
            "group_id":     self.group_id,
            "created_at":   self.created_at.isoformat(),
        }


class BillParticipant(db.Model):
    """Stores each participant's share of a bill."""
    __tablename__ = "bill_participants"

    id         = db.Column(db.Integer, primary_key=True)
    bill_id    = db.Column(db.Integer, db.ForeignKey("bills.id"), nullable=False)
    user_name  = db.Column(db.String(80), nullable=False)
    share      = db.Column(db.Float, nullable=False)   # amount owed by this participant
    settled    = db.Column(db.Boolean, default=False)
