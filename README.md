# Digital Equb System
Mobile-first web app that digitizes the Ethiopian Equb: groups, contributions, penalties with fair notice, payout-risk tiers, and a tamper-evident audit log. Payments are sandbox only.

**Stack:** React + Vite + Tailwind/shadcn (Vercel) | Django + DRF + PostgreSQL/Neon (Render) | GitHub Actions cron for deadlines.

## Layout
`/frontend` `/backend` `/docs` (Charter) `/scripts` (tasks, GitHub setup) `/timeline.html` (live timeline)

## Start
```
./scripts/setup_github.sh OWNER/digital-equb   # repo, labels, 9 weekly milestones, 42 issues, branch protection
```
Then add repo secrets `API_URL` and `CRON_TOKEN` (Settings > Secrets > Actions).
Backend: `cd backend && python -m venv .venv && pip install -r requirements.txt` | Frontend: `cd frontend && npm create vite@latest .`
Team: Amar, Kaleab, Kidus, Yonas | Advisor: Mr. Eshetu Tadesse | Freeze Nov 15 (features) / Dec 12 (code) | Submit Dec 15.

## Design reference
The 3D Ring and Pot prototype is in `docs/prototypes/ring-and-pot.html` (open in a browser). Palette tokens: `frontend/src/styles/tokens.css`.
