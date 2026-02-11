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
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## About The Project

BarzMap Server is a RESTful API built with FastAPI that powers the BarzMap application. It provides endpoints for managing parks, equipment, users, images, reviews, and events. The server includes an approval workflow for user-submitted parks and supports role-based access control for administrators.

### Key Features

- **Parks Management**: CRUD operations for outdoor gyms and workout parks
- **Equipment Tracking**: Manage equipment inventory at parks
- **User Authentication**: Auth0 integration for secure user management
- **Image Management**: Handle park photos with approval workflow
- **Reviews & Ratings**: User reviews and ratings system
- **Events**: Community events at parks
- **Admin Workflows**: Park approval and content moderation
- **Location-based Queries**: Search parks by geographic coordinates

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

The API provides the following endpoint groups:

- **Authentication** (`/auth`) - User authentication endpoints
- **Users** (`/api/users`) - User management
- **Parks** (`/api/park`) - Park CRUD operations and location-based queries
- **Equipment** (`/api/equipment`) - Equipment type management
- **Park Equipment** (`/api/park-equipment`) - Link equipment to parks
- **Images** (`/api/images`) - Image upload and management
- **Reviews** (`/api/reviews`) - User reviews and ratings
- **Events** (`/api/events`) - Park events management
- **Admin** (`/api/admin`) - Administrative operations

### API Documentation

Interactive API documentation is automatically available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Project Structure

```
BarzMap-server/
├── api/                    # API route handlers
│   ├── AdminRouter.py
│   ├── EquipmentRouter.py
│   ├── EventsRouter.py
│   ├── ImagesRouter.py
│   ├── ParkEquipmentRouter.py
│   ├── ParksRouter.py
│   ├── ReviewsRouter.py
│   └── UsersRouter.py
├── alembic/                # Database migrations
│   └── versions/
├── docs/                   # Documentation
│   ├── DATABASE_SCHEMA.md
│   ├── POSTGRES_SETUP.md
│   └── TECH_PLAN.md
├── models/                 # Data models
│   ├── database/          # SQLAlchemy models
│   └── requests/          # Pydantic request models
├── services/              # Business logic
│   ├── Authentication/    # Auth0 integration
│   ├── Database/         # Database operations
│   └── Manager/          # Business logic managers
│       ├── CloudFlare.py # Image storage service
│       └── ParkSubmissions.py
├── tests/                 # Test files
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker Compose configuration
└── alembic.ini           # Alembic configuration
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Testing

Run tests using pytest:

```sh
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_parks.py
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
- **[TECH_PLAN.md](docs/TECH_PLAN.md)** - Technical plan and roadmap

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

### Phase 1: Core API ✅
- [x] Database schema design and implementation
- [x] Core CRUD operations for all entities
- [x] API documentation (Swagger/OpenAPI)
- [x] Basic location-based queries

### Phase 2: Admin & Moderation 🚧
- [ ] Role-based access control (RBAC)
- [ ] Park approval workflow endpoints
- [ ] Image moderation endpoints
- [ ] Content moderation tools

### Phase 3: Advanced Features 📋
- [ ] Advanced geospatial queries (PostGIS)
- [ ] AI-powered equipment detection from images
- [ ] Real-time notifications
- [ ] Analytics and reporting

See the [open issues](https://github.com/your_username/BarzMap-server/issues) for a full list of proposed features and known issues.

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

Distributed under the MIT License. See `LICENSE.txt` for more information.

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
