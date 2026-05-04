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

### 1. API Endpoints
- **Parks**: Create, Read, Update, Delete (CRUD) parks
- **Equipment**: Manage park equipment inventory
- **Users**: User profiles backed by Auth0 identity (roles live in Auth0 / API layer, not on `users`)
- **Images**: Handle park image metadata and approvals
- **Reviews**: User reviews and ratings for parks
- **Events**: Event feed with location-based filtering and distance calculations
- **Park Submissions**: Submit new parks with images and equipment
- **Admin**: Advanced management and approval workflows

### 2. Admin Workflows
- **Approval System**: Admins review user-submitted parks before they go live
  - Approve, deny, or set parks back to pending status
  - Add moderation comments
  - View paginated submission list with filtering
- **Content Moderation**: Review and manage images
  - Update image approval status and flags
  - Delete inappropriate images

## P1 (Complete)

- [x] Set up PostgreSQL database in Docker
  - [x] Configure Docker Compose for main and test databases
  - [x] Set up database connection and environment variables
- [x] Create Auth0 account and tenant
  - [x] Configure social login providers (Google, Facebook)
  - [x] Set up application settings and callbacks
  - [x] Configure user metadata and roles
- [x] Create Render account for backend hosting
  - [x] Set up web service configuration
  - [x] Configure environment variables and secrets
- [x] Set up FastAPI project structure
  - [x] Create main.py with basic app configuration
  - [x] Set up project folders (api, models, services)
  - [x] Configure CORS and middleware
- [x] Connect to PostgreSQL
  - [x] Install and configure SQLAlchemy
  - [x] Set up database connection (PostgresConnection.py)
  - [x] Create database models (User, Park, Equipment, etc.)
  - [x] Set up Alembic for migrations
- [x] Create API endpoints
  - [x] Health check endpoint (/health)
  - [x] Parks CRUD endpoints
  - [x] Equipment & Park-Equipment endpoints
  - [x] User management endpoints
  - [x] Reviews & Images endpoints
  - [x] Events endpoints with location-based queries
  - [x] Park submission endpoints (submit, view, list with pagination)
- [x] Design and create database schema
  - [x] Parks, Equipment, Users, Images, Reviews tables
  - [x] Events table
- [x] Implement core CRUD operations
- [x] Park submission workflow
  - [x] Submit parks with images and equipment
  - [x] View submission details
  - [x] List submissions with pagination and filtering
- [x] Events feature
  - [x] Event feed with location-based filtering
  - [x] Distance calculations using haversine formula
- [x] API Documentation (Swagger/OpenAPI auto-generated)
- [x] Park approval workflow endpoints
  - [x] Approve park submissions
  - [x] Deny/reject park submissions
  - [x] Set parks back to pending status
  - [x] Add moderation comments
  - [x] "Pending" vs "Approved" vs "Rejected" status logic
- [x] Image moderation endpoints
  - [x] Update image approval status and flags
  - [x] Delete images
- [x] Admin CRUD endpoints for all resources
  - [x] Parks, Equipment, Images, Reviews, Park-Equipment, Events, Users
- [x] Geospatial queries
  - [x] Simple lat/long bounding box implemented
  - [x] Distance/radius search for events
- [x] Set up Pytest environment
- [x] Create unit tests for all major endpoints

## P2

- [ ] Implement user authentication security
  - [ ] Auth0 JWT token validation middleware
  - [ ] Protected route decorators (Dependencies)
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

## Cost
- **Auth0**: Free for 7,500 users/month
- **Docker/PostgreSQL**: Free (self-hosted)
- **Render**: Free server hosting (API)
- **Cloudflare**: Free image delivery

**Total cost: $0/month** for the first 6+ months
