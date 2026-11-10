from datetime import timedelta

from django.conf import settings
from django.utils import timezone


def get_now():
    """All business logic reads time here, so demos can time-travel (staging only)."""
    now = timezone.now()
    if settings.DEMO_MODE:
        from .models import ClockState
        state = ClockState.objects.first()
        if state:
            return now + timedelta(seconds=state.offset_seconds)
    return now
