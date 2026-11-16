"""Debt simplification (US27): minimise the number of transfers.

Given each member's net balance in cents (positive = is owed, negative = owes),
the minimum number of transfers is ``n - k`` where ``k`` is the largest number
of disjoint groups whose balances each sum to zero. We find ``k`` exactly with
a bitmask DP for small groups and fall back to a greedy matching otherwise.
"""

EXACT_LIMIT = 12


def _transfers_within(members):
    """Settle one zero-sum group with len(members) - 1 transfers."""
    creditors = sorted(((n, c) for n, c in members if c > 0), key=lambda x: (-x[1], x[0]))
    debtors = sorted(((n, -c) for n, c in members if c < 0), key=lambda x: (-x[1], x[0]))
    out = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        d, owe = debtors[i]
        c, due = creditors[j]
        amt = min(owe, due)
        out.append({"from": d, "to": c, "amount": amt / 100})
        debtors[i] = (d, owe - amt)
        creditors[j] = (c, due - amt)
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1
    return out


def _zero_sum_groups(items):
    n = len(items)
    full = (1 << n) - 1
    sums = [0] * (1 << n)
    for mask in range(1, 1 << n):
        low = (mask & -mask).bit_length() - 1
        sums[mask] = sums[mask & (mask - 1)] + items[low][1]

    # best[mask] = max number of zero-sum groups that partition `mask`
    # (-inf if mask cannot be partitioned into zero-sum groups).
    NEG = -1
    best = [NEG] * (1 << n)
    choice = [0] * (1 << n)
    best[0] = 0
    for mask in range(1, 1 << n):
        if sums[mask] != 0:
            continue
        low = mask & -mask
        rest = mask ^ low
        sub = rest
        while True:
            group = sub | low  # always contains the lowest bit
            remainder = mask ^ group
            if sums[group] == 0 and best[remainder] != NEG and best[remainder] + 1 > best[mask]:
                best[mask] = best[remainder] + 1
                choice[mask] = group
            if sub == 0:
                break
            sub = (sub - 1) & rest

    groups = []
    mask = full
    while mask:
        group = choice[mask]
        groups.append([items[i] for i in range(n) if group >> i & 1])
        mask ^= group
    return groups


def simplify_debts(net_cents):
    """Return a minimal list of {from, to, amount} transfers settling net_cents."""
    items = sorted((n, c) for n, c in net_cents.items() if c != 0)
    if not items:
        return []
    if len(items) <= EXACT_LIMIT:
        groups = _zero_sum_groups(items)
    else:
        groups = [items]
    transfers = []
    for g in groups:
        transfers.extend(_transfers_within(g))
    return transfers
