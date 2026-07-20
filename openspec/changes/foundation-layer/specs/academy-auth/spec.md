# Academy Auth Specification

## Purpose

Defines registration, login, and JWT token lifecycle for the Academy-as-user model. An Academy IS the user — no separate User table exists.

## ADDED Requirements

### Requirement: Academy Registration

The system MUST allow an Academy to register with a unique name and email. Password MUST be hashed with bcrypt before storage.

#### Scenario: Successful registration

- GIVEN no Academy with the given email exists
- WHEN POST /api/auth/register with valid name, email, password
- THEN a new Academy is created
- AND the response contains id, name, email, access_token, refresh_token
- AND the password is NOT stored in plaintext

#### Scenario: Duplicate email

- GIVEN an Academy with email "test@academy.com" exists
- WHEN POST /api/auth/register with email "test@academy.com"
- THEN the response is 409 Conflict

#### Scenario: Duplicate name

- GIVEN an Academy with name "Academy X" exists
- WHEN POST /api/auth/register with name "Academy X"
- THEN the response is 409 Conflict

### Requirement: Academy Login

The system MUST authenticate an Academy by email and password, returning access and refresh JWT tokens.

#### Scenario: Successful login

- GIVEN an Academy with valid credentials exists
- WHEN POST /api/auth/login with correct email and password
- THEN the response contains access_token and refresh_token
- AND both tokens are valid JWTs

#### Scenario: Wrong password

- GIVEN an Academy with email "test@academy.com" exists
- WHEN POST /api/auth/login with correct email and wrong password
- THEN the response is 401 Unauthorized

#### Scenario: Unknown email

- GIVEN no Academy with email "unknown@academy.com" exists
- WHEN POST /api/auth/login with email "unknown@academy.com"
- THEN the response is 401 Unauthorized

### Requirement: Token Refresh

The system MUST allow exchanging a valid refresh token for a new access token, and MUST invalidate the old refresh token.

#### Scenario: Successful token refresh

- GIVEN a valid refresh token was issued
- WHEN POST /api/auth/refresh with the refresh token
- THEN the response contains a new access_token
- AND the old refresh token is invalidated

#### Scenario: Invalid refresh token

- GIVEN a refresh token has been rotated or expired
- WHEN POST /api/auth/refresh with the old token
- THEN the response is 401 Unauthorized

### Requirement: JWT Token Structure

Access tokens MUST encode the academy_id as the subject claim. Tokens MUST have configurable expiry via application settings.

#### Scenario: Access token contains academy_id

- GIVEN a valid access token was issued for Academy ID 42
- WHEN the token is decoded
- THEN the sub claim equals "42"
