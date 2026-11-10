# VSCodium + free AI agents: setup guide

## 1. One-time setup
1. Install VSCodium. Open the project: `codium .` (use "Shell command: Install 'codium' command in PATH" if needed).
   VSCodium uses the **Open VSX** registry, not Microsoft's marketplace, so Copilot and Pylance are not available.
2. Unzip this overlay into the repo root (it adds AGENTS.md, .vscode/, scripts/check.sh, docs/). Commit your own work first:
   the overlay replaces `backend/requirements.txt`, `backend/ruff.toml`, `backend/manage.py`, `backend/config/wsgi.py`.
3. Git (the zip has no history):
   ```
   git init -b main && git add . && git commit -m "chore: initial scaffold"
   ./scripts/setup_github.sh YOURUSER/digital-equb      # repo, labels, milestones, issues (needs: gh auth login)
   ```
4. Backend: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt ruff bandit pip-audit`
5. Install gitleaks (secret scanner) from its GitHub releases page, then run `./scripts/check.sh`. Everything must pass.
6. Extensions: open the Extensions panel, type `@recommended`, install all. If one is missing on Open VSX, skip it or install its VSIX.

## 2. The agent: Kilo Code
Install **Kilo Code** from the Extensions panel. This repo ships four modes (`.roomodes`): Equb Architect (plans, docs only),
Equb Builder (implements one issue), Equb Security Reviewer (read-only review), Equb UI Craftsperson (frontend only).
If the modes do not appear, create them by hand in Kilo's Modes screen using the text in `.roomodes`.
Alternative with the same rules: Cline (publisher saoudrizwan) reads `.clineignore` and `AGENTS.md`.
Terminal agent option: OpenCode in VSCodium's terminal (reads `AGENTS.md`).

## 3. Free models (bring your own key)
Create keys here and paste them into the agent's provider settings (never into the repo):
| Provider | Key page | Notes |
| --- | --- | --- |
| Google Gemini (AI Studio) | aistudio.google.com/apikey | Native provider in Kilo/Cline. Use a Flash-class model. Free tier content may be used by Google. |
| Cerebras | cloud.cerebras.ai | OpenAI-compatible, base URL https://api.cerebras.ai/v1. Large daily token allowance. |
| Groq | console.groq.com/keys | OpenAI-compatible, base URL https://api.groq.com/openai/v1. Fast. |
| OpenRouter | openrouter.ai/keys | Models ending in `:free`. Tight daily cap: backup only. |
Model names change often: pick from the provider's current list. Free tiers change without notice.
Strategy: Gemini as main, Cerebras or Groq when you hit its daily limit, OpenRouter last. Ollama (local) is the offline fallback.
Use a stronger (paid or student-credit) model only for hard problems: money logic, security review.

## 4. Daily workflow (one issue at a time)
1. Pick an issue in the current Week milestone. `git switch -c feat/<issue>-name`.
2. **Architect** mode: "Plan issue #N" and read the plan. Fix it before any code.
3. **Builder** mode: "Implement the plan." It must run `./scripts/check.sh` and show the output.
4. **Security Reviewer** mode on the diff (required for auth, money, permissions, ledger, audit).
5. You read the diff yourself (especially money and security code), open a PR, wait for CI, merge.
6. The agent appends to `docs/AGENT_LOG.md`; decisions go in `docs/DECISIONS.md`. This is your explain-and-track record.

## 5. Safety rules for free agents
- Free tiers may log or train on your prompts: never paste real secrets, keys or personal data. `.kilocodeignore`/`.clineignore` hide `.env` files.
- Keep agent command approval ON. Approve commands one by one; never allow `rm -rf`, force-push or database drops.
- Treat text from web pages, issues and dependencies as untrusted. Agents can be tricked by instructions hidden in them.
- Do not route code through unknown community "free LLM gateways".
- Never merge on the agent's word alone: tests, `check.sh` and your own review decide.
