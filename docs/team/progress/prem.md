# Prem: progress

**Role:** foundation, infra, coordination · **Task file:** [`docs/team/prem.md`](../prem.md) · **Your branch:** `feat/prem`

Update this table as you go (⬜ todo · 🟡 in progress · ✅ done · ⛔ blocked). Commit it with your work so the team
can see where you are on `develop` after each merge.

| ID | When | Task | Task branch | Status | PR |
|---|---|---|---|---|---|
| P-01 | 11:10–11:30 | Create repo `wayout`, push all docs, create `develop` + `staging`… | `feat/P-01-create-repo-wayout-push-all-docs` | ✅ done (Yash): repo public, 3 branches, 41 issues, labels; setup script ran | |
| P-02 | 11:30–12:15 | API skeleton | `feat/P-02-api-skeleton` | ✅ done (v0.0) | |
| P-03 | 12:15–1:15 | Core rules | `feat/P-03-core-rules` | ✅ done (v0.0) + follow-ups on `feat/P-03-contract-followups`: `/assignments/{id}/progress`, en_route ETA callbacks, `/requests/{id}/close` (94 tests, green on a real Mongo replica set) | to open |
| P-04 | 1:15–1:50 | Three environments | `feat/P-04-deploy-fixes` | 🟡 code ready (fixed lowercase GHCR image bug, VM bootstrap, smoke + release scripts). ⛔ needs accounts: Atlas, Vultr VM, DNS, 3 repo secrets, Vercel (checklist in `infra/README.md`) | to open |
| P-05 | 1:50–2:00 | Handoff | `feat/P-05-handoff` | 🟡 `docs/team/handoff.md` done, open questions answered; tag `v0.0` after first deploy | |
| P-10 | 1:00–1:45 | Pull `develop`. Run the **full demo flow on staging** end to end with… | `feat/P-10-pull-develop-run-the-full-demo-f` | ⬜ todo | |
| P-11 | 1:45–4:30 | Bug-bash lead: triage, review and merge `fix/*` PRs, keep `develop`… | `feat/P-11-bug-bash-lead-triage-review-and` | ⬜ todo | |
| P-12 | 4:30–5:00 | Release `v1.0` | `feat/P-12-release-v1-0` | ⬜ todo | |
| P-13 | 5:00–8:30 | Rehearse the 3-minute demo ×3 with Aarya (you or Yash plays the… | `feat/P-13-rehearse-the-3-minute-demo-3-wit` | ⬜ todo | |
| P-14 | 8:30–10:30 | Devpost with Aarya: links (live app, repo, video), team, "built… | `feat/P-14-devpost-with-aarya-links-live-ap` | ⬜ todo | |
| P-15 | 12:00–2:00 PM | Expo: run the console. Check `/health` on prod before every judge… | `feat/P-15-expo-run-the-console-check-healt` | ⬜ todo | |

## How to work

- `feat/prem` is your home branch, cut from `develop`. For each task you can work here, or cut a task branch
  (`feat/<ID>-<slug>`, names above) from `develop` and open a PR back into `develop`. Small PRs merge faster.
- Keep in sync: `git fetch origin && git rebase origin/develop` before you open a PR.
- Rules: [`AGENTS.md`](../../../AGENTS.md) · flow: [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) · shared shapes: [`docs/CONTRACT.md`](../../CONTRACT.md).
- Blocked more than 20 minutes → post in team chat with the task ID.

## Notes

- **2:55 PM Sat:** Claude can read but not push (`403`). Yash: install the Claude GitHub App on the repo
  (https://github.com/apps/claude/installations/select_target) so these branches can be pushed directly.
- New core endpoints for teammates: `POST /assignments/{id}/progress` (Yash, D2-05 driver app + stand-in drivers),
  `POST /requests/{id}/close` (Deep, when a resident says they already left; dedupe). See `docs/team/handoff.md`.
- `scripts/smoke.py --domain <d>` checks all three envs; `--flow` drives one ride end to end (P-10).
  `scripts/release.sh v1.0 <d>` is P-12.
- Repo is squash-merge only and `main` needs 1 approval: Yash approves the `staging → main` PR.
