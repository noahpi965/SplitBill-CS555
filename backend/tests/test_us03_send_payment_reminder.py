"""US03 (#5): Send Payment Reminder."""
from datetime import datetime, timedelta

from extensions import db
from models import Reminder


class TestUS03SendPaymentReminder:

    def test_reminder_is_sent_when_unsettled_balance_exists(self, client, add_bill):
        # Arrange
        add_bill(total_amount=40, paid_by="Alice", participants=["Alice", "Bob"])

        # Act
        response = client.post("/api/reminders", json={
            "group_id": 1,
            "from": "Alice",
            "to": "Bob",
        })

        # Assert
        assert response.status_code == 201
        body = response.get_json()
        assert body["message"] == "Reminder sent to Bob"
        note = body["notification"]
        assert note["to"] == "Bob"
        assert note["from"] == "Alice"
        assert note["amount"] == 20.0
        assert "20.00" in note["details"]
        assert "Team Dinner" in note["details"]

    def test_duplicate_reminder_within_24_hours_is_blocked(self, client, add_bill):
        # Arrange
        add_bill(total_amount=40, paid_by="Alice", participants=["Alice", "Bob"])
        db.session.add(Reminder(
            group_id=1,
            from_user="Alice",
            to_user="Bob",
            amount=20.0,
            details="already sent",
            created_at=datetime.utcnow() - timedelta(hours=2),
        ))
        db.session.commit()

        # Act
        response = client.post("/api/reminders", json={
            "group_id": 1,
            "from": "Alice",
            "to": "Bob",
        })

        # Assert
        assert response.status_code == 429
        body = response.get_json()
        assert body["cooldown"] is True
        assert "24 hours" in body["error"]
        assert Reminder.query.count() == 1
