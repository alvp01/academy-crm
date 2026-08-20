# Academy CRM — Developer & Agent Instructions

This file is the single source of truth for anyone working on this codebase — human or AI agent.
Read it before making any changes. It exists so every contributor starts with the same context.

---

## Project Overview

Multi-tenant academy management system. Each academy manages its own headquarters, classrooms, students, and classes with full tenant isolation.

**Core constraint:** Every database query MUST be scoped by `academy_id` from the JWT. Cross-academy access returns 404 (not 403 — no data leakage).

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Python, FastAPI, SQLAlchemy 2.0 (async), Alembic | 3.11+ |
| Database | PostgreSQL | 16+ |
| Frontend | React, TypeScript, Vite, Tailwind CSS | 19, 5.7, 6, 3.4 |
| State | Zustand (client), TanStack Query (server) | 5, 5 |
| Auth | JWT (access + refresh), bcrypt, CSRF double-submit | — |
| Infra | Docker Compose | 3 services |

---

## Architecture

```
Backend:  API → Services → Repositories → Database
Frontend: Pages → Domain Components → UI Primitives
```

**Backend layers:**
- `app/api/` — FastAPI routers, request/response handling
- `app/services/` — Business logic, orchestration
- `app/repositories/` — Database queries, data access
- `app/models/` — SQLAlchemy ORM models
- `app/schemas/` — Pydantic request/response schemas
- `app/core/` — Config, security, dependencies, database

**Frontend layers:**
- `src/features/{domain}/` — Domain-specific pages, components, hooks, types
- `src/components/ui/` — Atomic, domain-agnostic UI primitives
- `src/components/layout/` — Structural layout components
- `src/api/` — API client and endpoint definitions
- `src/store/` — Zustand stores (client state)

---

## Quick Start

```bash
# 1. Clone and start
git clone <repo-url> && cd academy-crm
docker compose up

# 2. Run migrations (separate terminal)
docker compose exec backend alembic upgrade head

# 3. Access
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Prerequisites:** Docker, Docker Compose, pnpm (for frontend dev outside Docker)

---

## Environment Variables

Required in `backend/.env` (or passed via Docker Compose):

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — | JWT signing key (MUST be set) |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@db:5432/academy_crm` | Database connection |
| `JWT_EXPIRY_MINUTES` | `30` | Access token lifetime |
| `REFRESH_EXPIRY_DAYS` | `7` | Refresh token lifetime |
| `FRONTEND_URL` | `http://localhost:5173` | CORS origin |
| `ENVIRONMENT` | `development` | `development` or `production` |

---

## Testing

### Backend (pytest)

```bash
cd backend && pytest -v                    # Run all tests
cd backend && pytest tests/test_auth.py    # Run specific file
cd backend && pytest -k "test_create"      # Run matching tests
```

- Tests use `pytest-asyncio` with `asyncio_mode = "auto"`
- Database is reset between tests (drop + recreate tables)
- Use `client` fixture for HTTP requests, `academy_a`/`academy_b` for auth
- Cookie-based auth: use `login_academy()` + `auth_headers()` helpers from conftest

### Frontend (TypeScript check)

```bash
cd frontend && tsc --noEmit    # Type check only
cd frontend && pnpm build     # Full build
```

---

## Coding Conventions

### Backend (Python)

| Rule | Standard |
|------|----------|
| Style | PEP 8, 88-char line length |
| Type hints | Required on all functions |
| Async | Use `async/await` everywhere (no blocking calls) |
| DB sessions | Never create sessions manually — use `Depends(get_db)` |
| Tenant isolation | Always filter by `academy_id` — never skip |
| Errors | HTTPException with appropriate status codes |
| Schemas | Pydantic v2 with `model_config` for settings |
| IDs | UUID primary keys on all entities |
| Migrations | Alembic — never modify migration files after push |

**Naming:**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Frontend (TypeScript/React)

