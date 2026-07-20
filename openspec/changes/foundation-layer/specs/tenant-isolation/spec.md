# Tenant Isolation Specification

## Purpose

Defines the FastAPI dependency injection pattern that ensures every database query is scoped by academy_id. Prevents cross-academy data leakage.

## ADDED Requirements

### Requirement: Academy Context Extraction

The system MUST provide a FastAPI dependency `get_academy_context` that extracts the academy_id from the JWT access token.

#### Scenario: Valid token provides context

- GIVEN a valid access token for Academy ID 42
- WHEN get_academy_context is invoked
- THEN the returned context contains academy_id = 42

#### Scenario: Missing token

- GIVEN no Authorization header is present
- WHEN get_academy_context is invoked
- THEN the response is 401 Unauthorized

#### Scenario: Expired token

- GIVEN an expired access token
- WHEN get_academy_context is invoked
- THEN the response is 401 Unauthorized

### Requirement: Query Scoping

Every database query for Headquarters, Classroom, and future entities MUST include a WHERE clause filtering by academy_id.

#### Scenario: Scoped headquarters list

- GIVEN Academy A owns 3 Headquarters and Academy B owns 2
- WHEN Academy A lists Headquarters
- THEN only Academy A's 3 Headquarters are returned

#### Scenario: Scoped classroom list

- GIVEN Academy A's Headquarters has 4 classrooms and Academy B's has 1
- WHEN Academy A lists all their classrooms
- THEN only Academy A's 4 classrooms are returned

### Requirement: Cross-Academy Access Denial

The system MUST return 404 Not Found when an Academy attempts to access a resource owned by a different Academy. MUST NOT return 403 (which would leak existence).

#### Scenario: Cross-academy read

- GIVEN Headquarters HX belongs to Academy A
- WHEN Academy B attempts GET /api/headquarters/{HX.id}
- THEN the response is 404 Not Found

#### Scenario: Cross-academy update

- GIVEN Headquarters HX belongs to Academy A
- WHEN Academy B attempts PUT /api/headquarters/{HX.id}
- THEN the response is 404 Not Found

#### Scenario: Cross-academy delete

- GIVEN Headquarters HX belongs to Academy A
- WHEN Academy B attempts DELETE /api/headquarters/{HX.id}
- THEN the response is 404 Not Found

### Requirement: Unauthenticated Request Denial

The system MUST return 401 Unauthorized for any request to protected endpoints that lacks a valid access token.

#### Scenario: No token on protected endpoint

- GIVEN no Authorization header is present
- WHEN GET /api/headquarters is requested
- THEN the response is 401 Unauthorized
