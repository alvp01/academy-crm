# Academy CRM — Design Brief

**Multi-tenant academy management system — Full-stack architecture overview & roadmap**

---

## 🛠 Tech Stack

**Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 16, Alembic  
**Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Zustand, TanStack Query  
**Infra:** Docker Compose (3 services)  
**Auth:** JWT access + refresh tokens, bcrypt, tenant isolation via `academy_id`

---

## 🗄 Database Schema (Implemented)

### Academy (tenant root)
- `id` UUID PK · `name` · `email` (unique) · `identification_number` (unique) · `password_hash`

### Headquarters (per academy)
- `id` UUID PK · `academy_id` FK → academies.id · `name` (unique per academy)

### Classroom (per headquarters)
- `id` UUID PK · `headquarters_id` FK → headquarters.id · `name` · `classes_capacity`

### Refresh Tokens (auth)
- `id` UUID PK · `academy_id` FK → academies.id (CASCADE)
- `token_hash` · `jti` (unique) · `expires_at` · `revoked_at`
- `user_agent` · `ip_address` · `created_at`
- **Indexes:** `(academy_id, jti)` unique · `expires_at`

> 🔐 **Tenant Isolation:** Every query scoped by `academy_id` from JWT. Cross-academy access returns **404** (not 403 — no data leakage).

---

## ✅ Implemented Features (Foundation Layer)

### Docker Foundation
- `docker-compose.yml`: frontend (5173), backend (8000), postgres (5432)
- Multi-stage Dockerfiles with dev/prod targets
- Health checks & dependency ordering

### Academy Authentication
- **Register:** `POST /api/auth/register` (create academy + first admin)
- **Login:** `POST /api/auth/login` → access + refresh tokens
- **Refresh:** `POST /api/auth/refresh` (rotation + reuse detection)
- **Logout:** `POST /api/auth/logout` (idempotent revocation)
- **JWT:** RS256, 15min access / 30d refresh, `academy_id` in claims

### Headquarters CRUD (tenant-scoped)
- `GET/POST /api/headquarters` · `GET/PUT/DELETE /api/headquarters/{id}`
- Pagination, unique name per academy

### Classroom CRUD (tenant-scoped)
- `GET/POST /api/classrooms` · `GET/PUT/DELETE /api/classrooms/{id}`
- Linked to headquarters, capacity tracking

### Tenant Isolation (enforced at DB + API layer)
- Middleware extracts `academy_id` from JWT
- All repositories filter by `academy_id` automatically
- 404 on cross-tenant access (no info leak)

> **Archived:** Foundation Layer (2026-07-20) + Refresh Token Table (2026-07-20)

---

## 🚀 Next Features (from Database Specs — Not Yet Implemented)

### Phase 1: Instructor Management
- Instructor CRUD (belongs to academy)
- Fields: `name`, `email` (unique), `identification_number` (unique), `phone`, `address`, `date_of_birth`

### Phase 2: Student Management
- Student CRUD (belongs to academy)
- Fields: `name`, `email` (unique), `identification_number` (unique), `phone`, `address`, `date_of_birth`, `allergies`, `referral_source`, `occupation`

### Phase 3: Schedule & Classes
- **Schedule CRUD** (per headquarters): `headquarters_id`, `name`, `start_time`, `end_time`
- **Class CRUD** (per classroom + instructor + schedule): `classroom_id`, `instructor_id`, `schedule_id`, `name`, `start_date`, `quota`
- **ClassInscription** (many-to-many Class ↔ Student): `class_id`, `student_id`, `inscription_date`, `graduation_date`, `role` (leader/follower)

### Architecture Impact
- New repositories, services, API routers per domain
- Tenant isolation extends to all new entities
- **Cascading deletes:** academy → HQ → classroom → schedule → class → inscription
- Instructor/Student unique constraints per academy

### Relationship Chain
```
Academy → HQ → Classroom → Class → Inscription ← Student
                  ↳ Schedule
                  ↳ Instructor
```

---

## 📡 Current API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register academy |
| POST | `/api/auth/login` | Get tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Revoke refresh token (204) |

### Headquarters (scoped by academy)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/headquarters` | List (paginated) |
| POST | `/api/headquarters` | Create |
| GET | `/api/headquarters/{id}` | Get by ID |
| PUT | `/api/headquarters/{id}` | Update |
| DELETE | `/api/headquarters/{id}` | Delete |

### Classrooms (scoped by academy)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/classrooms` | List (paginated) |
| POST | `/api/classrooms` | Create |
| GET | `/api/classrooms/{id}` | Get by ID |
| PUT | `/api/classrooms/{id}` | Update |
| DELETE | `/api/classrooms/{id}` | Delete |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | `{status, database}` |

---

## 🏗️ Architecture Notes

**Layered:** API → Services → Repositories  
**Tenant isolation:** JWT `academy_id` + DB-scoped queries  
**Refresh tokens:** Rotation with reuse detection  
**Migrations:** Alembic versioned (v001, v002)  
**Local dev:** Docker Compose

---

*Generated from OpenPencil design canvas · Academy CRM project*