# Docker Foundation Specification

## Purpose

Defines the Docker Compose setup with 3 independent services: PostgreSQL database, FastAPI backend, and React frontend. Each container MUST be independently runnable for development.

## ADDED Requirements

### Requirement: Docker Compose Services

The system MUST provide a `docker-compose.yml` with 3 services: `db` (PostgreSQL), `backend` (FastAPI), `frontend` (React).

#### Scenario: All services start together

- GIVEN docker-compose.yml exists at project root
- WHEN `docker compose up` is executed
- THEN all 3 services start successfully
- AND the backend connects to the database
- AND the frontend connects to the backend

### Requirement: Database Service

The db service MUST use PostgreSQL 18.4 with a named volume for data persistence.

#### Scenario: Database with health check

- GIVEN the db service is configured
- WHEN the container starts
- THEN a health check verifies PostgreSQL is accepting connections
- AND data persists in a named volume across restarts

#### Scenario: Database accessible to backend

- GIVEN the db and backend services are running
- WHEN the backend starts
- THEN it connects to the database using DATABASE_URL environment variable

### Requirement: Backend Service

The backend service MUST run uvicorn with hot reload for development.

#### Scenario: Backend with hot reload

- GIVEN the backend service is configured
- WHEN the container starts
- THEN uvicorn runs with --reload flag
- AND file changes in the mounted source directory trigger automatic restart

#### Scenario: Backend connects to database

- GIVEN the db service is healthy
- WHEN the backend service starts
- THEN it successfully connects to PostgreSQL
- AND the API endpoints are available

### Requirement: Frontend Service

The frontend service MUST run Vite dev server with hot reload for development.

#### Scenario: Frontend with hot reload

- GIVEN the frontend service is configured
- WHEN the container starts
- THEN Vite dev server runs
- AND source changes trigger automatic HMR

#### Scenario: Frontend connects to backend

- GIVEN the backend service is running
- WHEN the frontend service starts
- THEN API requests are proxied to the backend

### Requirement: Independent Containers

Each container MUST be independently runnable. No single container failure should prevent other containers from starting.

#### Scenario: Backend without frontend

- GIVEN only the db and backend services are running
- WHEN the frontend container is not started
- THEN the backend API remains fully functional

#### Scenario: Frontend without backend

- GIVEN only the frontend service is running
- WHEN the backend container is not started
- THEN the frontend loads (may show connection errors for API calls)

### Requirement: Network Isolation

The system MUST configure a Docker network for inter-service communication.

#### Scenario: Inter-service communication

- GIVEN all 3 services are on the same Docker network
- WHEN the backend references the db service by name
- THEN DNS resolution succeeds
- AND the connection is established over the Docker network

### Requirement: Volume Persistence

Database data MUST persist in a named Docker volume across container restarts and recreations.

#### Scenario: Data survives restart

- GIVEN the db container has been running with data
- WHEN `docker compose down` is executed
- AND `docker compose up` is executed again
- THEN all data is intact
