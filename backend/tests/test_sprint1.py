"""
Sprint 1 — Test Suite
One test class per User Story, each covering the story's two acceptance criteria:
  - US01 (#3 ): Add a Shared Bill
  - US04 (#2 ): View Group Bills
  - US05 (#7 ): View Balance Summary
  - US06 (#8 ): View Monthly Report
"""
import sys
import os

# Allow imports from the backend root when running: pytest tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import create_app, db


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Provide a Flask test client backed by an in-memory SQLite database."""
    app = create_app(testing=True)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def add_bill(client, **overrides):
    payload = {
        "title":        "Team Dinner",
        "total_amount": 90.00,
        "paid_by":      "Alice",
        "group_id":     1,
        "participants": ["Alice", "Bob", "Carol"],
    }
    payload.update(overrides)
    return client.post("/api/bills", json=payload)


# ── US01: Add a Shared Bill (#3) ─────────────────────────────────────────────

class TestUS01AddSharedBill:

    def test_valid_bill_is_saved_and_appears_in_group_list(self, client):
        # Arrange
        payload = {
            "title":        "Team Dinner",
            "total_amount": 100.00,
            "paid_by":      "Alice",
            "group_id":     1,
            "participants": ["Alice", "Bob", "Carol"],
        }

        # Act
        response = client.post("/api/bills", json=payload)
        listed = client.get("/api/bills?group_id=1").get_json()["bills"]

        # Assert
        assert response.status_code == 201
        bill = response.get_json()["bill"]
        assert bill["title"] == "Team Dinner"
        assert bill["paid_by"] == "Alice"
        shares = [p["share"] for p in bill["participants"]]
        assert shares == [33.34, 33.33, 33.33]
        assert sum(shares) == pytest.approx(100.00)
        assert [b["id"] for b in listed] == [bill["id"]]

    def test_empty_amount_returns_validation_error_and_is_not_saved(self, client):
        # Arrange / Act
        response = add_bill(client, total_amount="")

        # Assert
        assert response.status_code == 400
        assert "total_amount" in response.get_json()["errors"]
        assert client.get("/api/bills?group_id=1").get_json()["bills"] == []


# ── US04: View Group Bills (#2) ──────────────────────────────────────────────

class TestUS04ViewGroupBills:

    def test_lists_group_bills_with_date_amount_payer_and_participants(self, client):
        # Arrange
        add_bill(client, title="Groceries", total_amount=40, paid_by="Bob",
                 participants=["Alice", "Bob"], date="2026-10-01")
        add_bill(client, title="Taxi", total_amount=30, paid_by="Carol",
                 participants=["Bob", "Carol"], date="2026-10-03")
        add_bill(client, title="Other group", group_id=2)

        # Act
        response = client.get("/api/bills?group_id=1")

        # Assert
        assert response.status_code == 200
        bills = response.get_json()["bills"]
        assert [b["title"] for b in bills] == ["Taxi", "Groceries"]
        taxi = bills[0]
        assert taxi["created_at"].startswith("2026-10-03")
        assert taxi["total_amount"] == 30
        assert taxi["paid_by"] == "Carol"
        assert [p["user_name"] for p in taxi["participants"]] == ["Bob", "Carol"]

    def test_empty_group_shows_friendly_message(self, client):
        # Act
        response = client.get("/api/bills?group_id=99")

        # Assert
        assert response.status_code == 200
        body = response.get_json()
        assert body["bills"] == []
        assert body["message"] == "No bills yet. Add one!"


# ── US05: View Balance Summary (#7) ──────────────────────────────────────────

class TestUS05ViewBalanceSummary:

    def test_shows_each_debt_direction_and_exact_amount(self, client):
        # Arrange: Alice pays 90 for 3 people, Bob pays 30 for Bob & Carol
        add_bill(client, total_amount=90, paid_by="Alice",
                 participants=["Alice", "Bob", "Carol"])
        add_bill(client, total_amount=30, paid_by="Bob",
                 participants=["Bob", "Carol"])

        # Act
        response = client.get("/api/balance?group_id=1")

        # Assert: Bob net -15, Carol net -45, Alice net +60
        assert response.status_code == 200
        body = response.get_json()
        assert body["all_settled"] is False
        assert body["net"] == {"Alice": 60.0, "Bob": -15.0, "Carol": -45.0}
        assert body["balances"] == [
            {"from": "Carol", "to": "Alice", "amount": 45.0},
            {"from": "Bob",   "to": "Alice", "amount": 15.0},
        ]

    def test_all_settled_when_no_outstanding_debts(self, client):
        # Arrange: a bill only the payer took part in leaves nobody owing anything
        add_bill(client, total_amount=20, paid_by="Alice", participants=["Alice"])

        # Act
        response = client.get("/api/balance?group_id=1")

        # Assert
        body = response.get_json()
        assert response.status_code == 200
        assert body["balances"] == []
        assert body["all_settled"] is True
        assert body["message"] == "All settled up"


# ── US06: View Monthly Report (#8) ───────────────────────────────────────────

class TestUS06ViewMonthlyReport:

    def test_report_shows_total_bill_count_and_category_breakdown(self, client):
        # Arrange
        add_bill(client, title="Dinner", total_amount=60, category="Food", date="2026-10-02")
        add_bill(client, title="Lunch",  total_amount=25.5, category="Food", date="2026-10-20")
        add_bill(client, title="Uber",   total_amount=18, category="Transport", date="2026-10-31")
        add_bill(client, title="Sept rent", total_amount=900, category="Rent", date="2026-09-30")

        # Act
        response = client.get("/api/reports/monthly?group_id=1&year=2026&month=10")

        # Assert
        assert response.status_code == 200
        body = response.get_json()
        assert body["total"] == pytest.approx(103.5)
        assert body["bill_count"] == 3
        assert body["categories"] == [
            {"category": "Food",      "amount": 85.5},
            {"category": "Transport", "amount": 18.0},
        ]
        assert [i["title"] for i in body["items"]] == ["Dinner", "Lunch", "Uber"]

    def test_month_without_activity_shows_no_expenses_message(self, client):
        # Arrange
        add_bill(client, date="2026-10-05")

        # Act
        response = client.get("/api/reports/monthly?group_id=1&year=2026&month=11")

        # Assert
        assert response.status_code == 200
        body = response.get_json()
        assert body["total"] == 0
        assert body["bill_count"] == 0
        assert body["categories"] == []
        assert body["message"] == "No expenses recorded for this period"
