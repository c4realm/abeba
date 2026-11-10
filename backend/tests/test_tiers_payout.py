from decimal import Decimal

import pytest

from services.payout import compute_payout, late_bonus_share
from services.tiers import assign_slot, tier_for_slot


def test_tiers_n10():
    assert [tier_for_slot(s, 10) for s in range(1, 11)] == ["early"] * 3 + ["middle"] * 4 + ["late"] * 3


def test_assign_slot_lowest_free_in_tier():
    assert assign_slot({1, 2}, "early", 10) == 3
    assert assign_slot({1, 2, 3}, "early", 10) is None


def test_worked_example_charter_6_9():
    p = compute_payout("1000", 10, 1)
    assert (p.gross, p.premium, p.holdback, p.net) == (
        Decimal("10000.00"), Decimal("200.00"), Decimal("2700.00"), Decimal("7100.00"))
    assert p.release_per_cycle == Decimal("300.00")


def test_guarantor_removes_holdback():
    p = compute_payout("1000", 10, 1, guaranteed=True)
    assert p.holdback == Decimal("0.00") and p.net == Decimal("9800.00")


def test_late_tier_no_holdback_no_premium():
    p = compute_payout("1000", 10, 10)
    assert p.holdback == 0 and p.premium == 0 and p.net == Decimal("10000.00")


def test_middle_tier_holdback():
    p = compute_payout("1000", 10, 5)  # 10% * 1000 * 5
    assert p.holdback == Decimal("500.00")


def test_holdback_cap_enforced():
    with pytest.raises(ValueError):
        compute_payout("1000", 10, 1, rules={"holdback_rates": {"early": "0.60", "middle": "0", "late": "0"}})


def test_bonus_share_rounds_down():
    assert late_bonus_share("200.00", 3) == Decimal("66.66")
    assert late_bonus_share("200.00", 0) == Decimal("0.00")
