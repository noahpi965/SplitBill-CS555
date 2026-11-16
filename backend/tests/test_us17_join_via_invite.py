"""US17 (#19): Join Group via Invite Link or QR Code."""


class TestUS17JoinViaInvite:

    def test_valid_invite_adds_member_immediately(self, client, register, make_group):
        alice, _ = register("Alice")
        bob, _ = register("Bob")
        group = make_group(alice)

        response = client.post(f"/api/invites/{group['invite_code']}/join", headers=bob)

        assert response.status_code == 201
        members = client.get(f"/api/groups/{group['id']}/members", headers=bob).get_json()["members"]
        assert sorted((m["name"], m["role"]) for m in members) == [("Alice", "Admin"), ("Bob", "Member")]

    def test_invalid_code_is_rejected(self, client, register):
        bob, _ = register("Bob")

        assert client.get("/api/invites/bogus").status_code == 404
        assert client.post("/api/invites/bogus/join", headers=bob).status_code == 404
