"""US01 (#3): Add a Shared Bill."""
import pytest
from models import Bill


class TestUS01AddSharedBill:

    def test_valid_bill_is_saved_with_equal_shares(self, client):
        # Arrange
        payload = {
            "title":        "Team Dinner",
            "total_amount": 100.00,
            "paid_by":      "Alice",
            "group_id":     1,
            "participants": ["Alice", "Bob", "Carol"],
        }

        # Act
        response = client.post("/api/bills", json=payload)

        # Assert
        assert response.status_code == 201
        bill = response.get_json()["bill"]
        assert bill["title"] == "Team Dinner"
        assert bill["paid_by"] == "Alice"
        shares = [p["share"] for p in bill["participants"]]
        assert shares == [33.34, 33.33, 33.33]
        assert sum(shares) == pytest.approx(100.00)
        assert [b.id for b in Bill.query.filter_by(group_id=1)] == [bill["id"]]

    def test_empty_amount_returns_validation_error_and_is_not_saved(self, add_bill):
        # Act
        response = add_bill(total_amount="")

        # Assert
        assert response.status_code == 400
        assert "total_amount" in response.get_json()["errors"]
        assert Bill.query.count() == 0
