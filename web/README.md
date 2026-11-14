# web/ — Next.js app (Vercel)

```bash
pnpm i
NEXT_PUBLIC_API_URL=http://localhost:8000 pnpm dev   # http://localhost:3000
pnpm lint && pnpm typecheck && pnpm build
```

| Path | Owner | Task |
|---|---|---|
| `/` kiosk | Deep | D1-08 |
| `/console` | Yash | D2-03 |
| `/driver` (PWA) | Yash | D2-05, D2-08 (`app/driver/safety.ts`) |
| `/calls` | Deep | D1-04 |
| `/system` | Deep | D1-09 |
| `/report` | Yash | P2 |
| `/drill` | Deep | D1-07 (plainly labeled, never styled as a county site) |

- `lib/api.ts`: REST client for CONTRACT §2.
- `lib/live.ts`: one `/live` socket → Zustand store per collection, reconnect with backoff + REST resync.
- `components/Shell.tsx`: placeholder shell and the `SimBadge`. Replace the shell per page as you build it.
- Still to add in D2-01: shadcn/ui (`pnpm dlx shadcn@latest init`), `maplibre-gl`, `deck.gl`.

Vercel: project root = `web/`. Branch domains: `dev.` ← `develop`, `staging.` ← `staging`, `app.` ← `main`.
Set `NEXT_PUBLIC_API_URL` per environment (`https://api-dev.<domain>`, `https://api-staging.<domain>`, `https://api.<domain>`).
