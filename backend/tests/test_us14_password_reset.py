"""US14 (#16): password reset via email"""
from mailer import OUTBOX


def _token_from_outbox():
    # get the reset token from the latest email
    return OUTBOX[-1]["body"].split("token=")[1].split()[0]


class TestUS14PasswordReset:

    def test_registered_email_gets_reset_link_email(self, client, register):
        # create an account first
        register("Alice", "alice@example.com")

        # request a password reset for that email
        response = client.post("/api/auth/forgot-password", json={"email": "alice@example.com"})

        # check the outbox has one email with the right recipient and reset link
        assert response.status_code == 200
        assert len(OUTBOX) == 1
        assert OUTBOX[0]["to"] == "alice@example.com"
        assert "/reset-password?token=" in OUTBOX[0]["body"]

    def test_reset_token_sets_new_password_once(self, client, register):
        # create an account and get its reset token
        register("Alice", "alice@example.com")
        client.post("/api/auth/forgot-password", json={"email": "alice@example.com"})
        token = _token_from_outbox()

        # reset the password then try using the same token again
        first = client.post("/api/auth/reset-password", json={"token": token, "password": "NewSecret456"})
        reuse = client.post("/api/auth/reset-password", json={"token": token, "password": "Another789"})

        # check the reset worked and the token cannot be reused
        assert first.status_code == 200
        assert reuse.status_code == 400

        # check the new password works and the old one is rejected
        assert client.post("/api/auth/login", json={
            "email": "alice@example.com", "password": "NewSecret456"}).status_code == 200
        assert client.post("/api/auth/login", json={
            "email": "alice@example.com", "password": "Secret123"}).status_code == 401
