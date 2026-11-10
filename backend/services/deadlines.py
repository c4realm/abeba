from django.db import transaction

from apps.core.clock import get_now
from apps.cycles.models import Obligation
from services import audit, ladder, ledger
from services.rules import get_rules

OPEN_STATUSES = ["scheduled", "due", "late", "cure"]


def process_deadlines(now=None) -> dict:
    """Advance every open obligation along the ladder. Safe to run any number of times (idempotent).
    TODO(P3): send notices/emails; cover shortfall in order holdback -> guarantor -> payout claim."""
    now = now or get_now()
    summary = {"checked": 0, "transitions": 0, "fees": 0, "defaults": 0}
    with transaction.atomic():
        qs = (Obligation.objects.select_for_update(of=("self",))
              .select_related("cycle__group", "membership__user").filter(status__in=OPEN_STATUSES))
        for ob in qs:
            summary["checked"] += 1
            group = ob.cycle.group
            rules = get_rules(group)
            new = ladder.evaluate(ob.cycle.due_date, now, paid=False, grace_days=rules["grace_days"],
                                  cure_days=rules["cure_days"], extension_days=ob.extension_days,
                                  dispute_open=ob.dispute_open)
            if new in ("cure", "defaulted") and ob.fee_applied == 0:
                fee = ladder.fee_amount(ob.amount, rules["fee_rate"], rules["fee_cap"])
                ledger.record(group, "fee", fee, membership=ob.membership, cycle=ob.cycle, key=f"fee:{ob.id}")
                ob.fee_applied = fee
                summary["fees"] += 1
                audit.append_event("obligation.fee_applied", {"obligation": str(ob.id), "fee": str(fee)}, group=group)
            if new == "defaulted":
                user = ob.membership.user
                if user.standing == "good":
                    user.standing = "restricted"
                    user.save(update_fields=["standing"])
                summary["defaults"] += 1
            if new != ob.status:
                audit.append_event("obligation.status", {"obligation": str(ob.id), "from": ob.status, "to": new},
                                   group=group)
                ob.status = new
                summary["transitions"] += 1
            ob.save()
    return summary
