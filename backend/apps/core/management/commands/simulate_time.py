from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core.models import ClockState


class Command(BaseCommand):
    help = "Advance the app clock for demos. CLI only; refuses to run unless DEMO_MODE=1."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=float, default=0)
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **opts):
        if not settings.DEMO_MODE or settings.ENVIRONMENT == "production":
            raise CommandError("simulate_time requires DEMO_MODE=1 outside production")
        state, _ = ClockState.objects.get_or_create(pk=1)
        state.offset_seconds = 0 if opts["reset"] else state.offset_seconds + int(opts["days"] * 86400)
        state.save()
        self.stdout.write(f"clock offset is now {state.offset_seconds} seconds")
