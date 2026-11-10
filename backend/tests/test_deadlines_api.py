from datetime import datetime

from rest_framework.test import APIClient

from apps.audit.models import AuditEvent
from apps.money.models import LedgerEntry
from services import audit
from services.deadlines import process_deadlines
from services.ladder import ADDIS


def test_ladder_end_to_end_and_idempotent(setup_obligation):
    group, m, ob = setup_obligation()
    process_deadlines(now=datetime(2026, 11, 11, 9, tzinfo=ADDIS))       # late, no fee
    assert LedgerEntry.objects.filter(kind="fee").count() == 0
    process_deadlines(now=datetime(2026, 11, 13, 9, tzinfo=ADDIS))       # cure, fee once
    process_deadlines(now=datetime(2026, 11, 13, 10, tzinfo=ADDIS))      # run again: nothing new
    assert LedgerEntry.objects.filter(kind="fee").count() == 1
    ob.refresh_from_db()
    assert ob.status == "cure" and str(ob.fee_applied) == "50.00"
    process_deadlines(now=datetime(2026, 11, 17, 9, tzinfo=ADDIS))       # defaulted
    ob.refresh_from_db()
    m.user.refresh_from_db()
    assert ob.status == "defaulted" and m.user.standing == "restricted"
    assert LedgerEntry.objects.filter(kind="fee").count() == 1
    assert audit.verify_chain()[0] and AuditEvent.objects.count() >= 4


def test_health(client):
    assert client.get("/api/v1/health/").status_code == 200


def test_cron_endpoint_requires_token(db):
    c = APIClient()
    assert c.post("/api/v1/internal/run-deadlines/").status_code == 401
    assert c.post("/api/v1/internal/run-deadlines/", HTTP_X_CRON_TOKEN="wrong").status_code == 401
    assert c.get("/api/v1/internal/run-deadlines/", HTTP_X_CRON_TOKEN="test-token").status_code == 405
    assert c.post("/api/v1/internal/run-deadlines/", HTTP_X_CRON_TOKEN="test-token").status_code == 200


def test_register_login_and_no_mass_assignment(db):
    c = APIClient()
    body = {"phone": "+251911223344", "full_name": "Abebe", "password": "Str0ng-pass-1234", "role": "admin",
            "standing": "good"}
    assert c.post("/api/v1/auth/register/", body, format="json").status_code == 201
    from apps.accounts.models import User
    assert User.objects.get(phone="+251911223344").role == "member"      # role ignored (T2)
    assert c.post("/api/v1/auth/login/", {"phone": "+251911223344", "password": "Str0ng-pass-1234"},
                  format="json").status_code == 200
    assert c.post("/api/v1/auth/register/", {**body, "phone": "0911"}, format="json").status_code == 400
    assert c.post("/api/v1/auth/register/", {**body, "password": "123"}, format="json").status_code == 400
