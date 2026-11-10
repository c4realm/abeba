import uuid

from django.db import models

from apps.core.models import AppendOnlyModel


class LedgerEntry(AppendOnlyModel):
    """Insert-only. Positive = charged to / contributed by the member, negative = paid out.
    Balances are always computed from these rows, never stored."""
    class Kind(models.TextChoices):
        CONTRIBUTION = "contribution"
        FEE = "fee"
        HOLDBACK = "holdback"
        RELEASE = "release"
        PREMIUM = "premium"
        BONUS = "bonus"
        PAYOUT = "payout"
        SETOFF = "setoff"
        COVER = "cover"
        REFUND = "refund"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey("groups.Group", on_delete=models.PROTECT)
    cycle = models.ForeignKey("cycles.Cycle", null=True, blank=True, on_delete=models.PROTECT)
    membership = models.ForeignKey("groups.Membership", null=True, blank=True, on_delete=models.PROTECT)
    kind = models.CharField(max_length=14, choices=Kind.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    idempotency_key = models.CharField(max_length=120, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Payout(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        PAID = "paid"
        ACKNOWLEDGED = "acknowledged"
        AUTO_ACKNOWLEDGED = "auto_acknowledged"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cycle = models.OneToOneField("cycles.Cycle", on_delete=models.PROTECT)
    recipient = models.ForeignKey("groups.Membership", on_delete=models.PROTECT)
    gross = models.DecimalField(max_digits=12, decimal_places=2)
    premium = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    holdback = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    setoff = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    receipt_no = models.CharField(max_length=24, blank=True)