| Rule | Standard |
|------|----------|
| Components | Functional only, named exports |
| Props | Interface + discriminated unions (no boolean props) |
| Imports | `@/` alias — never relative for shared code |
| State | Zustand for client, TanStack Query for server |
| Styling | Tailwind CSS — no inline styles, no CSS modules |
| Forms | React Hook Form |
| Routing | React Router v7 |

**Naming:**
- Components: `PascalCase.tsx`
- Hooks: `use{Domain}.ts`
- Types: `types.ts`
- Barrel exports: `index.ts`

### Git

- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
- One logical change per commit
- No AI attribution in commits
- Branch naming: `feat/`, `fix/`, `chore/` prefixes

---

## Tenant Isolation Protocol (CRITICAL)

This is the most important architectural constraint. Violations are bugs.

1. **Every new endpoint** must extract `academy_id` from JWT via `Depends(get_current_academy)`
2. **Every new repository method** must accept `academy_id` as first parameter
3. **Every new query** must filter by `academy_id`
4. **Cross-academy access returns 404** — never 403 (avoids leaking entity existence)
5. **Tests must verify isolation** — access academy B's resources with academy A's token

---

## Adding a New Feature

### Backend

1. Define model in `app/models/{entity}.py`
2. Create migration: `alembic revision --autogenerate -m "add {entity}"`
3. Add schema in `app/schemas/{entity}.py`
4. Implement repository in `app/repositories/{entity}.py`
5. Implement service in `app/services/{entity}.py`
6. Add router in `app/api/{entity}.py`
7. Register router in `app/main.py`
8. Write tests in `tests/test_{entity}.py`

### Frontend

1. Create feature folder: `src/features/{domain}/`
2. Define types in `types.ts`
3. Create API hooks in `use{Domain}.ts`
4. Build domain components
5. Create page component `{Domain}Page.tsx`
6. Add barrel export `index.ts`
7. Register route in `App.tsx`

---

## Common Pitfalls

| Mistake | Why it's wrong | Fix |
|---------|---------------|-----|
| Query without `academy_id` | Tenant isolation breach | Add `.where(Model.academy_id == academy.id)` |
| Blocking I/O in async | Event loop starvation | Use `await` or `run_in_executor` |
| Relative imports | Fragile paths | Use `@/` alias |
| Boolean props | Hard to extend | Use discriminated unions |
| Manual DB sessions | Leaks, no transaction mgmt | Use `Depends(get_db)` |
| Modifying migrations | History rewrite, merge conflicts | Create new migration |

---

## File Structure Reference

```
academy-crm/
├── AGENTS.md                          # You are here
├── README.md                          # Project overview + API docs
├── DESIGN_BRIEF.md                    # Architecture + roadmap
├── docker-compose.yml                 # 3-service local dev
├── backend/
│   ├── app/
│   │   ├── api/                       # FastAPI routers
│   │   ├── core/                      # Config, security, deps, database
│   │   ├── models/                    # SQLAlchemy models
│   │   ├── repositories/              # Data access layer
│   │   ├── schemas/                   # Pydantic schemas
│   │   ├── services/                  # Business logic
│   │   └── main.py                    # App entry point
│   ├── alembic/                       # Database migrations
│   ├── tests/                         # pytest tests
│   └── pyproject.toml                 # Dependencies + config
├── frontend/
│   ├── src/
│   │   ├── api/                       # API client
│   │   ├── components/                # UI primitives + layout
│   │   │   ├── ui/                    # Atomic components
│   │   │   └── layout/               # Structural components
│   │   ├── features/                  # Domain-specific code
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   └── students/
│   │   ├── store/                     # Zustand stores
│   │   └── App.tsx                    # Route definitions
│   ├── COMPONENT-GUIDELINES.md        # Component creation rules
│   └── package.json                   # Dependencies + scripts
└── openspec/                          # SDD artifacts (if using spec-driven)
```

---

*Last updated: August 2026*
