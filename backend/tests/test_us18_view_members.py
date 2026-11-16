"""US18 (#20): View Group Members and Roles."""
import base64

PNG = "data:image/png;base64," + base64.b64encode(b"img").decode()


class TestUS18ViewMembers:

    def test_lists_names_avatars_and_roles(self, client, register, make_group):
        alice, _ = register("Alice")
        bob, _ = register("Bob")
        client.put("/api/auth/profile", json={"avatar": PNG}, headers=bob)
        group = make_group(alice)
        client.post(f"/api/invites/{group['invite_code']}/join", headers=bob)

        response = client.get(f"/api/groups/{group['id']}/members", headers=alice)

        assert response.status_code == 200
        members = {m["name"]: m for m in response.get_json()["members"]}
        assert members["Alice"]["role"] == "Admin"
        assert members["Bob"]["role"] == "Member"
        assert members["Bob"]["avatar"] == PNG
        assert members["Alice"]["avatar"] is None

    def test_non_member_cannot_view_members(self, client, register, make_group):
        alice, _ = register("Alice")
        eve, _ = register("Eve")
        group = make_group(alice)

        response = client.get(f"/api/groups/{group['id']}/members", headers=eve)

        assert response.status_code == 403
