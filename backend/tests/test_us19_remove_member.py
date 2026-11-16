"""US19 (#21): Remove Member from Group."""


def _group_with_bob(client, register, make_group):
    alice, _ = register("Alice")
    bob, _ = register("Bob")
    group = make_group(alice)
    client.post(f"/api/invites/{group['invite_code']}/join", headers=bob)
    members = client.get(f"/api/groups/{group['id']}/members", headers=alice).get_json()["members"]
    bob_member_id = next(m["id"] for m in members if m["name"] == "Bob")
    return alice, bob, group, bob_member_id


class TestUS19RemoveMember:

    def test_member_with_zero_balance_is_removed(self, client, register, make_group):
        alice, _, group, bob_id = _group_with_bob(client, register, make_group)

        response = client.delete(f"/api/groups/{group['id']}/members/{bob_id}", headers=alice)

        assert response.status_code == 200
        members = client.get(f"/api/groups/{group['id']}/members", headers=alice).get_json()["members"]
        assert [m["name"] for m in members] == ["Alice"]

    def test_member_with_unsettled_debt_is_blocked_until_settled(self, client, register, make_group, add_bill):
        alice, _, group, bob_id = _group_with_bob(client, register, make_group)
        add_bill(group_id=group["id"], paid_by="Alice", participants=["Alice", "Bob"], total_amount=20)

        blocked = client.delete(f"/api/groups/{group['id']}/members/{bob_id}", headers=alice)
        client.post("/api/settlements", json={"group_id": group["id"], "from": "Bob", "to": "Alice"})
        allowed = client.delete(f"/api/groups/{group['id']}/members/{bob_id}", headers=alice)

        assert blocked.status_code == 409
        assert "unsettled" in blocked.get_json()["error"]
        assert allowed.status_code == 200
