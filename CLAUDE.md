# Claude Code project notes

## Project overview

`serviceops-portal` is a FastAPI service for internal service-request management
(FIREWALL/SSL/SFTP/SERVER_ACCESS/DNS) with JWT auth, role-based approvals, audit
logging, and a Postgres backend. A static vanilla-JS UI lives in `ui/` and is
served by `nginx:alpine`. Both run as separate Docker containers on the
`serviceops-net` user-defined network.

## Layout

- `app/` — FastAPI package. Routers in `app/api/`, ORM in `app/models/`, Pydantic
  schemas in `app/schemas/`, business logic in `app/services/`, auth helpers in
  `app/auth/`, the in-process notifications worker in `app/workers/`.
- `alembic/` — DB migrations. Source of truth for schema.
- `ui/` — Static SPA. `index.html`, `app.js`, `styles.css`, `Dockerfile`, `README.md`.
- `Dockerfile` (root) — Builds the API image (Python 3.12-slim, exposes 8000).

## Conventions

- **Auth**: JWT (HS256), 60-min default expiry. Login is form-encoded
  (`OAuth2PasswordRequestForm`), not JSON. Token revocation is in-process
  (`app/auth/blocklist.py`) — fine for single-replica deployments.
- **Roles**: `ADMIN`, `APPROVER`, `OPERATOR`, `USER`. Gated via
  `app.auth.dependencies.require_role`.
- **Audit**: every state-changing router writes an entry via
  `app.services.audit_service.record`.
- **CORS**: configured in `app/main.py` via `UI_ORIGINS` env (default `*`).
- **Migrations**: always via Alembic. Do not hand-edit DB schema; the
  `create_table.sh` script is legacy.
- **API base URL for the UI**: the browser hits the host-mapped API port
  (`http://localhost:8000`). The UI container is on the same Docker network
  (`serviceops-net`) but talks to the API from the browser, not server-side.

## Gotchas

- The `requests` router has a parameter `status: Optional[str] = Query(None)`
  that shadows the imported `status` module — cosmetic, currently works.
- `notification_worker.run_worker` runs as an asyncio task on app startup; it
  polls the `notifications` table every 30s. No external broker.
- `UserCreate` and `user_service.create_user` existed before the `/users` router
  was added — the router reuses them. The first ADMIN must be seeded
  out-of-band (see root `README.md`).
- UI uses `localStorage` for the JWT under key `serviceops_token`. Logout
  clears it but only the in-process blocklist invalidates the server-side
  token.

## Useful commands

```bash
# Run the API locally
uvicorn app.main:app --reload

# DB migrations
alembic upgrade head
alembic revision --autogenerate -m "msg"

# Rebuild + restart API container
docker build -t serviceportal:1 .
docker run -d --name serviceops-api --network serviceops-net -p 8000:8000 serviceportal:1

# Rebuild + restart UI container
docker build -t serviceops-ui:1 ./ui
docker run -d --name serviceops-ui --network serviceops-net -p 8080:80 serviceops-ui:1
```

## Where to look

- Adding a new endpoint → mirror the structure of `app/api/auth.py` (router,
  `get_db`, `require_role`, audit record).
- Adding UI screens → hash-routed, add to the route table at the bottom of
  `ui/app.js`, render with the small `el(tag, attrs, ...children)` helper.
- Changing the schema → update the SQLAlchemy model + Pydantic schema, then
  `alembic revision --autogenerate`.
