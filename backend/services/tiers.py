from math import ceil


def tier_size(n: int) -> int:
    return ceil(0.3 * n)


def tier_for_slot(slot: int, n: int) -> str:
    if not 1 <= slot <= n:
        raise ValueError("slot out of range")
    if slot <= tier_size(n):
        return "early"
    if slot > n - tier_size(n):
        return "late"
    return "middle"


def slots_in_tier(tier: str, n: int) -> range:
    k = tier_size(n)
    return {"early": range(1, k + 1), "late": range(n - k + 1, n + 1),
            "middle": range(k + 1, n - k + 1)}[tier]


def assign_slot(taken: set, tier: str, n: int):
    """Lowest free slot in the requested tier, or None if the tier is full."""
    return next((s for s in slots_in_tier(tier, n) if s not in taken), None)
