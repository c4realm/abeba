import pytest

from apps.audit.models import AuditEvent
from apps.money.models import LedgerEntry
from services import audit, ledger


def test_audit_chain_verifies_and_detects_tamper(db):
    for i in range(3):
        audit.append_event("test.event", {"i": i})
    assert audit.verify_chain() == (True, None, 3)
    # tamper with row 2 directly in the DB (bypassing the append-only guard, as an attacker with DB access would)
    AuditEvent.objects.model._base_manager.filter(seq=2).update(payload={"i": 999})
    ok, bad, _ = audit.verify_chain()
    assert not ok and bad == 2


def test_audit_detects_deleted_row(db):
    for i in range(3):
        audit.append_event("test.event", {"i": i})
    AuditEvent._base_manager.filter(seq=2).delete()
    ok, bad, _ = audit.verify_chain()
    assert not ok and bad == 3


def test_append_only_guards(db, setup_obligation):
    group, m, _ = setup_obligation()
    entry, _ = ledger.record(group, "contribution", "1000.00", membership=m)
    entry.amount = 1
    with pytest.raises(RuntimeError):
        entry.save()
    with pytest.raises(RuntimeError):
        LedgerEntry.objects.all().delete()
    with pytest.raises(RuntimeError):
        LedgerEntry.objects.update(amount=0)


def test_ledger_idempotency(db, setup_obligation):
    group, m, _ = setup_obligation()
    _, c1 = ledger.record(group, "contribution", "1000.00", membership=m, key="pay:1")
    _, c2 = ledger.record(group, "contribution", "1000.00", membership=m, key="pay:1")
    assert (c1, c2) == (True, False)
    assert str(ledger.balance(group)) == "1000.00"
