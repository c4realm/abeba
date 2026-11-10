#!/usr/bin/env bash
# One command to run every quality and security gate. Agents must run this before each commit.
set -u
cd "$(dirname "$0")/.."
fail=0
step() { local name="$1"; shift; echo; echo "== $name"; "$@" || { echo "FAILED: $name"; fail=1; }; }

( cd backend
  step "ruff lint" ruff check .
  step "backend tests" python -m pytest -q
  step "bandit (security lint)" bandit -q -r apps services config -ll
  step "pip-audit (dependencies)" pip-audit -r requirements.txt --progress-spinner off
  exit $fail ) || fail=1

if command -v gitleaks >/dev/null 2>&1; then
  step "gitleaks (secrets)" gitleaks detect --no-banner --redact
else
  echo; echo "== gitleaks not installed: install it (https://github.com/gitleaks/gitleaks) to scan for secrets"
fi

if [ -f frontend/package.json ] && [ -d frontend/node_modules ]; then
  ( cd frontend
    step "eslint" npm run lint --if-present
    step "frontend build" npm run build --if-present
    step "npm audit" npm audit --audit-level=high
    exit $fail ) || fail=1
fi

echo; [ $fail -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail
