"""Pure penalty-ladder logic (Charter 6.6). No database access: easy to test at every boundary."""
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from .payout import q
from .rules import D

ADDIS = ZoneInfo("Africa/Addis_Ababa")


def deadline_at(due: date, extension_days: int = 0) -> datetime:
    return datetime.combine(due + timedelta(days=extension_days), time(23, 59, 59), tzinfo=ADDIS)


def evaluate(due: date, now: datetime, paid: bool, grace_days: int, cure_days: int,
             extension_days: int = 0, dispute_open: bool = False) -> str:
    """Return one of: paid, scheduled, due, late, cure, defaulted."""
    if paid:
        return "paid"
    deadline = deadline_at(due, extension_days)
    grace_end = deadline + timedelta(days=grace_days)
    cure_end = grace_end + timedelta(days=cure_days)
    if now <= deadline:
        start = datetime.combine(due, time(0, 0), tzinfo=ADDIS)
        return "scheduled" if now < start else "due"
    if now <= grace_end:
        return "late"  # no fee during grace
    if dispute_open or now <= cure_end:
        return "cure"  # fee applies on entry; a dispute pauses the clock
    return "defaulted"


def fee_amount(contribution, rate, cap) -> Decimal:
    """One-time, never compounded; rate is capped by the platform cap."""
    return q(D(contribution) * min(D(rate), D(cap)))
