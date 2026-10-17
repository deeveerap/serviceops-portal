# ServiceOps Portal

A small FastAPI backend for managing internal service requests (firewall, SSL, SFTP,
server access, DNS) with role-based approval flow, audit logging, and a notifications
worker — plus a lightweight static-JS UI for the same.

## Stack

- **API**: FastAPI 0.115, SQLAlchemy 2, Pydantic 2, JWT auth (HS256)
- **DB**: PostgreSQL
- **Migrations**: Alembic
- **UI**: vanilla HTML/CSS/JS served by `nginx:alpine`
- **Container**: Docker, single user-defined network `serviceops-net`

## Layout

```
serviceops-portal/
├── app/                # FastAPI application
│   ├── api/            # Routers (auth, requests, approvals, dashboard, users, health)
│   ├── auth/           # JWT, bcrypt, dependencies
│   ├── models/         # SQLAlchemy ORM
│   ├── schemas/        # Pydantic models
│   ├── services/       # Business logic
│   ├── workers/        # In-process notification worker
│   └── main.py
├── alembic/            # DB migrations (canonical schema source)
├── ui/                 # Static SPA (no build step)
└── Dockerfile          # API image
```

## Endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/health` | none | Liveness |
| GET | `/ready` | none | DB ping |
| GET | `/metrics` | none | Prometheus |
| POST | `/login` | form | OAuth2 form-encoded → JWT |
| POST | `/logout` | Bearer | Revokes token |
| GET | `/me` | Bearer | Current user |
| GET/POST | `/requests` | Bearer | List / create |
| GET/PUT/DELETE | `/requests/{id}` | Bearer | Detail / update / delete (delete: ADMIN/OPERATOR) |
| POST | `/requests/{id}/approve` | ADMIN/APPROVER | |
| POST | `/requests/{id}/reject` | ADMIN/APPROVER | |
| GET | `/dashboard` | Bearer | Counts + by-type breakdown |
| GET/POST/DELETE | `/users` | ADMIN | List / create / delete (self-delete blocked) |

Roles: `ADMIN`, `APPROVER`, `OPERATOR`, `USER`.

## Configuration

Environment (also read from `.env`):

| Var | Default | Notes |
|---|---|---|
| `POSTGRES_HOST` | `postgres` | Docker DNS name on `serviceops-net` |
| `POSTGRES_PORT` | `5432` | |
| `POSTGRES_USER` | `serviceops` | |
| `POSTGRES_PASSWORD` | `serviceops` | |
| `POSTGRES_DB` | `serviceops` | |
| `JWT_SECRET` | `change-me-in-production` | **Override in production** |
| `JWT_ALGORITHM` | `HS256` | |
| `JWT_EXPIRE_MINUTES` | `60` | |
| `ENABLE_REDIS` | `false` | Reserved; not currently used |
| `UI_ORIGINS` | `*` | Comma-separated CORS origins for the UI |

## Run the stack

1. **Create the network** (once):
   ```bash
   docker network create serviceops-net
   ```

2. **Start Postgres**:
   ```bash
   docker run -d --name serviceops-postgres \
     --network serviceops-net \
     -e POSTGRES_USER=serviceops \
     -e POSTGRES_PASSWORD=serviceops \
     -e POSTGRES_DB=serviceops \
     -p 5432:5432 \
     postgres:latest
   ```

3. **Build and start the API**:
   ```bash
   docker build -t serviceportal:1 .
   docker run -d --name serviceops-api \
     --network serviceops-net \
     -p 8000:8000 \
     -e JWT_SECRET=change-me \
     -e UI_ORIGINS=http://localhost:8080 \
     serviceportal:1
   ```

4. **Apply migrations** (from the repo, against the running container):
   ```bash
   docker exec -it serviceops-api alembic upgrade head
   ```

5. **Build and start the UI**:
   ```bash
   docker build -t serviceops-ui:1 ./ui
   docker run -d --name serviceops-ui \
     --network serviceops-net \
     -p 8080:80 \
     serviceops-ui:1
   ```

## Seed the first admin

The `POST /users` endpoint requires an existing ADMIN, so the first user must be
created out-of-band. Two options:

**Option A — one-off Python inside the API container**:
```bash
docker exec -it serviceops-api python -c "
from app.database import SessionLocal
from app.schemas.user import UserCreate
from app.services.user_service import create_user
db = SessionLocal()
create_user(db, UserCreate(username='admin', password='admin', role='ADMIN'))
"
```

**Option B — psql with a precomputed bcrypt hash**.

After the admin exists, log in at `http://localhost:8080` and use the Users page to
create more accounts.

## Development

Run the API locally (outside Docker) for fast iteration:
```bash
pip install -r requirements.txt
export POSTGRES_HOST=localhost
alembic upgrade head
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for the interactive API docs.

The UI is plain static files — `cd ui && python -m http.server 8080` works for local
dev, but remember to point `API_BASE` (top of `app.js`) at `http://localhost:8000`.

## Migrations

Alembic is the schema source of truth. After changing a model:
```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

The `create_table.sh` script is a legacy raw-SQL bootstrap; prefer Alembic.

## See also

- `ui/README.md` — UI-specific build and run details.
