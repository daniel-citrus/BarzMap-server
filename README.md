# BarzMap Server

Backend API server for BarzMap, a web application where people can find and share outdoor gyms and workout parks. This server handles data storage, user authentication, and admin workflows.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Table of Contents

- [About The Project](#about-the-project)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Database Migrations](#database-migrations)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## About The Project

BarzMap Server is a RESTful API built with FastAPI that powers the BarzMap application. The **HTTP surface mounted in `main.py` is intentionally trimmed** to what the current frontend uses; the database and service layers still include more (for example `reviews` tables and Auth0 helpers) than is exposed over HTTP. User-submitted parks go through a moderation-oriented workflow (`pending` / `approved` / `rejected`). Administrator and moderator access is intended to be enforced via Auth0 and API authorization rather than columns on the `users` table (JWT route protection is not fully wired yet—see `docs/TECH_PLAN.md`).

### Key Features

- **Parks**: List, bounding-box query, multipart submission, moderation (`PATCH`), and submission delete (`DELETE`) under `/api/park`
- **Equipment & park equipment**: Read-only listing (`/api/equipment`, `/api/park-equipment/...`)
- **Auth0**: Management integration and user bootstrap/login flows under `/api/users` (not a separate `/auth` router)
- **Images**: List images for a park (`/api/images/...`); uploads happen as part of park submission (no standalone image moderation HTTP API yet)
- **Events**: Feed with optional location and date filters (`/api/events`)
- **Schema support (not fully exposed over HTTP)**: Reviews and richer admin/list contracts exist in the DB and docs but are **not** mounted as `/api/reviews` or `/api/admin/...` in `main.py` today

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![FastAPI][FastAPI]][FastAPI-url] - Modern, fast web framework for building APIs
* [![PostgreSQL][PostgreSQL]][PostgreSQL-url] - Relational database
* [![SQLAlchemy][SQLAlchemy]][SQLAlchemy-url] - Python SQL toolkit and ORM
* [![Alembic][Alembic]][Alembic-url] - Database migration tool
* [![Pytest][Pytest]][Pytest-url] - Testing framework
* [![Docker][Docker]][Docker-url] - Containerization
* [![Auth0][Auth0]][Auth0-url] - Authentication service

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- PostgreSQL 15+ (or use Docker)
- Auth0 account (for authentication)

### Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/your_username/BarzMap-server.git
   cd BarzMap-server
   ```

2. **Create a `.env` file** in the project root:
   ```env
   POSTGRES_USER=barzmap_user
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_DB=barzmap_db
   POSTGRES_PORT=5432
   POSTGRES_HOST=localhost
   
   # Auth0 Configuration
   AUTH0_DOMAIN=your-auth0-domain.auth0.com
   AUTH0_CLIENT_ID=your-client-id
   AUTH0_CLIENT_SECRET=your-client-secret
   AUTH0_AUDIENCE=your-api-identifier
   
   # Optional: Cloudflare for image storage
   CLOUDFLARE_ACCOUNT_ID=your-account-id
   CLOUDFLARE_API_TOKEN=your-api-token
   ```

3. **Install Python dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Start the database with Docker Compose**
   ```sh
   docker-compose up -d postgres
   ```

5. **Run database migrations**
   ```sh
   alembic upgrade head
   ```

6. **Start the development server**
   ```sh
   uvicorn main:app --reload
   ```

   Or use Docker Compose to run everything:
   ```sh
   docker-compose up
   ```

The API will be available at `http://localhost:8000`

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `POSTGRES_USER` | PostgreSQL username | Yes |
| `POSTGRES_PASSWORD` | PostgreSQL password | Yes |
| `POSTGRES_DB` | Database name | Yes |
| `POSTGRES_HOST` | Database host | Yes |
| `POSTGRES_PORT` | Database port | Yes |
| `AUTH0_DOMAIN` | Auth0 domain | Yes |
| `AUTH0_CLIENT_ID` | Auth0 client ID | Yes |
| `AUTH0_CLIENT_SECRET` | Auth0 client secret | Yes |
| `AUTH0_AUDIENCE` | Auth0 API identifier | Yes |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account ID | No |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token | No |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## API Endpoints

Routers are registered in `main.py`. The docstrings in `api/__init__.py` describe this as the **frontend-trimmed** set.

### Mounted today (`main.py`)

