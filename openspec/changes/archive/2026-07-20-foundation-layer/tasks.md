# Tasks: Foundation Layer

## Phase 1: Project Init & Infrastructure

- [x] 1.1 Create `/backend/pyproject.toml` with dependencies: fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, pydantic, python-jose, passlib[bcrypt], alembic, httpx, pytest, pytest-asyncio
- [x] 1.2 Create `/backend/app/__init__.py` (empty)
- [x] 1.3 Create `/backend/app/core/__init__.py` and `config.py` — Pydantic Settings: SECRET_KEY, DATABASE_URL, JWT_EXPIRY_MINUTES, REFRESH_EXPIRY_DAYS
- [x] 1.4 Create `/backend/app/core/database.py` — async engine, AsyncSession factory, Base declarative
- [x] 1.5 Create `/backend/app/models/academy.py` — Academy model: id (UUID PK), name, email (unique), identification_number (unique), password_hash, created_at, updated_at
- [x] 1.6 Create `/backend/app/models/headquarters.py` — Headquarters model: id (UUID PK), academy_id (FK), name; UniqueConstraint(academy_id, name)
- [x] 1.7 Create `/backend/app/models/classroom.py` — Classroom model: id (UUID PK), headquarters_id (FK), name, classes_capacity (int); UniqueConstraint(headquarters_id, name)
- [x] 1.8 Create `/backend/app/models/__init__.py` importing all models for Alembic auto-discovery
- [x] 1.9 Create `/backend/alembic.ini` pointing to async driver (asyncpg)
- [x] 1.10 Create `/backend/alembic/env.py` — async migration env, import Base.metadata
- [x] 1.11 Run `alembic revision --autogenerate -m "initial tables"` and `alembic upgrade head`
- [x] 1.12 Create `/backend/Dockerfile` — Python 3.11-slim, install deps, uvicorn with --reload
- [x] 1.13 Create `/docker-compose.yml` — services: db (postgres:16-alpine), backend, frontend; volumes for db; health checks
- [x] 1.14 Create `/frontend/package.json` — pnpm, vite, react, typescript, tailwindcss, zustand, @tanstack/react-query, axios
- [x] 1.15 Create `/frontend/Dockerfile` — Node 20-alpine, pnpm install, vite dev server

## Phase 2: Auth & Tenant Isolation

- [x] 2.1 Create `/backend/app/core/security.py` — hash_password(), verify_password(), create_access_token(), create_refresh_token(), decode_token()
- [x] 2.2 Create `/backend/app/core/deps.py` — get_db() async generator, get_current_academy() dependency (JWT decode → Academy)
- [x] 2.3 Create `/backend/app/schemas/auth.py` — RegisterRequest, LoginRequest, TokenResponse, AcademyResponse
- [x] 2.4 Create `/backend/app/repositories/academy.py` — create(), get_by_email(), get_by_id()
- [x] 2.5 Create `/backend/app/services/auth.py` — register_academy(), login_academy(), refresh_token()
- [x] 2.6 Create `/backend/app/api/auth.py` — POST /api/auth/register, POST /api/auth/login, POST /api/auth/refresh
- [x] 2.7 Create `/backend/app/main.py` — FastAPI app, CORS middleware, mount auth router
- [x] 2.8 Create `/backend/tests/conftest.py` — async test client, test DB session, 2 academy fixtures
- [x] 2.9 Create `/backend/tests/test_auth.py` — RED: register success, duplicate email 409, login success, login wrong password 401, refresh token success, refresh expired 401
- [x] 2.10 GREEN: verify all auth tests pass
- [x] 2.11 Create `/backend/tests/test_isolation.py` — RED: academy A creates resource, academy B attempts read → 404/403; verify academy A's data unaffected

## Phase 3: Headquarters CRUD

- [x] 3.1 Create `/backend/app/schemas/headquarters.py` — HQCreate, HQUpdate, HQResponse, PaginatedHQResponse
- [x] 3.2 Create `/backend/app/repositories/headquarters.py` — create(), get_by_id(academy_id), list(academy_id, page, size), update(), delete()
- [x] 3.3 Create `/backend/app/services/headquarters.py` — create_hq(), get_hq(), list_hqs(), update_hq(), delete_hq(); enforce name uniqueness per academy
- [x] 3.4 Create `/backend/app/api/headquarters.py` — full CRUD endpoints, all scoped by get_current_academy dependency
- [x] 3.5 Mount headquarters router in `/backend/app/main.py`
- [x] 3.6 Create `/backend/tests/test_headquarters.py` — RED: create success, list scoped, get by id scoped, update, delete, duplicate name 409, cross-academy get → 404, cross-academy update → 404, cross-academy delete → 404
- [x] 3.7 GREEN: verify all headquarters tests pass

## Phase 4: Classroom CRUD

- [x] 4.1 Create `/backend/app/schemas/classroom.py` — ClassroomCreate, ClassroomUpdate, ClassroomResponse, PaginatedClassroomResponse
- [x] 4.2 Create `/backend/app/repositories/classroom.py` — create(), get_by_id(headquarters_id), list(headquarters_id, page, size), update(), delete()
- [x] 4.3 Create `/backend/app/services/classroom.py` — create_classroom(), get_classroom(), list_classrooms(), update_classroom(), delete_classroom(); enforce name uniqueness per headquarters + capacity validation
- [x] 4.4 Create `/backend/app/api/classroom.py` — full CRUD endpoints, all scoped by get_current_academy dependency
- [x] 4.5 Mount classroom router in `/backend/app/main.py`
- [x] 4.6 Create `/backend/tests/test_classroom.py` — RED: create success, list scoped, get by id scoped, update, delete, duplicate name 409, capacity validation error, cross-academy get → 404, cross-academy update → 404, cross-academy delete → 404
- [x] 4.7 GREEN: verify all classroom tests pass
- [x] 4.8 Run full isolation test suite: `pytest tests/test_isolation.py -v`

## Phase 5: Frontend

- [x] 5.1 Initialize Vite React TypeScript project in `/frontend`, install all dependencies
- [x] 5.2 Configure Tailwind CSS in `/frontend/tailwind.config.js`
- [x] 5.3 Create `/frontend/src/store/auth.ts` — Zustand store: tokens, user, login(), logout(), isAuthenticated
- [x] 5.4 Create `/frontend/src/api/client.ts` — Axios instance with base URL, token interceptor, refresh logic
- [x] 5.5 Create `/frontend/src/components/ProtectedRoute.tsx` — redirect to /login if not authenticated
- [x] 5.6 Create `/frontend/src/features/auth/Login.tsx` — email/password form, calls login API, stores tokens
- [x] 5.7 Create `/frontend/src/features/auth/Register.tsx` — name/email/identification/password form, calls register API
- [x] 5.8 Create `/frontend/src/components/Layout.tsx` — app shell with header and logout button
- [x] 5.9 Create `/frontend/src/App.tsx` — React Router: /login, /register, /protected (guarded)
- [x] 5.10 Create `/frontend/src/main.tsx` — entry point with QueryClientProvider and Router

## Phase 6: Documentation & Cleanup

- [x] 6.1 Create `/README.md` — project overview, prerequisites (Docker, pnpm), setup instructions (docker compose up), API docs summary
- [ ] 6.2 Verify `docker compose up` starts all 3 services with health checks
- [ ] 6.3 Run full test suite: `cd /backend && pytest -v`
- [ ] 6.4 Final smoke test: register via API, login, create HQ, create classroom, verify all responses match design contracts
