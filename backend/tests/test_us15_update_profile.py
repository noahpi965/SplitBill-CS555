"""US15 (#17): Update Profile & Avatar."""
import base64

PNG = "data:image/png;base64," + base64.b64encode(b"\x89PNG fake").decode()


class TestUS15UpdateProfile:

    def test_update_name_and_avatar(self, client, register):
        headers, _ = register("Alice")

        response = client.put("/api/auth/profile", json={"name": "Alice W.", "avatar": PNG}, headers=headers)

        assert response.status_code == 200
        user = response.get_json()["user"]
        assert user["name"] == "Alice W."
        assert user["avatar"] == PNG
        me = client.get("/api/auth/me", headers=headers).get_json()["user"]
        assert me["avatar"] == PNG

    def test_avatar_appears_with_bills_and_balances(self, client, register, add_bill):
        headers, _ = register("Alice")
        client.put("/api/auth/profile", json={"avatar": PNG}, headers=headers)
        add_bill(paid_by="Alice", participants=["Alice", "Bob"], total_amount=20)

        bills = client.get("/api/bills?group_id=1").get_json()
        balance = client.get("/api/balance?group_id=1").get_json()

        assert bills["avatars"] == {"Alice": PNG}
        assert balance["avatars"] == {"Alice": PNG}
