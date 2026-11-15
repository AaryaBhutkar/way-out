# Deep: progress

**Role:** resident side: voice, interpreter, honesty, calls, evals · **Task file:** [`docs/team/deep.md`](../deep.md) · **Your branch:** `feat/deep`

Update this table as you go (⬜ todo · 🟡 in progress · ✅ done · ⛔ blocked). Commit it with your work so the team
can see where you are on `develop` after each merge.

| ID | When | Task | Task branch | Status | PR |
|---|---|---|---|---|---|
| D1-01 | 11:10–12:30 | Cartesia hello-world → thin client | `feat/D1-01-cartesia-hello-world-thin-client` | ⬜ todo | |
| D1-02 | 12:30–2:30 | State machine + templates | `feat/deep` | ✅ done | |
| D1-03 | 2:30–4:00 | Interpreter + honesty | `feat/deep` | 🟡 code + tests done; needs a live Gemini/Claude key check | |
| D1-04 | 4:00–5:45 | Record → request | `feat/deep` | 🟡 backend + `/calls` page done; M1 check (real call → map) waits on D1-01 | |
| D1-05 | 6:00–8:00 | Dialer + reach ladder | `feat/deep` | ✅ stand-ins + ladder done (200 homes in ~2 min); real-phone dialing coded, untested until D1-01 | |
| D1-06 | 8:00–10:00 | Callbacks + live status | `feat/deep` | ✅ done with stand-ins; real-phone callbacks coded, untested until D1-01 | |
| D1-07 | 10:00–11:15 | TinyFish SET trigger | `feat/D1-07-tinyfish-set-trigger` | ⬜ todo | |
| D1-08 | 11:15–12:15 | Dedupe + kiosk | `feat/D1-08-dedupe-kiosk` | ⬜ todo | |
| D1-09 | 12:15–1:00 | Evals + /system | `feat/D1-09-evals-system` | ⬜ todo | |

## How to work

- `feat/deep` is your home branch, cut from `develop`. For each task you can work here, or cut a task branch
  (`feat/<ID>-<slug>`, names above) from `develop` and open a PR back into `develop`. Small PRs merge faster.
- Keep in sync: `git fetch origin && git rebase origin/develop` before you open a PR.
- Rules: [`AGENTS.md`](../../../AGENTS.md) · flow: [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) · shared shapes: [`docs/CONTRACT.md`](../../CONTRACT.md).
- Blocked more than 20 minutes → post in team chat with the task ID.

## Notes

- Try it: `uv run --project api python -m api.agent.chat -v` (no DB or keys needed).
- Contract additions (in `docs/CONTRACT.md`): a §4 line for "no request yet", the `asks_why` flag, and
  `mobility=wheelchair` / `medical=none` in interpreter output.
- Honesty guard also blocks timing words, comfort and advice at every status, not only before accept.
- A household that can leave with a car gets `role: left` (green). Tell Yash if the console wants a different role.
- Dialer (D1-05): runs inside the API. Zone at `set`/`go` → homes called earliest deadline first.
  Simulated homes are called only while `POST /sim/control {"standIns": {"voice": true}}` is on.
  Real phones need `CARTESIA_API_KEY`, `CARTESIA_AGENT_ID`, `CARTESIA_FROM_NUMBER_ID`; the Line agent gets
  `householdId` + `callId` as dynamic variables. Demo knob: `REACH_LADDER_SCALE=0.1` shortens the 2/5/3-minute waits.
- Any home without a car now gets a request (Aarya's personas expect it), not only no car + mobility limits.
- Callbacks (D1-06): `api/agent/callbacks.py` runs inside the API. Status read when the call connects, never from
  the queue, so a stale callback can't announce an old ETA. Resident already on a call → told there, no second call.
  No answer → one retry after 60 s → `unanswered`. The Line agent must pass `callType: callback` to `/agent/start`.
- Known gap: personas p29 ("I'm staying") and p31 (suspicious caller) end as `left`, not `stay`/`unknown`.
