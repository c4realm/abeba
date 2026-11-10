import uuid

from django.db import models


class Cycle(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled"
        OPEN = "open"
        CLOSING = "closing"
        CLOSED = "closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey("groups.Group", on_delete=models.CASCADE, related_name="cycles")
    number = models.PositiveSmallIntegerField()
    due_date = models.DateField()  # local (Addis) date; deadline is 23:59:59 that day
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SCHEDULED)
    recipient = models.ForeignKey("groups.Membership", null=True, blank=True, on_delete=models.PROTECT,
                                  related_name="payout_cycles")

    class Meta:
        unique_together = ("group", "number")


class Obligation(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled"
        DUE = "due"
        LATE = "late"
        CURE = "cure"
        DEFAULTED = "defaulted"
        PAID = "paid"
        COVERED = "covered"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name="obligations")
    membership = models.ForeignKey("groups.Membership", on_delete=models.PROTECT, related_name="obligations")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SCHEDULED)
    fee_applied = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_at = models.DateTimeField(null=True, blank=True)
    extension_days = models.PositiveSmallIntegerField(default=0)  # approved hardship, max 3
    dispute_open = models.BooleanField(default=False)

    class Meta:
        unique_together = ("cycle", "membership")
