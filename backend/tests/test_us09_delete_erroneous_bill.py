"""US09 (#11): Delete Erroneous Bill."""
from extensions import db
from models import Bill


class TestUS09DeleteErroneousBill:

    def test_confirmed_delete_removes_bill_and_recalculates_balances(self, client, add_bill):
        # Arrange
        keep = add_bill(
            title="Groceries",
            total_amount=40,
            paid_by="Alice",
            participants=["Alice", "Bob"],
        ).get_json()["bill"]
        drop = add_bill(
            title="Logged by mistake",
            total_amount=90,
            paid_by="Alice",
            participants=["Alice", "Bob", "Carol"],
        ).get_json()["bill"]

        # Act: calling DELETE is the confirmed action from the UI dialog
        response = client.delete(f"/api/bills/{drop['id']}")

        # Assert
        assert response.status_code == 200
        assert db.session.get(Bill, drop["id"]) is None
        remaining = client.get("/api/bills?group_id=1").get_json()["bills"]
        assert [b["id"] for b in remaining] == [keep["id"]]
        balance = client.get("/api/balance?group_id=1").get_json()
        assert balance["net"] == {"Alice": 20.0, "Bob": -20.0}

    def test_bill_is_unchanged_when_delete_is_not_called(self, client, add_bill):
        # Arrange / Act: the Cancel path never hits DELETE
        created = add_bill().get_json()["bill"]

        # Assert
        listed = client.get("/api/bills?group_id=1").get_json()["bills"]
        assert listed[0]["id"] == created["id"]
        assert Bill.query.count() == 1
        missing = client.delete("/api/bills/999")
        assert missing.status_code == 404
        assert Bill.query.count() == 1
