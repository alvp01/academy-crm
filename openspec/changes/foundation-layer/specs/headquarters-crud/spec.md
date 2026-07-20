# Headquarters CRUD Specification

## Purpose

Defines full CRUD operations for Headquarters, scoped to the authenticated Academy. Each Headquarters has a unique name within its Academy.

## ADDED Requirements

### Requirement: Create Headquarters

The system MUST allow an Academy to create a Headquarters with a name. The name MUST be unique within the Academy.

#### Scenario: Successful creation

- GIVEN an authenticated Academy
- WHEN POST /api/headquarters with a valid name
- THEN the response contains id, academy_id, name
- AND the Headquarters is persisted

#### Scenario: Duplicate name within academy

- GIVEN an Academy already has a Headquarters named "Main"
- WHEN the same Academy POSTs /api/headquarters with name "Main"
- THEN the response is 409 Conflict

#### Scenario: Same name in different academy

- GIVEN Academy A has a Headquarters named "Main"
- WHEN Academy B creates a Headquarters named "Main"
- THEN the creation succeeds (uniqueness is per-academy)

### Requirement: List Headquarters

The system MUST return a paginated list of Headquarters belonging to the authenticated Academy.

#### Scenario: Paginated list

- GIVEN an Academy owns 15 Headquarters
- WHEN GET /api/headquarters?page=1&size=10
- THEN the response contains items (max 10), total=15, page=1, size=10

#### Scenario: Empty list

- GIVEN an Academy owns no Headquarters
- WHEN GET /api/headquarters
- THEN the response contains items=[], total=0

### Requirement: Get Headquarters by ID

The system MUST return a single Headquarters by ID, scoped to the Academy.

#### Scenario: Successful get

- GIVEN Headquarters HX belongs to the authenticated Academy
- WHEN GET /api/headquarters/{HX.id}
- THEN the response contains the Headquarters with id, academy_id, name

#### Scenario: Headquarters not found

- GIVEN no Headquarters with ID 999 exists
- WHEN GET /api/headquarters/999
- THEN the response is 404 Not Found

### Requirement: Update Headquarters

The system MUST allow updating a Headquarters name. The new name MUST be unique within the Academy.

#### Scenario: Successful name update

- GIVEN Headquarters HX with name "Old" belongs to the Academy
- WHEN PUT /api/headquarters/{HX.id} with name "New"
- THEN the response contains name="New"
- AND the update is persisted

#### Scenario: Name conflict on update

- GIVEN an Academy has Headquarters "A" and "B"
- WHEN Headquarters "A" is updated to name "B"
- THEN the response is 409 Conflict

### Requirement: Delete Headquarters

The system MUST allow deleting a Headquarters by ID. Deletion MUST be blocked if the Headquarters has associated classrooms.

#### Scenario: Successful deletion

- GIVEN Headquarters HX has no classrooms
- WHEN DELETE /api/headquarters/{HX.id}
- THEN the response is 204 No Content
- AND the Headquarters is removed

#### Scenario: Blocked deletion with classrooms

- GIVEN Headquarters HX has 2 classrooms
- WHEN DELETE /api/headquarters/{HX.id}
- THEN the response is 409 Conflict
- AND the Headquarters is NOT deleted
