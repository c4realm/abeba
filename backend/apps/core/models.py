from django.db import models


class AppendOnlyQuerySet(models.QuerySet):
    def update(self, *a, **k):
        raise RuntimeError("append-only table: update is forbidden")

    def delete(self):
        raise RuntimeError("append-only table: delete is forbidden")

    def bulk_update(self, *a, **k):
        raise RuntimeError("append-only table: update is forbidden")


class AppendOnlyModel(models.Model):
    """Insert-only rows (ledger, audit). Also revoke UPDATE/DELETE for the app DB role if possible."""
    objects = AppendOnlyQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *a, **k):
        if not self._state.adding:
            raise RuntimeError("append-only table: rows cannot be modified")
        super().save(*a, **k)

    def delete(self, *a, **k):
        raise RuntimeError("append-only table: rows cannot be deleted")


class ClockState(models.Model):
    """Demo-only time offset (see simulate_time). Ignored unless DEMO_MODE is on."""
    offset_seconds = models.BigIntegerField(default=0)
