# BarzMap - Server Tech Plan

## What We're Building
A backend API for BarzMap, a web app where people can find and share outdoor gyms and workout parks. This server handles data storage, user authentication, and admin workflows.

## Tech Stack

### Backend
- **FastAPI** - Handles requests and data
- **PostgreSQL** - Stores data (Docker containers)
- **Auth0** - Handles user login
- **Python** - Core language
- **SQLAlchemy** - ORM for database interaction
- **Alembic** - Database migrations
- **Pytest** - Automated testing

### Hosting & Infrastructure
- **Render** - Hosts the API server
- **Docker** - PostgreSQL database in containers
- **Cloudflare** - Image delivery / Storage (Optional)
- **Redis** - Rate limiting (planned)

## Features

### 1. API Endpoints (mounted HTTP vs backlog)
Mounted in `main.py` today (**trimmed** to current frontend usage; see `README.md`):
- **Parks**: List; bounding-box read; multipart **submit**; **moderate** submission (`PATCH`); **delete** submission (`DELETE`) — not a full public CRUD resource for arbitrary field edits
- **Equipment / Park equipment**: List / read endpoints
- **Users**: List; Auth0-backed login/bootstrap; role/permission helpers
- **Images**: List images per park — uploads are tied to park submission and Adapters layer
- **Events**: Feed with location and date filtering

Still in schema, services, or product docs but **not** exposed as mounted routers (examples: dedicated `/api/reviews`, `/api/admin/park-submissions` per FEDC, `/auth`, standalone image moderation routes). See **README**, section *Untrimmed / not mounted on the app (yet)*.

### 2. Admin Workflows
- **Approval (partially in HTTP)**: Moderation status and notes via `PATCH /api/park/{park_id}`; removal via `DELETE`. No dedicated admin submission feed routes in `main.py` yet (contrast `docs/FEDC.md`).
- **Content Moderation (HTTP backlog)**: Image records and flags may exist in the DB layer; **no** dedicated mounted endpoints for moderators to approve/flag/delete images outside the submission pipeline.

## P1 (Complete in repo — matches current implementation)

- [x] Set up PostgreSQL database in Docker
  - [x] Configure Docker Compose for main and test databases
  - [x] Set up database connection and environment variables
- [x] Set up FastAPI project structure
  - [x] `main.py` app configuration and trimmed router registration
  - [x] Project folders (`api`, `models`, `services`)
  - [x] CORS and middleware
- [x] Connect to PostgreSQL
  - [x] SQLAlchemy session and `PostgresConnection.py`
  - [x] Database models (User, Park, Equipment, Image, Review, Event, etc.)
  - [x] Alembic migrations
- [x] Mounted HTTP API (see `main.py` and `README.md`)
  - [x] Parks: list, location/bounding-box query, multipart submit, moderation `PATCH`, submission `DELETE`
  - [x] Equipment and park-equipment read endpoints
  - [x] Users: list, login/bootstrap, Auth0 role/permission helpers
  - [x] Images: list-by-park
  - [x] Events: feed with location-based filtering and distance (Haversine) in the service layer
- [x] Design and create database schema (incl. reviews table and related models where present)
- [x] Park submission pipeline (multipart + storage adapter where configured)
- [x] OpenAPI (Swagger/ReDoc)

## P1 backlog (intentionally unchecked — not in current mounted API or repo)

- [ ] **Auth0 tenant / Render hosting**: account and dashboard steps are outside this repository; track in your runbook, not as code-complete checkboxes
- [ ] **Health route**: `GET /health` on the FastAPI app (Compose healthchecks exist; app route does not)
- [ ] **Full HTTP CRUD** for every domain object (e.g. arbitrary park field updates outside moderation)
- [ ] **Reviews HTTP API** (`/api/reviews` or equivalent router)
- [ ] **Dedicated admin submission feed** (e.g. paginated `GET /api/admin/park-submissions` per FEDC)
- [ ] **Dedicated image moderation HTTP endpoints** (approve/flag/delete as first-class routes)
- [ ] **Automated tests**: `pytest.ini` exists; **no** `tests/` suite in-tree yet

## P2

- [ ] Implement user authentication security
  - [ ] Auth0 JWT token validation middleware
  - [ ] Protected route decorators (Dependencies)
  - [ ] Management API access token caching
- [ ] Add integration tests for complex flows
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Implement role-based access control (RBAC)
  - [ ] Auth0 JWT token validation middleware
  - [ ] Admin-only endpoint protection
  - [ ] Moderator permissions enforcement
- [ ] Redis rate limiting
  - [ ] Park submission rate limiting (per user/IP)
  - [ ] Map/location request rate limiting (per user/IP)
- [ ] Advanced distance/radius search for parks
- [ ] AI Integration
  - [ ] Park equipment detection from images (Zero-shot / YOLO)

## Roadmap

Product-oriented phases (overlaps in places with **P1 backlog** and **P2** above; those sections track engineering detail).

### Phase 1: Core API ✅
- [x] Database schema design and implementation
- [x] Frontend-trimmed HTTP API mounted in `main.py`
- [x] API documentation (Swagger/OpenAPI)
- [x] Basic location-based park queries (`GET /api/park/location`)

### Phase 2: Admin & Moderation 🚧
- [ ] Role-based access control (RBAC) and JWT-protected routes
- [x] Park submission moderation (`PATCH /api/park/{park_id}`) and deletion (`DELETE /api/park/{park_id}`)
- [ ] Admin submission list/detail HTTP aligned with `docs/FEDC.md` (e.g. `/api/admin/park-submissions`)
- [ ] Reviews HTTP surface (`/api/reviews`)
- [ ] Dedicated image moderation / management endpoints beyond list-by-park

### Phase 3: Advanced Features 📋
- [ ] Advanced geospatial queries (PostGIS)
- [ ] AI-powered equipment detection from images
- [ ] Real-time notifications
- [ ] Analytics and reporting

See the [open issues](https://github.com/your_username/BarzMap-server/issues) for a full list of proposed features and known issues.

## Cost
- **Auth0**: Free for 7,500 users/month
- **Docker/PostgreSQL**: Free (self-hosted)
- **Render**: Free server hosting (API)
- **Cloudflare**: Free image delivery

**Total cost: $0/month** for the first 6+ months
