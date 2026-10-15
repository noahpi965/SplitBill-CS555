"""US06 (#8): View Monthly Report."""
import pytest


class TestUS06ViewMonthlyReport:

    def test_report_shows_total_bill_count_and_category_breakdown(self, client, add_bill):
        # Arrange
        add_bill(title="Dinner",    total_amount=60,   category="Food",      date="2026-10-02")
        add_bill(title="Lunch",     total_amount=25.5, category="Food",      date="2026-10-20")
        add_bill(title="Uber",      total_amount=18,   category="Transport", date="2026-10-31")
        add_bill(title="Sept rent", total_amount=900,  category="Rent",      date="2026-09-30")

        # Act
        response = client.get("/api/reports/monthly?group_id=1&year=2026&month=10")

        # Assert
        assert response.status_code == 200
        body = response.get_json()
        assert body["total"] == pytest.approx(103.5)
        assert body["bill_count"] == 3
        assert body["categories"] == [
            {"category": "Food",      "amount": 85.5},
            {"category": "Transport", "amount": 18.0},
        ]
        assert [i["title"] for i in body["items"]] == ["Dinner", "Lunch", "Uber"]

    def test_month_without_activity_shows_no_expenses_message(self, client, add_bill):
        # Arrange
        add_bill(date="2026-10-05")

        # Act
        response = client.get("/api/reports/monthly?group_id=1&year=2026&month=11")

        # Assert
        assert response.status_code == 200
        body = response.get_json()
        assert body["total"] == 0
        assert body["bill_count"] == 0
        assert body["categories"] == []
        assert body["message"] == "No expenses recorded for this period"
