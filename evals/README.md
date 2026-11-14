# evals/ — honesty + accuracy (Deep, D1-09)

- `run.py`: 40 personas from `data/personas.json` (EN + ES) over `/agent/turn`
- Claude Opus (`CLAUDE_JUDGE_MODEL`) grades every agent line for implied promises
- Output: `evals/results.json` → shown on `/system` (per-field accuracy, correction rate, implied-promise rate, latency p50/p95)
