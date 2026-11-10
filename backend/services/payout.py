from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from .rules import D
from .tiers import tier_for_slot

CENT = Decimal("0.01")


def q(x) -> Decimal:
    return D(x).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PayoutBreakdown:
    gross: Decimal
    premium: Decimal
    holdback: Decimal
    net: Decimal
    release_per_cycle: Decimal  # released after each later on-time contribution


def compute_payout(contribution, n, slot, guaranteed=False, rules=None) -> PayoutBreakdown:
    """Charter 6.4/6.5. holdback = rate * C * (N - slot); early tier pays premium_rate of the pot."""
    from .rules import DEFAULT_RULES
    r = {**DEFAULT_RULES, **(rules or {})}
    c = D(contribution)
    tier = tier_for_slot(slot, n)
    gross = q(c * n)
    premium = q(gross * D(r["premium_rate"])) if tier == "early" else Decimal("0.00")
    rate = D(r["holdback_rates"][tier])
    if rate > D(r["holdback_cap"]):
        raise ValueError("holdback rate above platform cap")
    holdback = Decimal("0.00") if guaranteed else q(rate * c * (n - slot))
    release = Decimal("0.00") if guaranteed else q(rate * c)
    return PayoutBreakdown(gross, premium, holdback, q(gross - premium - holdback), release)


def late_bonus_share(premium_pool, eligible_count: int) -> Decimal:
    """Premium pool split equally among eligible late-tier members (round down; remainder stays in pool)."""
    if eligible_count <= 0:
        return Decimal("0.00")
    return (D(premium_pool) / eligible_count).quantize(CENT, rounding="ROUND_DOWN")
