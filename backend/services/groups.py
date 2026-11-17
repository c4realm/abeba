"""Group rules (Charter 6.1 and 6.2). Views call these functions; the rules live here, not in the views."""
import hashlib

from django.db import transaction

from apps.accounts.models import User
from apps.groups.models import Group, GroupTerms, Membership
from services import audit
from services.rules import DEFAULT_RULES

OPEN_STATUSES = ("draft", "recruiting", "locked", "active")
NEW_ORGANIZER_MAX_MEMBERS = 10
NEW_ORGANIZER_MAX_OPEN_GROUPS = 3


class RuleViolation(Exception):
    """A business rule said no. `code` lets the view pick the right HTTP status."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def terms_hash(terms: dict) -> str:
    """Fingerprint of the rules. Members will accept this exact hash, so the rules cannot change silently."""
    return hashlib.sha256(audit.canonical(terms).encode()).hexdigest()


@transaction.atomic
def create_group(organizer, name, member_count, contribution, frequency) -> Group:
    # Lock the organizer's row so two simultaneous requests cannot both slip past the group limit.
    organizer = User.objects.select_for_update().get(pk=organizer.pk)

    if organizer.standing != User.Standing.GOOD:
        raise RuleViolation("restricted", "Your account is restricted and cannot organize groups.")

    organized = Group.objects.filter(organizer=organizer)
    if not organized.filter(status=Group.Status.COMPLETED).exists():  # a "new" organizer
        if member_count > NEW_ORGANIZER_MAX_MEMBERS:
            raise RuleViolation(
                "limit", f"New organizers can create groups of up to {NEW_ORGANIZER_MAX_MEMBERS} members.")
        if organized.filter(status__in=OPEN_STATUSES).count() >= NEW_ORGANIZER_MAX_OPEN_GROUPS:
            raise RuleViolation(
                "limit", f"New organizers can have up to {NEW_ORGANIZER_MAX_OPEN_GROUPS} open groups.")

    group = Group.objects.create(organizer=organizer, name=name, member_count=member_count,
                                 contribution=contribution, frequency=frequency)  # status starts as draft
    terms = {"member_count": member_count, "contribution": str(contribution), "frequency": frequency,
             "payout_model": group.payout_model, **DEFAULT_RULES}
    digest = terms_hash(terms)
    GroupTerms.objects.create(group=group, version=1, terms_json=terms, terms_hash=digest)
    Membership.objects.create(group=group, user=organizer, status=Membership.Status.APPROVED)
    audit.append_event("group.created", {"group": str(group.id), "terms_hash": digest},
                       actor=organizer, group=group)
    return group
