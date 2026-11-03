"""US12 (#14): user login"""


class TestUS12UserLogin:

    def test_valid_credentials_authenticate_and_return_token(self, client):
        # create an account to log into
        client.post("/api/auth/register", json={
            "email": "bob@example.com",
            "password": "Secret123",
            "name": "Bob",
        })

        # log in with the correct email and password
        response = client.post("/api/auth/login", json={
            "email": "bob@example.com",
            "password": "Secret123",
        })

        # check login worked and returned user info and a token
        assert response.status_code == 200
        body = response.get_json()
        assert body["user"]["email"] == "bob@example.com"
        assert body["user"]["name"] == "Bob"
        assert body["token"]

        # check the token gives access to the correct account
        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['token']}"})
        assert me.status_code == 200
        assert me.get_json()["user"]["email"] == "bob@example.com"

    def test_incorrect_credentials_return_invalid_prompt(self, client):
        # create the account first
        client.post("/api/auth/register", json={
            "email": "bob@example.com",
            "password": "Secret123",
        })

        # try logging in with the wrong password
        response = client.post("/api/auth/login", json={
            "email": "bob@example.com",
            "password": "wrong-pass",
        })

        # check login was rejected with the right error
        assert response.status_code == 401
        assert response.get_json()["error"] == "Invalid email or password"
