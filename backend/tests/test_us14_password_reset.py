"""US14 (#16): Password Reset via Email."""
from mailer import OUTBOX


def _token_from_outbox():
    return OUTBOX[-1]["body"].split("token=")[1].split()[0]


class TestUS14PasswordReset:

    def test_registered_email_gets_reset_link_email(self, client, register):
        # Arrange
        register("Alice", "alice@example.com")

        # Act
        response = client.post("/api/auth/forgot-password", json={"email": "alice@example.com"})

        # Assert
        assert response.status_code == 200
        assert len(OUTBOX) == 1
        assert OUTBOX[0]["to"] == "alice@example.com"
        assert "/reset-password?token=" in OUTBOX[0]["body"]

    def test_reset_token_sets_new_password_once(self, client, register):
        # Arrange
        register("Alice", "alice@example.com")
        client.post("/api/auth/forgot-password", json={"email": "alice@example.com"})
        token = _token_from_outbox()

        # Act
        first = client.post("/api/auth/reset-password", json={"token": token, "password": "NewSecret456"})
        reuse = client.post("/api/auth/reset-password", json={"token": token, "password": "Another789"})

        # Assert
        assert first.status_code == 200
        assert reuse.status_code == 400
        assert client.post("/api/auth/login", json={
            "email": "alice@example.com", "password": "NewSecret456"}).status_code == 200
        assert client.post("/api/auth/login", json={
            "email": "alice@example.com", "password": "Secret123"}).status_code == 401
