# Academy CRM

Multi-tenant academy management system. Each academy manages its own headquarters and classrooms with full tenant isolation.

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 16, Alembic
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Zustand, TanStack Query
- **Infrastructure**: Docker Compose (3 services: frontend, backend, db)

## Prerequisites

- Docker & Docker Compose
- pnpm (for frontend development outside Docker)

## Quick Start

```bash
# Start all services
docker compose up

# Run database migrations (in a separate terminal)
docker compose exec backend alembic upgrade head
```

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Development

### Backend

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
pytest -v
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new academy |
| POST | `/api/auth/login` | Login and get tokens |
| POST | `/api/auth/refresh` | Refresh access token |

### Headquarters (scoped by academy)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/headquarters` | List headquarters (paginated) |
| POST | `/api/headquarters` | Create headquarters |
| GET | `/api/headquarters/{id}` | Get headquarters by ID |
| PUT | `/api/headquarters/{id}` | Update headquarters |
| DELETE | `/api/headquarters/{id}` | Delete headquarters |

### Classrooms (scoped by academy)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/classrooms` | List classrooms (paginated) |
| POST | `/api/classrooms` | Create classroom |
| GET | `/api/classrooms/{id}` | Get classroom by ID |
| PUT | `/api/classrooms/{id}` | Update classroom |
| DELETE | `/api/classrooms/{id}` | Delete classroom |

## Tenant Isolation

Every database query is scoped by `academy_id`. Cross-academy access returns 404 (not leaked). JWT tokens carry the academy ID and are validated on every request.
