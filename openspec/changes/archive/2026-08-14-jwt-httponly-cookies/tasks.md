# Tasks: JWT HttpOnly Cookies

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 350–450 |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Backend foundation: config + cookie helpers + CSRF validation + Bearer fallback in deps | PR 1 | `cd backend && pytest tests/test_security_helpers.py tests/test_deps_cookie.py` | N/A — unit tests only | `config.py`, `security.py`, `deps.py` (no behavior change to existing endpoints) |
| 2 | Backend auth endpoints: cookies on login/register/refresh/logout + /me + test fixtures | PR 2 | `cd backend && pytest -v` | Full integration — login → /me → refresh → logout flow | `auth.py`, `services/auth.py`, `conftest.py`, `schemas/auth.py` |
| 3 | Frontend migration: remove tokens from store/client, update Login/Register components | PR 3 | `cd frontend && tsc --noEmit` | Browser auth flow — login → navigate → refresh → logout | `store/auth.ts`, `api/client.ts`, `Login.tsx`, `Register.tsx` |

## Phase 1: Foundation (Backend Config + Cookie Helpers + CSRF)

- [x] 1.1 RED: Write failing test `backend/tests/test_security_helpers.py` — `test_generate_csrf_token_returns_32_char_hex`, `test_set_auth_cookies_sets_three_cookies`, `test_clear_auth_cookies_sets_max_age_zero`, `test_dev_mode_cookies_lack_secure_flag`, `test_prod_mode_cookies_have_secure_flag` (~30 lines)
- [x] 1.2 GREEN: Add `generate_csrf_token()` → `secrets.token_hex(16)`, `set_auth_cookies(response, access_token, refresh_token, csrf_token, environment)`, `clear_auth_cookies(response)` to `backend/app/core/security.py` (~50 lines)
- [x] 1.3 Add `ENVIRONMENT: str = "development"` to `backend/app/core/config.py` (~3 lines)
- [x] 1.4 RED: Write failing test `backend/tests/test_deps_cookie.py` — `test_get_token_from_cookie`, `test_fallback_to_bearer_header`, `test_no_token_returns_401`, `test_csrf_valid_on_matching_header`, `test_csrf_rejects_mismatched_header`, `test_csrf_rejects_missing_header`, `test_csrf_bypasses_on_get` (~35 lines)
- [x] 1.5 GREEN: Replace `OAuth2PasswordBearer` with cookie-first extraction + Bearer fallback in `backend/app/core/deps.py`; add `validate_csrf()` dependency (~30 lines)
- [x] 1.6 Run `cd backend && pytest tests/test_security_helpers.py tests/test_deps_cookie.py` — all GREEN

## Phase 2: Backend Auth Endpoints (Cookies + /me)

- [x] 2.1 RED: Write failing test `backend/tests/test_auth_cookies.py` — `test_login_sets_three_cookies`, `test_login_response_has_no_token_fields`, `test_register_sets_three_cookies`, `test_refresh_rotates_cookies_from_cookie`, `test_logout_clears_three_cookies`, `test_me_returns_user_from_cookie`, `test_me_401_without_cookie` (~45 lines)
- [x] 2.2 Modify `backend/app/services/auth.py` — `login()` returns `(Academy, access_token, refresh_token, csrf_token)` instead of `TokenResponse`; `register()` returns tuple with tokens; `refresh()` reads token from cookie param; `logout()` reads from cookie param (~40 lines)
- [x] 2.3 Modify `backend/app/api/auth.py` — login/register/refresh endpoints call `set_auth_cookies()` on response; logout calls `clear_auth_cookies()`; change response_model to `AcademyResponse` where applicable; add `POST /api/auth/me` endpoint (~40 lines)
- [x] 2.4 Remove `TokenResponse` and `RefreshRequest` from `backend/app/schemas/auth.py` (~-12 lines)
- [x] 2.5 Update `backend/tests/conftest.py` — `login_academy()` extracts tokens from `Set-Cookie` headers; add `get_auth_cookie()` helper; update `auth_headers()` to use cookies (~25 lines)
- [x] 2.6 Run `cd backend && pytest -v` — all GREEN

## Phase 3: Frontend Migration

- [x] 3.1 Modify `frontend/src/store/auth.ts` — remove `accessToken`, `refreshToken`, `setTokens`; change `login` signature to `(user: User) => void` (~-15 lines)
- [x] 3.2 Modify `frontend/src/api/client.ts` — set `withCredentials: true`; replace Bearer interceptor with CSRF header injection (`X-CSRF-Token` from cookie) on POST/PUT/PATCH/DELETE; refresh interceptor calls `POST /api/auth/refresh` with no body (~25 lines)
- [x] 3.3 Modify `frontend/src/features/auth/Login.tsx` — call `login(user)` without tokens; response body contains only `{id, name, email}` (~-8 lines)
- [x] 3.4 Modify `frontend/src/features/auth/Register.tsx` — remove auto-login after register; redirect to `/login` on success (two-step flow) (~-15 lines)
- [x] 3.5 Run `cd frontend && tsc --noEmit` — no type errors

## Phase 4: Verification + Cleanup

- [x] 4.1 Run full backend test suite: `cd backend && pytest -v` — all GREEN (79/79)
- [x] 4.2 Verify zero `accessToken`/`refreshToken` references in frontend code — CONFIRMED
- [x] 4.3 Verify no `Bearer` header injection in frontend — CONFIRMED
- [x] 4.4 Update OpenAPI docstrings in `backend/app/api/auth.py` to reflect cookie-based auth

## Archive Reconciliation

Phase 3-4 checkboxes reconciled during archive. All 20 tasks (17 original + 3 additional tests) confirmed complete via engram apply-progress (#38) and orchestrator final-state assertion.
