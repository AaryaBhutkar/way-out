# infra/ — Vultr VM + Caddy + three API environments (P-04)

## One-time VM setup (Ubuntu 24.04)

```bash
curl -fsSL https://get.docker.com | sh
sudo mkdir -p /opt/wayout && sudo chown $USER /opt/wayout
cd /opt/wayout
cat > .env <<'X'
DOMAIN=<your-domain>
API_IMAGE=ghcr.io/yash-charde/wayout-api
X
# one secrets file per env, copied from .env.example (ENV is set by compose)
nano dev.env staging.env prod.env
```

DNS: A records `api-dev`, `api-staging`, `api` → VM IP. Caddy gets the certificates.

## GitHub Environments (`dev`, `staging`, `production`)

Secrets in each: `VULTR_HOST`, `VULTR_USER`, `VULTR_SSH_KEY` (private key whose public half is in the VM's `authorized_keys`).
The deploy job logs the VM into GHCR with the workflow's token, so the image can stay private.

## Deploy / rollback

Merging to `develop` / `staging` / `main` deploys `api-dev` / `api-staging` / `api-prod`.
Rollback: Actions → **deploy** → Run workflow → pick env + an older image tag (a git sha).

Check: `curl https://api-dev.<domain>/health` → `{"ok":true,"env":"dev","gitSha":"..."}`
