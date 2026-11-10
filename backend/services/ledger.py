from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from apps.money.models import LedgerEntry


@transaction.atomic
def record(group, kind, amount, membership=None, cycle=None, key=None):
    """Insert a ledger row. Returns (entry, created). Same key twice returns the original (idempotent)."""
    if key:
        existing = LedgerEntry.objects.filter(idempotency_key=key).first()
        if existing:
            return existing, False
    entry = LedgerEntry.objects.create(group=group, kind=kind, amount=amount, membership=membership,
                                       cycle=cycle, idempotency_key=key)
    return entry, True


def balance(group, kind=None) -> Decimal:
    qs = LedgerEntry.objects.filter(group=group)
    if kind:
        qs = qs.filter(kind=kind)
    total = qs.aggregate(t=Sum("amount"))["t"] or Decimal("0")
    return Decimal(total).quantize(Decimal("0.01"))
