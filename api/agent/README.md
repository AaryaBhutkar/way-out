# api/agent/ — resident side (Deep)

| File | Task | What |
|---|---|---|
| `flow.py` | D1-02 | Call state machine: `greet → confirm_address → can_leave → household → needs → chair_kind → assistance → readback → neighbor → status/hold → goodbye` |
| `templates.py` | D1-02 | Every sentence about ride status (CONTRACT §4), en + es. The AI never writes these |
| `interpreter.py` | D1-03 | Gemini JSON (CONTRACT §5); Claude Sonnet fallback after 2.5 s |
| `honesty.py` | D1-03 | Drop acks with digits or promise language while no driver has accepted |
| `dialer.py` | D1-05 | Priority queue at SET, 1 call/s, reach ladder |
| `callbacks.py` | D1-06 | Worker: `callbacks` with `state: queued` → place call → `played` / `unanswered` |
| `dedupe.py` | D1-08 | Gemini embeddings + Atlas Vector Search + 50 m rule |
| `chat.py` | D1-02 | Text CLI: `uv run --project api python -m api.agent.chat` (from repo root) |

Use the core helpers, don't reimplement them:
- `api.requests.upsert_for_household()` to create/update a ride request
- `api.requests.transition()` for any status change (you'll rarely need it from here)
- `api.callbacks.enqueue()` is already called by accept / revoke
