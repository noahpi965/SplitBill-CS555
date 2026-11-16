import os
import sys

# Allow imports from the backend root when running: pytest tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import create_app
from extensions import db


@pytest.fixture
def client():
    """Provide a Flask test client backed by an in-memory SQLite database."""
    app = create_app(testing=True)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def add_bill(client):
    """POST a bill to /api/bills; keyword arguments override the default payload."""
    def _add_bill(**overrides):
        payload = {
            "title":        "Team Dinner",
            "total_amount": 90.00,
            "paid_by":      "Alice",
            "group_id":     1,
            "participants": ["Alice", "Bob", "Carol"],
        }
        payload.update(overrides)
        return client.post("/api/bills", json=payload)
    return _add_bill


@pytest.fixture
def register(client):
    """Register a user; returns (headers, user_dict)."""
    def _register(name="Alice", email=None, password="Secret123"):
        email = email or f"{name.lower()}@example.com"
        r = client.post("/api/auth/register", json={
            "email": email, "password": password, "name": name,
        })
        body = r.get_json()
        return {"Authorization": f"Bearer {body['token']}"}, body["user"]
    return _register


@pytest.fixture(autouse=True)
def clear_outbox():
    from mailer import OUTBOX
    OUTBOX.clear()
    yield
    OUTBOX.clear()
