"""US07 (#9): Edit Existing Bill."""


class TestUS07EditExistingBill:

    def test_editing_amount_updates_bill_and_recalculates_balances(self, client, add_bill):
        # Arrange
        created = add_bill(
            title="Team Dinner",
            total_amount=90,
            paid_by="Alice",
            participants=["Alice", "Bob", "Carol"],
        ).get_json()["bill"]
        bill_id = created["id"]

        # Act
        response = client.put(f"/api/bills/{bill_id}", json={"total_amount": 120})

        # Assert
        assert response.status_code == 200
        bill = response.get_json()["bill"]
        assert bill["total_amount"] == 120
        shares = [p["share"] for p in bill["participants"]]
        assert shares == [40.0, 40.0, 40.0]

        listed = client.get("/api/bills?group_id=1").get_json()["bills"]
        assert listed[0]["total_amount"] == 120

        balance = client.get("/api/balance?group_id=1").get_json()
        assert balance["net"]["Alice"] == 80.0
        assert balance["net"]["Bob"] == -40.0
        assert balance["net"]["Carol"] == -40.0

    def test_editing_a_settled_share_requires_confirmation(self, client, add_bill):
        # Arrange: mark Bob's share settled, then try to edit without confirm
        created = add_bill(
            total_amount=90,
            paid_by="Alice",
            participants=["Alice", "Bob", "Carol"],
        ).get_json()["bill"]
        bill_id = created["id"]

        from models import BillParticipant
        participant = BillParticipant.query.filter_by(bill_id=bill_id, user_name="Bob").one()
        participant.settled = True
        from extensions import db
        db.session.commit()

        # Act
        blocked = client.put(f"/api/bills/{bill_id}", json={"total_amount": 120})

        # Assert
        assert blocked.status_code == 409
        body = blocked.get_json()
        assert body["requires_confirm"] is True
        assert "settled" in body["warning"].lower()
        assert client.get(f"/api/bills/{bill_id}").get_json()["bill"]["total_amount"] == 90

        confirmed = client.put(
            f"/api/bills/{bill_id}",
            json={"total_amount": 120, "confirm": True},
        )
        assert confirmed.status_code == 200
        assert confirmed.get_json()["bill"]["total_amount"] == 120
