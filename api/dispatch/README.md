# api/dispatch/ — solver (Dev 2)

| File | Task | What |
|---|---|---|
| `greedy.py` | D2-04 | Earliest-deadline-first, capacity/crew/lift compatible, insert after last accepted stop |
| `ortools.py` | D2-09 (P1) | Pickup-and-delivery VRP with time windows, 3 s limit, warm start from greedy |
| `loop.py` | D2-04 | Re-plan every 5 s while open, 30 s otherwise, immediately on closure. Start it from `api/workers.py` |
| `doors.py` | — | Door-knock priority score |

Write `plans` + `proposed` assignments only. Approve/accept/revoke go through `api/assignments.py`.
Accepted stops are frozen; to drop one that can no longer be reached, call `api.assignments.revoke()`.
