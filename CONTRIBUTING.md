# Workflow
1. Pick an issue from the board (current Week milestone). Assign yourself.
2. Branch: `feat/<issue>-short-name` or `fix/...`. Never push to `main`.
3. Open a PR early; one teammate must approve; CI must pass. Squash-merge.
4. Business rules are enforced on the server only. Money = Decimal, writes in `transaction.atomic()` with `select_for_update()`.
5. Never commit secrets. Copy `.env.example` to `.env`.
Rhythm: Mon plan (20 min), Wed blockers (15), Fri live demo + retro.
