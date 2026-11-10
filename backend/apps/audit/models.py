from django.db import models

from apps.core.models import AppendOnlyModel


class AuditEvent(AppendOnlyModel):
    seq = models.PositiveBigIntegerField(unique=True)
    group_id = models.UUIDField(null=True, blank=True)
    actor_id = models.UUIDField(null=True, blank=True)
    action = models.CharField(max_length=80)
    payload = models.JSONField(default=dict)
    prev_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64)
    created_at = models.DateTimeField()
