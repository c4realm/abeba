import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditEvent
from apps.groups.models import Group, GroupTerms, Membership
from services import audit
from services.groups import terms_hash

URL = "/api/v1/groups/"
GOOD = {"name": "Campus Equb", "member_count": 10, "contribution": "1000.00", "frequency": "monthly"}


def make_user(phone, **extra):
    return User.objects.create_user(phone, "pass-12345-xyz", full_name=extra.pop("full_name", "Test User"), **extra)


def client_for(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def organizer(db):
    return make_user("+251911000101", full_name="Organizer One")


def test_requires_login(db):
    assert APIClient().post(URL, GOOD, format="json").status_code == 401
    assert APIClient().get(URL).status_code == 401


def test_create_group_happy_path(organizer):
    r = client_for(organizer).post(URL, GOOD, format="json")
    assert r.status_code == 201
    group = Group.objects.get(pk=r.data["id"])
    assert group.status == "draft" and group.organizer == organizer
    assert Membership.objects.filter(group=group, user=organizer, status="approved").exists()  # organizer is a member
    terms = GroupTerms.objects.get(group=group, version=1)
    assert terms.terms_hash == terms_hash(terms.terms_json) and len(terms.terms_hash) == 64
    assert r.data["terms_hash"] == terms.terms_hash and r.data["invite_code"] == group.invite_code
    assert AuditEvent.objects.filter(action="group.created", group_id=group.id).count() == 1
    assert audit.verify_chain()[0]


def test_client_cannot_set_protected_fields(organizer):
    other = make_user("+251911000102")
    body = {**GOOD, "organizer": str(other.id), "status": "active", "invite_code": "HACKED", "payout_model": "lottery"}
    r = client_for(organizer).post(URL, body, format="json")
    group = Group.objects.get(pk=r.data["id"])
    assert (group.organizer, group.status, group.payout_model) == (organizer, "draft", "rotational")
    assert group.invite_code != "HACKED"


@pytest.mark.parametrize("change", [{"name": "ab"}, {"member_count": 2}, {"member_count": 51},
                                    {"contribution": "10.00"}, {"contribution": "100001"}, {"frequency": "daily"}])
def test_validation_rejects_bad_input(organizer, change):
    assert client_for(organizer).post(URL, {**GOOD, **change}, format="json").status_code == 400
    assert Group.objects.count() == 0


def test_new_organizer_limits(organizer):
    c = client_for(organizer)
    assert c.post(URL, {**GOOD, "member_count": 11}, format="json").status_code == 400
    for i in range(3):
        assert c.post(URL, {**GOOD, "name": f"Group {i}"}, format="json").status_code == 201
    assert c.post(URL, {**GOOD, "name": "Group 4"}, format="json").status_code == 400


def test_experienced_organizer_can_make_bigger_groups(organizer):
    Group.objects.create(organizer=organizer, name="Done", member_count=5, contribution="100", status="completed")
    assert client_for(organizer).post(URL, {**GOOD, "member_count": 20}, format="json").status_code == 201


def test_restricted_user_cannot_organize(db):
    user = make_user("+251911000103", standing="restricted")
    assert client_for(user).post(URL, GOOD, format="json").status_code == 403


def test_list_and_detail_are_private(organizer):
    mine = client_for(organizer).post(URL, GOOD, format="json").data["id"]
    stranger = make_user("+251911000104")
    assert client_for(stranger).get(URL).data["results"] == []               # sees nothing
    assert client_for(stranger).get(f"{URL}{mine}/").status_code == 404      # other people's group does not exist
    assert [g["id"] for g in client_for(organizer).get(URL).data["results"]] == [mine]


def test_invite_code_only_for_organizer(organizer):
    gid = client_for(organizer).post(URL, GOOD, format="json").data["id"]
    member = make_user("+251911000105")
    Membership.objects.create(group_id=gid, user=member, status="approved")
    seen = client_for(member).get(f"{URL}{gid}/")
    assert seen.status_code == 200 and seen.data["invite_code"] is None and seen.data["is_organizer"] is False
