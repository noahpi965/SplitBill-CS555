"""US05 (#7): View Balance Summary."""


class TestUS05ViewBalanceSummary:

    def test_shows_each_debt_direction_and_exact_amount(self, client, add_bill):
        # Arrange: Alice pays 90 for 3 people, Bob pays 30 for Bob & Carol
        add_bill(total_amount=90, paid_by="Alice", participants=["Alice", "Bob", "Carol"])
        add_bill(total_amount=30, paid_by="Bob", participants=["Bob", "Carol"])

        # Act
        response = client.get("/api/balance?group_id=1")

        # Assert: Bob net -15, Carol net -45, Alice net +60
        assert response.status_code == 200
        body = response.get_json()
        assert body["all_settled"] is False
        assert body["net"] == {"Alice": 60.0, "Bob": -15.0, "Carol": -45.0}
        assert body["balances"] == [
            {"from": "Carol", "to": "Alice", "amount": 45.0},
            {"from": "Bob",   "to": "Alice", "amount": 15.0},
        ]

    def test_all_settled_when_no_outstanding_debts(self, client, add_bill):
        # Arrange: a bill only the payer took part in leaves nobody owing anything
        add_bill(total_amount=20, paid_by="Alice", participants=["Alice"])

        # Act
        response = client.get("/api/balance?group_id=1")

        # Assert
        body = response.get_json()
        assert response.status_code == 200
        assert body["balances"] == []
        assert body["all_settled"] is True
        assert body["message"] == "All settled up"
