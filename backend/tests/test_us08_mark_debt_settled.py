"""US08 (#10): Mark Debt as Settled."""


class TestUS08MarkDebtAsSettled:

    def test_marking_settled_zeros_active_balance_and_moves_to_history(self, client, add_bill):
        # Arrange: Bob owes Alice $15, Carol owes Alice $45
        add_bill(total_amount=90, paid_by="Alice", participants=["Alice", "Bob", "Carol"])
        add_bill(total_amount=30, paid_by="Bob", participants=["Bob", "Carol"])
        before = client.get("/api/balance?group_id=1").get_json()
        assert {"from": "Bob", "to": "Alice", "amount": 15.0} in before["balances"]

        # Act
        response = client.post("/api/settlements", json={
            "group_id": 1,
            "from": "Bob",
            "to": "Alice",
        })

        # Assert
        assert response.status_code == 201
        body = response.get_json()
        assert {"from": "Bob", "to": "Alice", "amount": 15.0} not in body["balances"]
        assert body["settlement"]["amount"] == 15.0
        history = body["settled_history"]
        assert history[0]["from"] == "Bob"
        assert history[0]["to"] == "Alice"
        assert history[0]["amount"] == 15.0

    def test_settled_item_appears_in_history_not_active_balances(self, client, add_bill):
        # Arrange
        add_bill(total_amount=40, paid_by="Alice", participants=["Alice", "Bob"])
        client.post("/api/settlements", json={"group_id": 1, "from": "Bob", "to": "Alice"})

        # Act
        response = client.get("/api/balance?group_id=1")

        # Assert
        body = response.get_json()
        assert response.status_code == 200
        assert body["balances"] == []
        assert body["all_settled"] is True
        assert body["settled_history"][0]["from"] == "Bob"
        assert body["settled_history"][0]["to"] == "Alice"
        assert body["settled_history"][0]["amount"] == 20.0
