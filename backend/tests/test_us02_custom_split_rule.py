"""US02 (#4): Custom Split Rule."""
import pytest
from models import Bill


class TestUS02CustomSplitRule:

    def test_custom_ratio_calculates_each_share_correctly(self, client):
        # Arrange: 3:7 custom split between two participants on $100
        payload = {
            "title":        "Couple Dinner",
            "total_amount": 100.00,
            "paid_by":      "Alice",
            "group_id":     1,
            "participants": ["Alice", "Bob"],
            "split_type":   "custom",
            "ratios":       {"Alice": 30, "Bob": 70},
        }

        # Act
        response = client.post("/api/bills", json=payload)

        # Assert
        assert response.status_code == 201
        bill = response.get_json()["bill"]
        shares = {p["user_name"]: p["share"] for p in bill["participants"]}
        assert shares == {"Alice": 30.0, "Bob": 70.0}
        assert sum(shares.values()) == pytest.approx(100.00)
        assert bill["split_type"] == "custom"
        assert Bill.query.count() == 1

    def test_ratios_not_summing_to_100_are_rejected(self, client):
        # Arrange
        payload = {
            "title":        "Couple Dinner",
            "total_amount": 100.00,
            "paid_by":      "Alice",
            "group_id":     1,
            "participants": ["Alice", "Bob"],
            "split_type":   "custom",
            "ratios":       {"Alice": 30, "Bob": 50},
        }

        # Act
        response = client.post("/api/bills", json=payload)

        # Assert
        assert response.status_code == 400
        assert "100%" in response.get_json()["errors"]["ratios"]
        assert Bill.query.count() == 0
