# Classroom CRUD Specification

## Purpose

Defines full CRUD operations for Classrooms, scoped to the Academy via Headquarters. Each Classroom belongs to a Headquarters and has a unique name within that Headquarters.

## ADDED Requirements

### Requirement: Create Classroom

The system MUST allow creating a Classroom within a Headquarters with a name and capacity. Capacity MUST be a positive integer.

#### Scenario: Successful creation

- GIVEN an authenticated Academy owns Headquarters HX
- WHEN POST /api/classrooms with headquarters_id={HX.id}, name="Room A", classes_capacity=30
- THEN the response contains id, headquarters_id, name, classes_capacity=30

#### Scenario: Invalid capacity

- GIVEN an authenticated Academy owns Headquarters HX
- WHEN POST /api/classrooms with classes_capacity=0
- THEN the response is 422 Unprocessable Entity

#### Scenario: Duplicate name within headquarters

- GIVEN Headquarters HX has a classroom named "Room A"
- WHEN another classroom "Room A" is created in HX
- THEN the response is 409 Conflict

#### Scenario: Same name in different headquarters

- GIVEN Headquarters HX1 has "Room A" and HX2 belongs to the same Academy
- WHEN "Room A" is created in HX2
- THEN the creation succeeds (uniqueness is per-headquarters)

### Requirement: List Classrooms

The system MUST return a paginated list of Classrooms, optionally filtered by headquarters_id.

#### Scenario: List all classrooms for academy

- GIVEN an Academy owns 8 classrooms across 3 Headquarters
- WHEN GET /api/classrooms
- THEN the response contains all 8 classrooms

#### Scenario: List classrooms by headquarters

- GIVEN Headquarters HX has 3 classrooms
- WHEN GET /api/classrooms?headquarters_id={HX.id}
- THEN the response contains only HX's 3 classrooms

#### Scenario: Paginated list

- GIVEN an Academy owns 25 classrooms
- WHEN GET /api/classrooms?page=2&size=10
- THEN the response contains items (max 10), total=25, page=2, size=10

### Requirement: Get Classroom by ID

The system MUST return a single Classroom by ID, scoped to the Academy.

#### Scenario: Successful get

- GIVEN Classroom CX belongs to the Academy
- WHEN GET /api/classrooms/{CX.id}
- THEN the response contains the Classroom with id, headquarters_id, name, classes_capacity

#### Scenario: Classroom not found

- GIVEN no Classroom with ID 999 exists
- WHEN GET /api/classrooms/999
- THEN the response is 404 Not Found

### Requirement: Update Classroom

The system MUST allow updating a Classroom's name and/or capacity. New capacity MUST be a positive integer.

#### Scenario: Successful update

- GIVEN Classroom CX with name="Room A", classes_capacity=30
- WHEN PUT /api/classrooms/{CX.id} with name="Room B", classes_capacity=40
- THEN the response contains name="Room B", classes_capacity=40

#### Scenario: Capacity validation on update

- GIVEN Classroom CX with classes_capacity=30
- WHEN PUT /api/classrooms/{CX.id} with classes_capacity=-5
- THEN the response is 422 Unprocessable Entity

### Requirement: Delete Classroom

The system MUST allow deleting a Classroom by ID. Deletion MUST be blocked if the Classroom has associated classes.

#### Scenario: Successful deletion

- GIVEN Classroom CX has no classes
- WHEN DELETE /api/classrooms/{CX.id}
- THEN the response is 204 No Content

#### Scenario: Blocked deletion with classes

- GIVEN Classroom CX has 2 classes
- WHEN DELETE /api/classrooms/{CX.id}
- THEN the response is 409 Conflict
- AND the Classroom is NOT deleted

### Requirement: Capacity Enforcement

The system MUST enforce that the total class quota within a Classroom does not exceed its classes_capacity.

#### Scenario: Class quota within capacity

- GIVEN Classroom CX has classes_capacity=30 and current total quota of 25
- WHEN a new class with quota 5 is added
- THEN the operation succeeds

#### Scenario: Class quota exceeds capacity

- GIVEN Classroom CX has classes_capacity=30 and current total quota of 28
- WHEN a new class with quota 5 is added
- THEN the response is 409 Conflict
