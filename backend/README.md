# Backend (Django + DRF + PostgreSQL)

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # set DATABASE_URL (Neon) or leave unset to use local SQLite
python manage.py migrate
python manage.py createcachetable throttle_cache
python -m pytest                # 21 tests: tiers, payout math, ladder boundaries, ledger, audit chain, API
python manage.py runserver
```

## What exists (spec phases P0 to P3 core)
- `services/` pure business logic: `tiers`, `payout` (holdback, premium; worked example = 7,100 Br), `ladder` (every deadline boundary), `ledger` (insert-only, idempotent), `audit` (hash chain + verify), `deadlines` (idempotent job).
- `apps/` models for users, groups, terms, memberships, cycles, obligations, ledger, payouts, audit.
- Auth: register (no mass assignment), login, refresh (JWT, bcrypt, throttled).
- `POST /api/v1/internal/run-deadlines/` (X-Cron-Token, constant-time compare).
- Guards: append-only ledger and audit, DEBUG/DEMO_MODE refused in production, no Django admin.

## Next (see the spec)
Group/membership/terms-acceptance endpoints, cycle generation, sandbox payment with Idempotency-Key, cover order (holdback, guarantor, payout claim), payouts + set-off, notices/disputes/hardship, password reset (S1), refresh token in HttpOnly cookie, audit anchoring (S4), SecurityEvent log (S9), OpenAPI docs.
