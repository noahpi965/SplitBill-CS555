"""US10 (#12): Remove Participant from Bill."""


class TestUS10RemoveParticipantFromBill:

    def test_removing_participant_recalculates_remaining_shares(self, client, add_bill):
        # Arrange
        created = add_bill(
            total_amount=90,
            paid_by="Alice",
            participants=["Alice", "Bob", "Carol"],
        ).get_json()["bill"]

        # Act
        response = client.put(f"/api/bills/{created['id']}", json={
            "participants": ["Alice", "Bob"],
        })

        # Assert
        assert response.status_code == 200
        names = [p["user_name"] for p in response.get_json()["bill"]["participants"]]
        shares = [p["share"] for p in response.get_json()["bill"]["participants"]]
        assert names == ["Alice", "Bob"]
        assert shares == [45.0, 45.0]
        balance = client.get("/api/balance?group_id=1").get_json()
        assert "Carol" not in balance["net"]
        assert balance["net"] == {"Alice": 45.0, "Bob": -45.0}

    def test_removing_a_paid_participant_requires_confirmation(self, client, add_bill):
        # Arrange: Bob already paid/settled his share
        created = add_bill(
            total_amount=90,
            paid_by="Alice",
            participants=["Alice", "Bob", "Carol"],
        ).get_json()["bill"]
        from models import BillParticipant
        from extensions import db
        participant = BillParticipant.query.filter_by(bill_id=created["id"], user_name="Bob").one()
        participant.settled = True
        db.session.commit()

        # Act
        blocked = client.put(f"/api/bills/{created['id']}", json={
            "participants": ["Alice", "Carol"],
        })

        # Assert
        assert blocked.status_code == 409
        body = blocked.get_json()
        assert body["requires_confirm"] is True
        assert "payment record" in body["warning"].lower()
        names = [
            p["user_name"]
            for p in client.get(f"/api/bills/{created['id']}").get_json()["bill"]["participants"]
        ]
        assert names == ["Alice", "Bob", "Carol"]

        confirmed = client.put(f"/api/bills/{created['id']}", json={
            "participants": ["Alice", "Carol"],
            "confirm": True,
        })
        assert confirmed.status_code == 200
        assert [p["user_name"] for p in confirmed.get_json()["bill"]["participants"]] == ["Alice", "Carol"]
