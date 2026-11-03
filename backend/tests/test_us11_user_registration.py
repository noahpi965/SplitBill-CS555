"""US11 (#13): user account registration"""
from models import User


class TestUS11UserAccountRegistration:

    def test_valid_registration_creates_account(self, client):
        # set up valid account info
        payload = {
            "email":    "alice@example.com",
            "password": "Secret123",
            "name":     "Alice",
        }

        # send registration request
        response = client.post("/api/auth/register", json=payload)

        # check account info, token, and saved user
        assert response.status_code == 201
        body = response.get_json()
        assert body["user"]["email"] == "alice@example.com"
        assert body["user"]["name"] == "Alice"
        assert body["token"]
        assert User.query.filter_by(email="alice@example.com").count() == 1

    def test_duplicate_email_returns_user_already_exists(self, client):
        # create the account first
        client.post("/api/auth/register", json={
            "email": "alice@example.com",
            "password": "Secret123",
        })

        # try the same email with different capitalization
        response = client.post("/api/auth/register", json={
            "email": "Alice@example.com",
            "password": "OtherPass1",
        })

        # check error and make sure no extra account was created
        assert response.status_code == 409
        assert response.get_json()["error"] == "User already exists"
        assert User.query.count() == 1
