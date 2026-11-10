from datetime import date, datetime
from decimal import Decimal

from services.ladder import ADDIS, evaluate, fee_amount

DUE = date(2026, 11, 10)


def at(y, m, d, h=0, mi=0):
    return datetime(y, m, d, h, mi, tzinfo=ADDIS)


def ev(now, **kw):
    return evaluate(DUE, now, paid=False, grace_days=2, cure_days=3, **kw)


def test_boundaries():
    assert ev(at(2026, 11, 9, 23, 59)) == "scheduled"
    assert ev(at(2026, 11, 10, 12)) == "due"
    assert ev(at(2026, 11, 10, 23, 59)) == "due"          # before 23:59:59
    assert ev(at(2026, 11, 11, 0, 30)) == "late"          # grace: no fee
    assert ev(at(2026, 11, 12, 23, 59)) == "late"
    assert ev(at(2026, 11, 13, 0, 30)) == "cure"          # D+G+1
    assert ev(at(2026, 11, 15, 23, 59)) == "cure"
    assert ev(at(2026, 11, 16, 0, 30)) == "defaulted"


def test_paid_wins():
    assert evaluate(DUE, at(2026, 12, 1), paid=True, grace_days=2, cure_days=3) == "paid"


def test_dispute_pauses_clock():
    assert ev(at(2026, 12, 1), dispute_open=True) == "cure"


def test_hardship_extension_shifts_deadline():
    assert ev(at(2026, 11, 12, 12), extension_days=3) == "due"


def test_fee_is_capped_and_not_compounded():
    assert fee_amount("1000", "0.05", "0.10") == Decimal("50.00")
    assert fee_amount("1000", "0.25", "0.10") == Decimal("100.00")
