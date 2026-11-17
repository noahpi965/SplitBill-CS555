"""US15 (#17): update profile and avatar"""
import base64

# placeholder avatar data for testing
PNG = "data:image/png;base64," + base64.b64encode(b"\x89PNG fake").decode()


class TestUS15UpdateProfile:

    def test_update_name_and_avatar(self, client, register):
        # create an account and get its auth headers
        headers, _ = register("Alice")

        # update the display name and avatar
        response = client.put("/api/auth/profile", json={"name": "Alice W.", "avatar": PNG}, headers=headers)

        # check the updated name and avatar are returned
        assert response.status_code == 200
        user = response.get_json()["user"]
        assert user["name"] == "Alice W."
        assert user["avatar"] == PNG

        # fetch the account again to check the avatar was saved
        me = client.get("/api/auth/me", headers=headers).get_json()["user"]
        assert me["avatar"] == PNG

    def test_avatar_appears_with_bills_and_balances(self, client, register, add_bill):
        # create an account with an avatar and add a shared bill
        headers, _ = register("Alice")
        client.put("/api/auth/profile", json={"avatar": PNG}, headers=headers)
        add_bill(paid_by="Alice", participants=["Alice", "Bob"], total_amount=20)

        # get the group's bills and balances
        bills = client.get("/api/bills?group_id=1").get_json()
        balance = client.get("/api/balance?group_id=1").get_json()

        # check both responses include alice's avatar
        assert bills["avatars"] == {"Alice": PNG}
        assert balance["avatars"] == {"Alice": PNG}
