"""US04 (#2): View Group Bills."""


class TestUS04ViewGroupBills:

    def test_lists_group_bills_with_date_amount_payer_and_participants(self, client, add_bill):
        # Arrange
        add_bill(title="Groceries", total_amount=40, paid_by="Bob",
                 participants=["Alice", "Bob"], date="2026-10-01")
        add_bill(title="Taxi", total_amount=30, paid_by="Carol",
                 participants=["Bob", "Carol"], date="2026-10-03")
        add_bill(title="Other group", group_id=2)

        # Act
        response = client.get("/api/bills?group_id=1")

        # Assert
        assert response.status_code == 200
        bills = response.get_json()["bills"]
        assert [b["title"] for b in bills] == ["Taxi", "Groceries"]
        taxi = bills[0]
        assert taxi["created_at"].startswith("2026-10-03")
        assert taxi["total_amount"] == 30
        assert taxi["paid_by"] == "Carol"
        assert [p["user_name"] for p in taxi["participants"]] == ["Bob", "Carol"]

    def test_empty_group_shows_friendly_message(self, client):
        # Act
        response = client.get("/api/bills?group_id=99")

        # Assert
        assert response.status_code == 200
        body = response.get_json()
        assert body["bills"] == []
        assert body["message"] == "No bills yet. Add one!"
