# Lesson 1: Create a group (our first vertical slice)

**Goal:** a logged-in user can create a group, see only their own groups, and open one group's details.
This one feature touches every layer of a web app. If you understand it, you understand the pattern for all the others.

## The journey of one request
```
POST /api/v1/groups/   (JSON + login token)
  1. config/urls.py          picks the route          -> apps/groups/urls.py
  2. apps/groups/views.py    receives the request     (thin: no rules here)
  3. serializers.py          checks the input shape   (types, lengths, allowed values)
  4. services/groups.py      applies the business rules and writes to the database (one transaction)
  5. models.py               the tables (Group, GroupTerms, Membership)
  6. serializers.py          shapes the response      (what the client is allowed to see)
```
**Why these layers:** each layer has one job, so a bug has one place to live and a rule has one place to change.

## File by file
| File | Job | Lines worth understanding |
| --- | --- | --- |
| `apps/groups/serializers.py` `GroupCreateSerializer` | A **whitelist**: only these 4 fields are accepted. Extra fields (`organizer`, `status`, `invite_code`) are ignored. | This is the defense against *mass assignment* (a client setting fields it should not). |
| `apps/groups/serializers.py` `GroupSerializer` | What we send back. `invite_code` is `None` unless you are the organizer. | `get_invite_code`: secrets are decided on the server, never in the UI. |
| `services/groups.py` `create_group` | The rules: standing must be good; new organizers max 10 members and 3 open groups; builds the versioned terms and its SHA-256 hash; makes the organizer a member; writes an audit event. | `@transaction.atomic` = all or nothing. `select_for_update` = lock the organizer's row so two simultaneous requests cannot both pass the "3 groups" check. |
| `apps/groups/views.py` `groups_visible_to` | The only groups a user may see: ones they belong to. | Filtering the query (not checking afterwards) makes other people's groups return **404**, so attackers cannot even confirm an ID exists. This blocks *IDOR*. |
| `apps/groups/views.py` `GroupListCreate.create` | Validates, calls the service, converts a `RuleViolation` into HTTP 400 or 403. | Views translate; services decide. |
| `tests/test_groups_api.py` | 14 tests (the 35th total). Read them like a specification. | One test per rule, plus attack tests: mass assignment, IDOR, restricted user. |

## Ideas you must be able to explain
1. **Serializer vs service vs view.** Shape of data, business rules, HTTP translation.
2. **Mass assignment.** Never trust which fields a client sends.
3. **IDOR.** Scope every query to the logged-in user so strangers get 404.
4. **Transactions and row locks.** Several writes succeed or fail together; concurrent requests are serialized.
5. **Terms hash.** The rules are frozen as JSON and fingerprinted; later, members accept that exact hash, so rules cannot be quietly changed.
6. **Audit event in the same transaction.** If the group is created, the record of it exists; if not, neither does.

## Try it by hand
```bash
cd backend && source .venv/bin/activate
python manage.py migrate && python manage.py createcachetable && python manage.py runserver
# in another terminal:
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ -H 'Content-Type: application/json' \
  -d '{"phone":"+251911223344","full_name":"Abebe Kebede","password":"Str0ng-pass-1234"}'
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login/ -H 'Content-Type: application/json' \
  -d '{"phone":"+251911223344","password":"Str0ng-pass-1234"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access'])")
curl -X POST http://127.0.0.1:8000/api/v1/groups/ -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"Campus Equb","member_count":10,"contribution":"1000.00","frequency":"monthly","status":"active"}'
```
Notice the response ignores `"status":"active"` and returns `"draft"`.

## Exercises (do all four; they are how you learn it)
1. Change `NEW_ORGANIZER_MAX_MEMBERS` to 8. Run the tests. Which fail, and why? Revert.
2. In `groups_visible_to`, remove the `filter(...)` (return `Group.objects.all()`). Which test catches the leak?
3. In `GroupCreateSerializer`, change `min_length=3` to `1`. Which test fails?
4. Predict what happens if the audit line were placed *after* the `return`. Then check how `test_create_group_happy_path` would react.

## Decisions to add to `docs/DECISIONS.md`
| Date | Decision | Reason | By |
| --- | --- | --- | --- |
| 2026-11-1x | The organizer is automatically a member (status approved) | In an Equb the organizer also contributes and takes a turn | human |
| 2026-11-1x | Groups are always created as `rotational`; lottery is stretch | Smaller scope for the main idea | human |
| 2026-11-1x | Contribution must be 50 to 100,000 Br; group size 3 to 50 | Sanity limits to block nonsense and abuse | human |

## Your approval checklist (before you commit)
- [ ] I can explain each of the six ideas above in my own words.
- [ ] I ran the four exercises and saw the failures.
- [ ] `./scripts/check.sh` says ALL CHECKS PASSED.
- [ ] I read every changed file; nothing in it surprises me.
