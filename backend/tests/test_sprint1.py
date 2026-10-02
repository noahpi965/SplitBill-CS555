"""
Sprint 1 — Test Suite
Covers the four User Stories currently in the Todo column of the Agile board:
  - US01 (#3 ): Add a Shared Bill
  - US04 (#2 ): View Group Bills
  - US05 (#7 ): View Balance Summary
  - US06 (#8 ): View Monthly Report
"""
import json
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


# ── US01: Add a Shared Bill (#3) ─────────────────────────────────────────────

def test_us01_add_shared_bill(client):
    """
    GIVEN a valid bill payload
    WHEN  POST /api/bills is called
    THEN  the response status should be 201 Created
          and the response body should confirm the bill was received.
    """
    payload = {
        "title":        "Team Dinner",
        "total_amount": 120.00,
        "paid_by":      "Alice",
        "group_id":     1,
        "participants": ["Alice", "Bob", "Carol"],
    }
    response = client.post(
        "/api/bills",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 201, (
        f"Expected 201 Created, got {response.status_code}"
    )
    body = response.get_json()
    assert "message" in body, "Response should contain a 'message' key"


# ── US04: View Group Bills (#2) ───────────────────────────────────────────────

def test_us04_view_group_bills(client):
    """
    GIVEN a group with id=1
    WHEN  GET /api/bills?group_id=1 is called
    THEN  the response status should be 200 OK
          and the body should contain a 'bills' list
    """
    response = client.get("/api/bills?group_id=1")

    assert response.status_code == 200, (
        f"Expected 200 OK, got {response.status_code}"
    )
    body = response.get_json()
    assert "bills" in body, "Response should contain a 'bills' key"
    assert isinstance(body["bills"], list), "'bills' should be a list"


# ── US05: View Balance Summary (#7) ──────────────────────────────────────────

def test_us05_view_balance_summary(client):
    """
    GIVEN a group with id=1
    WHEN  GET /api/balance?group_id=1 is called
    THEN  the response status should be 200 OK
          and the body should contain a 'balances' list
    """
    response = client.get("/api/balance?group_id=1")

    assert response.status_code == 200, (
        f"Expected 200 OK, got {response.status_code}"
    )
    body = response.get_json()
    assert "balances" in body, "Response should contain a 'balances' key"
    assert isinstance(body["balances"], list), "'balances' should be a list"


# ── US06: View Monthly Report (#8) ───────────────────────────────────────────

def test_us06_view_monthly_report(client):
    """
    GIVEN a group with id=1, year=2026, month=10
    WHEN  GET /api/reports/monthly?group_id=1&year=2026&month=10 is called
    THEN  the response status should be 200 OK
          and the body should include 'total' and 'items' fields
          with the correct year/month echoed back.
    """
    response = client.get("/api/reports/monthly?group_id=1&year=2026&month=10")

    assert response.status_code == 200, (
        f"Expected 200 OK, got {response.status_code}"
    )
    body = response.get_json()
    assert "total" in body,  "Response should contain 'total'"
    assert "items" in body,  "Response should contain 'items'"
    assert body["year"]  == 2026, "Year should be echoed as 2026"
    assert body["month"] == 10,   "Month should be echoed as 10"
