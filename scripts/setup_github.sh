#!/usr/bin/env bash
# Usage: ./scripts/setup_github.sh OWNER/digital-equb   (needs: gh auth login, python3, git)
set -e
REPO=${1:?usage: setup_github.sh OWNER/repo}
[ -d .git ] || { git init -b main; git add .; git commit -m "chore: initial project scaffold"; }
gh repo create "$REPO" --public --source=. --remote=origin --push || true
for l in "BE:1d76db" "FE:0e8a16" "UI:e99695" "ALL:5319e7" "bug:d73a4a"; do gh label create "${l%%:*}" -c "${l##*:}" -R "$REPO" --force; done
python3 - "$REPO" <<'PY'
import json,subprocess,sys,datetime as d
repo=sys.argv[1]; start=d.date(2026,10,12)
def gh(*a): return subprocess.run(["gh",*a],capture_output=True,text=True)
for w in range(1,10):
    due=(start+d.timedelta(days=7*w-1)).isoformat()+"T23:59:00Z"
    gh("api",f"repos/{repo}/milestones","-f",f"title=Week {w}","-f",f"due_on={due}")
for w,s,t in json.load(open("scripts/tasks.json")):
    gh("issue","create","-R",repo,"-t",t,"-l",s,"-m",f"Week {w}","-b","Definition of done: merged via reviewed PR, tested, deployed, demoed.")
PY
echo '{"required_status_checks":{"strict":true,"contexts":["ci"]},"enforce_admins":false,"required_pull_request_reviews":{"required_approving_review_count":1},"restrictions":null}' |
 gh api -X PUT "repos/$REPO/branches/main/protection" --input - >/dev/null || echo "Branch protection needs a public repo or paid plan; set it in Settings > Branches."
echo "Done. Create a Project board (Projects > New > Board) and add all issues."
