"""US12 (#14): User Login."""


class TestUS12UserLogin:

    def test_valid_credentials_authenticate_and_return_token(self, client):
        # Arrange
        client.post("/api/auth/register", json={
            "email": "bob@example.com",
            "password": "Secret123",
            "name": "Bob",
        })

        # Act
        response = client.post("/api/auth/login", json={
            "email": "bob@example.com",
            "password": "Secret123",
        })

        # Assert
        assert response.status_code == 200
        body = response.get_json()
        assert body["user"]["email"] == "bob@example.com"
        assert body["user"]["name"] == "Bob"
        assert body["token"]
        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['token']}"})
        assert me.status_code == 200
        assert me.get_json()["user"]["email"] == "bob@example.com"

    def test_incorrect_credentials_return_invalid_prompt(self, client):
        # Arrange
        client.post("/api/auth/register", json={
            "email": "bob@example.com",
            "password": "Secret123",
        })

        # Act
        response = client.post("/api/auth/login", json={
            "email": "bob@example.com",
            "password": "wrong-pass",
        })

        # Assert
        assert response.status_code == 401
        assert response.get_json()["error"] == "Invalid email or password"
