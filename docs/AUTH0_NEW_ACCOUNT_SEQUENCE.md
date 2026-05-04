# Auth0 New Account Sequence

## Purpose
Define the expected sequence when a user creates (or effectively creates) a BarzMap account through Auth0, including where backend user provisioning happens and what to do on failure paths.

## Scope
- Covers first-time user creation via Auth0-based login/signup.
- Covers repeated login behavior for already-provisioned users.
- Covers backend provisioning from Auth0 identity claims into the `users` table.

## Actors
- `Client App` (web/mobile frontend)
- `Auth0` (Universal Login + token issuer)
- `BarzMap API` (FastAPI backend)
- `PostgreSQL` (`users` table)

## High-Level Sequence

The diagram below is the source of truth. If an older rendered image link was embedded elsewhere, regenerate from this PlantUML.

```
@startuml
participant "Client App" as Client
participant "Auth0" as Auth0
participant "BarzMap API" as API
participant "PostgreSQL" as DB
Client ->> Auth0: Start signup/login (Universal Login)
Auth0 -->> Client: Return ID token + access token
Client ->> API: Call authenticated endpoint with Bearer token
API ->> API: Validate JWT (issuer, audience, exp, signature)
API ->> API: Extract identity claims (sub, email, name, picture)
API ->> DB: Lookup user by auth0_id (sub)
alt User exists
    DB -->> API: Existing user row
    API -->> Client: Continue request as existing user
else User does not exist
    API ->> DB: Insert new user (auth0_id, email, name, profile_picture_url)
    DB -->> API: New user row
    API -->> Client: Continue request as newly provisioned user
end
@enduml
```

## Detailed Flow

1. User selects `Continue with ...` or signs up in Auth0 Universal Login.
2. Auth0 authenticates the user and returns tokens to the client app.
3. Client app calls a protected BarzMap API endpoint with `Authorization: Bearer <token>`.
4. API validates token:
   - Signature against Auth0 JWKS
   - `iss` matches configured Auth0 domain
   - `aud` matches API audience
   - Token is not expired
5. API extracts identity claims from token:
   - `sub` (maps to `auth0_id`)
   - `email`
   - `name` (fallback strategy if missing)
   - `picture` (optional)
6. API checks whether a user already exists by `auth0_id`.
7. If not found, API creates a user row with the mapped identity fields only (`auth0_id`, `email`, `name`, optional `profile_picture_url`).
8. API continues serving the original protected request with the resolved app user context.

## Provisioning Rules
- **Primary identity key:** `auth0_id` (`sub` claim).
- **Idempotency:** Repeated logins with same `sub` must never create duplicate users.
- **Roles and permissions:** Not persisted on `users`. Use Auth0 roles, Actions, or app/API authorization for admin or moderator behavior.
- **Missing optional claims:** `picture` can be null.
- **Email updates:** If Auth0 email changes later, decide whether to sync (recommended: explicit sync policy, not silent overwrite).

## Failure Paths and Expected Behavior

### Invalid or Missing Token
- Return `401 Unauthorized`.
- Do not attempt user creation.

### Token Valid, DB Unavailable
- Return `503 Service Unavailable` (or `500` if service classification is not yet implemented).
- Log structured error with correlation/request ID.

### Token Valid, User Insert Fails (Constraint/Transaction Error)
- Roll back transaction.
- Return `500 Internal Server Error` with safe message.
- Log full error context server-side.

### Race Condition (Two First Requests in Parallel)
- Enforce unique constraint on `users.auth0_id`.
- On duplicate key:
  - Retry lookup by `auth0_id`.
  - Use existing row if found.

## Recommended Backend Contract
- Use a dedicated endpoint/dependency for auth bootstrap, for example:
  - `GET /auth/me` or
  - shared auth dependency used by protected endpoints.
- Response should include:
  - `user_id`
  - `email`
  - `name`
  - `is_new_user` (true only when provisioned during this request)
  - optional client-facing metadata (not required to mirror database columns on `users`)

## Data Mapping
- Auth0 `sub` -> `users.auth0_id`
- Auth0 `email` -> `users.email`
- Auth0 `name` -> `users.name`
- Auth0 `picture` -> `users.profile_picture_url`

## Security Notes
- Never trust user identity fields from client body/query when token is present.
- Identity source of truth is validated JWT claims.
- Keep Auth0 secrets and domain/audience values in environment variables.

## Observability
- Log events:
  - `auth.login.validated`
  - `auth.user.found`
  - `auth.user.created`
  - `auth.user.create_failed`
- Track metrics:
  - new users per day
  - auth validation failures
  - provisioning latency (p50/p95)

## Implementation Checklist
- [ ] JWT validation middleware/dependency wired for protected endpoints
- [ ] `auth0_id` unique constraint confirmed in DB schema
- [ ] get-or-create user flow implemented and transaction-safe
- [ ] `is_new_user` response contract implemented
- [ ] structured logs + metrics added
- [ ] integration tests for:
  - [ ] first-time login provisioning
  - [ ] repeat login no-duplicate behavior
  - [ ] invalid token rejection
  - [ ] DB failure handling