| Prefix | Purpose |
|--------|---------|
| `/api/park` | `GET /` list; `GET /location` bounding box; `POST /` submit park (multipart); `PATCH /{park_id}` moderation; `DELETE /{park_id}` remove submission |
| `/api/images` | `GET /park/{park_id}` list images for a park (optional query filters) |
| `/api/equipment` | `GET /` list equipment types |
| `/api/park-equipment` | `GET /park/{park_id}/equipment` equipment for one park |
| `/api/events` | `GET /` events feed (`lat` / `lng` / `radius` / `fromDate` / `limit`) |
| `/api/users` | `GET /` list users; `POST /{auth0_id}` login/bootstrap; `GET` / `POST` helpers for Auth0 roles and permissions |

There is **no** `GET /health` on the FastAPI app today (only Docker healthchecks in Compose).

### Untrimmed / not mounted on the app (yet)

These appear in older docs, broader product plans, or `docs/FEDC.md`, but **are not** included in `main.py` right now:

- **`/auth`** — no dedicated auth router; login/bootstrap lives under `/api/users`
- **`/api/reviews`** — `reviews` exist in the database layer; no reviews router is mounted
- **`/api/admin/...`** — e.g. `GET /api/admin/park-submissions` in FEDC; moderation today is `PATCH` / `DELETE` on `/api/park/{park_id}`, not under `/api/admin`
- **Full CRUD for every entity over HTTP** — many modules are read-oriented or workflow-specific (see table above)
- **Dedicated image moderation HTTP API** — not exposed; submission flow uses Cloudflare where configured
- **GeoJSON `bbox` on `GET /api/park`** — map use case uses `GET /api/park/location` with separate min/max lat/lng query params (see `docs/FEDC.md` implementation notes)

### API Documentation

Interactive API documentation is automatically available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Project Structure

```
BarzMap-server/
├── api/                    # FastAPI routers (mounted from main.py)
│   ├── equipment.py
│   ├── events.py
│   ├── images.py
│   ├── park_equipment.py
│   ├── parks.py
│   └── users.py
├── alembic/                # Database migrations
│   └── versions/
├── docs/                   # Documentation
│   ├── DATABASE_SCHEMA.md
│   ├── FEDC.md
│   ├── POSTGRES_SETUP.md
│   └── TECH_PLAN.md
├── models/                 # Data models (ORM + Pydantic)
│   ├── database/
│   ├── requests/
│   └── responses/
├── services/
│   ├── Adapters/           # Auth0, Cloudflare, etc.
│   ├── Database/          # Tables, PostgresConnection
│   └── Manager/           # Business logic orchestration
├── scripts/               # Seeds, purge utilities
├── main.py                # FastAPI application entry point
├── pytest.ini             # pytest config (test package not present yet)
├── requirements.txt
├── docker-compose.yml
├── docker-compose.test.yml
└── alembic.ini
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Testing

`pytest.ini` sets `testpaths = tests`, but **there is no `tests/` package in the repo yet**. When you add tests:

```sh
pytest
pytest --cov=. --cov-report=html
```

For testing, use the test database configuration in `docker-compose.test.yml`:

```sh
docker-compose -f docker-compose.test.yml up -d
pytest
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Database Migrations

This project uses Alembic for database migrations.

### Creating a new migration

```sh
alembic revision --autogenerate -m "description of changes"
```

### Applying migrations

```sh
alembic upgrade head
```

### Rolling back migrations

```sh
alembic downgrade -1
```

See `docs/DATABASE_SCHEMA.md` for the complete database schema documentation.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Documentation

Additional documentation is available in the `docs/` directory:

- **[DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)** - Complete database schema documentation
- **[POSTGRES_SETUP.md](docs/POSTGRES_SETUP.md)** - PostgreSQL setup guide
- **[TECH_PLAN.md](docs/TECH_PLAN.md)** - Technical plan, implementation checkpoints, backlog, **and roadmap** (phase-based); see especially [Roadmap](docs/TECH_PLAN.md#roadmap).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

MIT License is intended for this project; add a root `LICENSE` or `LICENSE.txt` file when publishing.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/
[PostgreSQL]: https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white
[PostgreSQL-url]: https://www.postgresql.org/
[SQLAlchemy]: https://img.shields.io/badge/SQLAlchemy-1C1C1C?style=for-the-badge&logo=sqlalchemy&logoColor=white
[SQLAlchemy-url]: https://www.sqlalchemy.org/
[Alembic]: https://img.shields.io/badge/Alembic-1C1C1C?style=for-the-badge
[Alembic-url]: https://alembic.sqlalchemy.org/
[Pytest]: https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white
[Pytest-url]: https://pytest.org/
[Docker]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[Auth0]: https://img.shields.io/badge/Auth0-EB5424?style=for-the-badge&logo=auth0&logoColor=white
[Auth0-url]: https://auth0.com/
