# Tasks: Refresh Token Table

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 350–400 |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (Foundation) → PR 2 (Service + Tests) |
| Delivery strategy | feature-branch-chain |
| Chain strategy | feature-branch-chain |

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Model, schemas, repository, security helpers, migration | PR 1 | `pytest backend/tests/test_refresh_token_repo.py -x --tb=short` | N/A — foundation layer has no runtime harness, validated by unit tests in Unit 2 | `backend/app/models/refresh_token.py`, `backend/app/repositories/refresh_token.py`, `backend/app/schemas/refresh_token.py`, `backend/app/core/security.py` additions, migration file |
| 2 | AuthService rewrite, API endpoints, all tests | PR 2 | `pytest backend/tests/test_auth.py backend/tests/test_refresh_token*.py -x --tb=short` | `POST /login` → `POST /refresh` → `POST /logout` via TestClient | `backend/app/services/auth.py`, `backend/app/api/auth.py`, test files |

## Phase 1: Foundation / Infrastructure

- [x] 1.1 Add `hash_token(token: str) -> str` and `verify_token(token: str, token_hash: str) -> bool` to `backend/app/core/security.py` using SHA-256 hex digest
- [x] 1.2 Create `RefreshToken` model in `backend/app/models/refresh_token.py` — fields: id (UUID PK), academy_id (FK → academies.id, CASCADE), token_hash, jti (unique), expires_at, revoked_at (nullable), user_agent (nullable), ip_address (nullable), created_at. Composite index on (academy_id, jti), index on expires_at
- [x] 1.3 Add `RefreshToken` to `backend/app/models/__init__.py` exports
- [x] 1.4 Create `RefreshTokenCreate` and `RefreshTokenRead` schemas in `backend/app/schemas/refresh_token.py`

## Phase 2: Repository + Migration

- [x] 2.1 Create `RefreshTokenRepository` in `backend/app/repositories/refresh_token.py` — methods: `create(academy_id, token, expires_at, jti, user_agent, ip)`, `get_by_jti(jti, academy_id)`, `revoke(jti, academy_id)`, `revoke_all_for_academy(academy_id)`, `cleanup_expired()`
- [x] 2.2 Create Alembic migration `backend/alembic/versions/002_add_refresh_tokens.py` — CREATE TABLE with indexes, FK to academies.id ON DELETE CASCADE

## Phase 3: Service Rewrite

- [ ] 3.1 Inject `RefreshTokenRepository` into `AuthService.__init__()` in `backend/app/services/auth.py`, keep `_revoked_refresh_tokens` as fallback
- [ ] 3.2 Update `AuthService.login()` — after creating tokens, call `RefreshTokenRepository.create()` to persist the refresh token
- [ ] 3.3 Rewrite `AuthService.refresh()` — replace in-memory set check with `repo.get_by_jti()`, add reuse detection (revoked row → `repo.revoke_all_for_academy()` + 401), rotate via revoke old + create new
- [ ] 3.4 Add `AuthService.logout(refresh_token)` — decode, extract jti/academy_id, call `repo.revoke()`

## Phase 4: API Layer

- [ ] 4.1 Add `POST /api/auth/logout` endpoint in `backend/app/api/auth.py` — accepts `RefreshRequest` body, calls `AuthService.logout()`
- [ ] 4.2 Verify `POST /api/auth/refresh` still works with DB rotation (schema already exists in `backend/app/schemas/auth.py`)

## Phase 5: Testing

- [x] 5.1 Unit tests for `hash_token` / `verify_token` — deterministic SHA-256, wrong token returns False
- [x] 5.2 Unit tests for `RefreshTokenRepository` — mock AsyncSession, verify create/get_by_jti/revoke/revoke_all_for_academy/cleanup_expired SQL calls
- [ ] 5.3 Unit tests for `AuthService` rotation — mock repo, verify revoke → create sequence on refresh
- [ ] 5.4 RED: Token reuse detection test — login, refresh (old token revoked), attempt refresh with old token → 401 + all academy tokens revoked
- [ ] 5.5 RED: Cross-academy isolation test — token from academy A rejected when academy_id mismatch
- [ ] 5.6 Integration test: full login → refresh → logout flow via TestClient + real DB
- [ ] 5.7 Verify existing `test_auth.py` tests still pass (no regressions)

## Phase 6: Documentation

- [ ] 6.1 Update backend README with `POST /api/auth/logout` endpoint docs
