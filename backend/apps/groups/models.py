import secrets
import uuid

from django.conf import settings
from django.db import models


def new_invite_code():
    return secrets.token_urlsafe(8)[:10]


class Group(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft"
        RECRUITING = "recruiting"
        LOCKED = "locked"
        ACTIVE = "active"
        COMPLETED = "completed"
        DISSOLVED = "dissolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="organized_groups")
    name = models.CharField(max_length=80)
    member_count = models.PositiveSmallIntegerField()  # N
    contribution = models.DecimalField(max_digits=12, decimal_places=2)  # C, in ETB
    frequency = models.CharField(max_length=10, default="monthly")  # weekly | biweekly | monthly
    payout_model = models.CharField(max_length=12, default="rotational")  # rotational | lottery
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    invite_code = models.CharField(max_length=16, unique=True, default=new_invite_code)
    student_only = models.BooleanField(default=False)
    lottery_seed = models.CharField(max_length=64, blank=True)
    start_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class GroupTerms(models.Model):
    """Versioned rules. terms_hash is what each member accepts. Frozen at lock."""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="terms")
    version = models.PositiveIntegerField(default=1)
    terms_json = models.JSONField(default=dict)  # keys: see services/rules.py
    terms_hash = models.CharField(max_length=64)
    frozen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("group", "version")


class Membership(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        ACTIVE = "active"
        REPLACED = "replaced"
        REMOVED = "removed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="memberships")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    tier_request = models.CharField(max_length=8, blank=True)  # early | middle | late
    tier = models.CharField(max_length=8, blank=True)
    slot = models.PositiveSmallIntegerField(null=True, blank=True)
    accepted_terms_hash = models.CharField(max_length=64, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["group", "user"], name="one_membership_per_user_per_group"),
            models.UniqueConstraint(fields=["group", "slot"], name="unique_slot_per_group",
                                    condition=models.Q(slot__isnull=False)),
        ]
