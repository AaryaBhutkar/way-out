#!/usr/bin/env bash
# P-01 one-shot GitHub setup. Run once, from the repo root, after the first push of `main`:
#   gh auth login && ./scripts/github-setup.sh
# Creates develop + staging, branch protection (PR + green CI), environments, labels,
# and one issue per task ID in docs/team/*.md. Safe to re-run: existing items are skipped.
set -euo pipefail

REPO="${REPO:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
MAIN_SHA="$(gh api "repos/$REPO/git/ref/heads/main" -q .object.sha)"
echo "repo: $REPO  main: ${MAIN_SHA:0:7}"

for b in develop staging; do
  gh api "repos/$REPO/git/refs" -f ref="refs/heads/$b" -f sha="$MAIN_SHA" >/dev/null 2>&1 \
    && echo "created $b" || echo "$b exists"
done
gh api -X PATCH "repos/$REPO" -f default_branch=develop -F delete_branch_on_merge=true \
  -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false >/dev/null
echo "default branch → develop, squash merges only"

protect() {  # branch, required approvals
  gh api -X PUT "repos/$REPO/branches/$1/protection" --input - >/dev/null <<JSON
{
  "required_status_checks": {"strict": false, "contexts": ["api", "web"]},
  "enforce_admins": false,
  "required_pull_request_reviews": {"required_approving_review_count": $2},
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
  echo "protected $1 (PR + CI, $2 approval(s))"
}
protect develop 0
protect staging 0
protect main 1

for e in dev staging production; do
  gh api -X PUT "repos/$REPO/environments/$e" >/dev/null && echo "environment $e"
done

label() { gh label create "$1" --color "$2" --description "$3" -R "$REPO" 2>/dev/null || true; }
label contract     d93f0b "Changes docs/CONTRACT.md"
label demo-blocker b60205 "Breaks the demo"
label P0 b60205 "Must work for the demo"
label P1 fbca04 "Makes it win"
label P2 c5def5 "If time"
for who in prem deep dev-2 aarya; do label "owner:$who" 5319e7 ""; done

existing="$(gh issue list -R "$REPO" --state all --limit 500 --json title -q '.[].title')"
for f in docs/team/*.md; do
  who="$(basename "$f" .md)"
  # Rows look like: | **D1-03** | 2:30–4:00 | **Interpreter + honesty.** ... |
  grep -E '^\| \*\*[A-Z0-9]+-[0-9]+\*\* \|' "$f" | while IFS= read -r row; do
    id="$(sed -E 's/^\| \*\*([A-Z0-9]+-[0-9]+)\*\*.*/\1/' <<<"$row")"
    when="$(awk -F'|' '{gsub(/^ +| +$/,"",$3); print $3}' <<<"$row")"
    task="$(awk -F'|' '{gsub(/^ +| +$/,"",$4); print $4}' <<<"$row")"
    title_part="$(sed -E 's/^\*\*([^*]+)\*\*.*/\1/; s/\.$//' <<<"$task" | cut -c1-72 | sed -E 's/[ ,:;]+$//')"
    title="$id $title_part"
    if grep -qxF "$title" <<<"$existing"; then echo "skip $title"; continue; fi
    body="$(printf '**Owner:** %s · **When:** %s\n\n%s\n\nSee https://github.com/%s/blob/develop/%s' "$who" "$when" "$task" "$REPO" "$f")"
    gh issue create -R "$REPO" --title "$title" --body "$body" --label "owner:$who" >/dev/null
    echo "issue: $title"
  done
done
echo "done"
