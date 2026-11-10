from datetime import date

import pytest

from apps.accounts.models import User
from apps.cycles.models import Cycle, Obligation
from apps.groups.models import Group, Membership


@pytest.fixture
def setup_obligation(db):
    """One group, one member, one cycle due 2026-11-10, one 1000 Br obligation."""
    def make(due=date(2026, 11, 10), amount="1000.00"):
        org = User.objects.create_user("+251911000001", "pass-12345-xyz", full_name="Org")
        mem_user = User.objects.create_user("+251911000002", "pass-12345-xyz", full_name="Member")
        group = Group.objects.create(organizer=org, name="Test", member_count=10, contribution=amount,
                                     status="active")
        m = Membership.objects.create(group=group, user=mem_user, status="active", slot=1, tier="early")
        cycle = Cycle.objects.create(group=group, number=1, due_date=due, status="open")
        ob = Obligation.objects.create(cycle=cycle, membership=m, amount=amount)
        return group, m, ob
    return make
