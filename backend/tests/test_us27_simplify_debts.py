"""US27 (#29): Smart Debt Simplification Algorithm"""
import pytest

from simplify import simplify_debts


def _add_complex_bills(add_bill, gid):
    # Net: A -5, B +3, C +2 (one cluster) and D -4, E +4 (another).
    # Plain matching needs 4 transfers; the optimum is 3.
    add_bill(group_id=gid, title="b1", total_amount=6, paid_by="B", participants=["B", "A"])
    add_bill(group_id=gid, title="b2", total_amount=4, paid_by="C", participants=["C", "A"])
    add_bill(group_id=gid, title="b3", total_amount=8, paid_by="E", participants=["E", "D"])


@pytest.fixture
def _complex_bills(add_bill):
    _add_complex_bills(add_bill, 1)


def _apply(transfers, nets):
    """Net balances after performing the transfers (should all be zero)"""
    result = dict(nets)
    for t in transfers:
        cents = round(t["amount"] * 100)
        result[t["from"]] += cents
        result[t["to"]] -= cents
    return result


class TestUS27SimplifyDebts:

    def test_finds_fewer_transfers_than_greedy_matching(self):
        # Greedy largest-first matching needs 4 transfers here; the optimum is 3.
        nets = {"A": -500, "B": 300, "C": 200, "D": -400, "E": 400}

        transfers = simplify_debts(nets)

        assert len(transfers) == 3
        assert all(v == 0 for v in _apply(transfers, nets).values())

    def test_balance_endpoint_uses_simplify_flag(self, client, _complex_bills):
        plain = client.get("/api/balance?group_id=1").get_json()
        simple = client.get("/api/balance?group_id=1&simplify=true").get_json()

        assert len(plain["balances"]) == 4
        assert simple["simplified"] is True
        assert len(simple["balances"]) == 3
        assert simple["original_transfer_count"] == 4
