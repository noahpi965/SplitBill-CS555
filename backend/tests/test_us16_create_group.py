"""US16 (#18): Create Expense Group."""


class TestUS16CreateGroup:

    def test_create_group_with_name_and_type(self, client, register):
        headers, user = register("Alice")

        response = client.post("/api/groups", json={"name": "Apartment 3B", "group_type": "Home"},
                               headers=headers)

        assert response.status_code == 201
        group = response.get_json()["group"]
        assert group["name"] == "Apartment 3B"
        assert group["group_type"] == "Home"
        assert group["member_count"] == 1
        assert group["invite_code"]

    def test_name_is_required_and_type_validated(self, client, register):
        headers, _ = register("Alice")

        no_name = client.post("/api/groups", json={"name": "  ", "group_type": "Trip"}, headers=headers)
        bad_type = client.post("/api/groups", json={"name": "X", "group_type": "Spaceship"}, headers=headers)

        assert no_name.status_code == 400
        assert bad_type.status_code == 400
