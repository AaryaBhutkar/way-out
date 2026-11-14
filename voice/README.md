# voice/ — Cartesia Line agent (Deep, D1-01)

Thin client: on every resident utterance it POSTs to `/agent/turn` and speaks back `say[]` exactly.
No prompts or call logic here; that all lives in `api/agent/`.

```bash
uv sync
cartesia auth login
cartesia deploy                       # creates / updates the agent
cartesia call +1XXXXXXXXXX <agent_id> # ring your own phone
```

Env: `PUBLIC_API_URL`, `INTERNAL_TOKEN`, `CARTESIA_API_KEY`. Use agent `wayout-dev` for dev/staging, `wayout-prod` for prod.
`client.py` is the API client; wire it into the Line SDK's custom-agent handler.
