import hashlib
import json

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent

GENESIS = "0" * 64


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def compute_hash(prev_hash, seq, ts, actor_id, action, payload) -> str:
    raw = "|".join([prev_hash, str(seq), ts.isoformat(), str(actor_id or ""), action, canonical(payload)])
    return hashlib.sha256(raw.encode()).hexdigest()


@transaction.atomic
def append_event(action, payload=None, actor=None, group=None) -> AuditEvent:
    """Write in the SAME transaction as the change being audited. Single global hash chain."""
    payload = payload or {}
    last = AuditEvent.objects.select_for_update().order_by("-seq").first()
    seq = (last.seq + 1) if last else 1
    prev = last.hash if last else GENESIS
    ts = timezone.now()
    actor_id = getattr(actor, "id", None)
    return AuditEvent.objects.create(
        seq=seq, group_id=getattr(group, "id", None), actor_id=actor_id, action=action, payload=payload,
        prev_hash=prev, hash=compute_hash(prev, seq, ts, actor_id, action, payload), created_at=ts)


def verify_chain():
    """Returns (ok, first_bad_seq, count). Detects edited rows, gaps and broken links.
    TODO(S4): also compare the head against externally anchored hashes to catch full-chain rewrites."""
    prev, expected, count = GENESIS, 1, 0
    for e in AuditEvent.objects.order_by("seq").iterator():
        count += 1
        if e.seq != expected or e.prev_hash != prev or e.hash != compute_hash(
                prev, e.seq, e.created_at, e.actor_id, e.action, e.payload):
            return False, e.seq, count
        prev, expected = e.hash, expected + 1
    return True, None, count
