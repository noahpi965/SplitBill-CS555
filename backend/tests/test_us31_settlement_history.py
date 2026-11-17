"""US31 (#33): View Settlement Transaction History"""
from datetime import datetime, timedelta

from extensions import db
from models import Settlement


def _seed(client, add_bill):
    add_bill(title="Dinner", total_amount=30, paid_by="Alice", participants=["Alice", "Bob", "Carol"])
    client.post("/api/settlements", json={"group_id": 1, "from": "Bob", "to": "Alice"})
    client.post("/api/settlements", json={"group_id": 1, "from": "Carol", "to": "Alice"})
    # Make timestamps deterministic: Bob's payment was earlier.
    rows = Settlement.query.order_by(Settlement.id).all()
    base = datetime(2026, 1, 1, 12, 0)
    rows[0].created_at = base
    rows[1].created_at = base + timedelta(days=1)
    db.session.commit()


class TestUS31SettlementHistory:

    def test_lists_completed_payments_chronologically_with_timestamps(self, client, add_bill):
        _seed(client, add_bill)

        response = client.get("/api/settlements?group_id=1")

        assert response.status_code == 200
        body = response.get_json()
        assert [(s["from"], s["to"]) for s in body["settlements"]] == [("Bob", "Alice"), ("Carol", "Alice")]
        assert body["settlements"][0]["settled_at"] == "2026-01-01T12:00:00"
        assert body["total_amount"] == 20.0

    def test_empty_history_returns_message(self, client):
        body = client.get("/api/settlements?group_id=1").get_json()

        assert body["settlements"] == []
        assert body["message"] == "No payments have been settled yet."
