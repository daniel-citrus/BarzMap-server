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

## Features

### 1. API Endpoints
- **Parks**: Create, Read, Update, Delete (CRUD) parks
- **Equipment**: Manage park equipment inventory
- **Users**: User profiles and role management
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

## Start Up Checklist

### 1. Set Up Accounts & Services
- [X] Set up PostgreSQL database in Docker
  - [X] Configure Docker Compose for main and test databases
  - [X] Set up database connection and environment variables
- [X] Create Auth0 account and tenant
  - [X] Configure social login providers (Google, Facebook)
  - [X] Set up application settings and callbacks
  - [X] Configure user metadata and roles
- [X] Create Render account for backend hosting
  - [X] Set up web service configuration
  - [X] Configure environment variables and secrets

### 2. Build Backend Foundation
- [X] Set up FastAPI project structure
  - [X] Create main.py with basic app configuration
  - [X] Set up project folders (api, models, services)
  - [X] Configure CORS and middleware
- [X] Connect to PostgreSQL
  - [X] Install and configure SQLAlchemy
  - [X] Set up database connection (PostgresConnection.py)
  - [X] Create database models (User, Park, Equipment, etc.)
  - [X] Set up Alembic for migrations
- [X] Create API endpoints
  - [X] Health check endpoint (/health)
  - [X] Parks CRUD endpoints
  - [X] Equipment & Park-Equipment endpoints
  - [X] User management endpoints
  - [X] Reviews & Images endpoints
  - [X] Events endpoints with location-based queries
  - [X] Park submission endpoints (submit, view, list with pagination)
- [ ] Implement user authentication security
  - [ ] Auth0 JWT token validation middleware
  - [ ] Protected route decorators (Dependencies)

### 3. Testing & Quality Assurance
- [X] Set up Pytest environment
- [X] Create unit tests for all major endpoints
- [ ] Add integration tests for complex flows
- [ ] Set up CI/CD pipeline (GitHub Actions)

## Build Plan

### Phase 1: Core API
- [X] Design and create database schema
  - [X] Parks, Equipment, Users, Images, Reviews tables
  - [X] Events table
- [X] Implement core CRUD operations
- [X] Park submission workflow
  - [X] Submit parks with images and equipment
  - [X] View submission details
  - [X] List submissions with pagination and filtering
- [X] Events feature
  - [X] Event feed with location-based filtering
  - [X] Distance calculations using haversine formula
- [X] API Documentation (Swagger/OpenAPI auto-generated)

### Phase 2: Admin & Moderation
- [X] Park approval workflow endpoints
  - [X] Approve park submissions
  - [X] Deny/reject park submissions
  - [X] Set parks back to pending status
  - [X] Add moderation comments
  - [X] "Pending" vs "Approved" vs "Rejected" status logic
- [X] Image moderation endpoints
  - [X] Update image approval status and flags
  - [X] Delete images
- [X] Admin CRUD endpoints for all resources
  - [X] Parks, Equipment, Images, Reviews, Park-Equipment, Events, Users
- [ ] Implement role-based access control (RBAC)
  - [ ] Auth0 JWT token validation middleware
  - [ ] Admin-only endpoint protection
  - [ ] Moderator permissions enforcement

### Phase 3: Advanced Features
- [X] Geospatial queries (PostGIS or simple bounding box)
  - [X] Simple lat/long bounding box implemented
  - [X] Distance/radius search for events
  - [ ] Advanced distance/radius search for parks
- [ ] AI Integration
  - [ ] Park equipment detection from images (Zero-shot / YOLO)

## Cost
- **Auth0**: Free for 7,500 users/month
- **Docker/PostgreSQL**: Free (self-hosted)
- **Render**: Free server hosting (API)
- **Cloudflare**: Free image delivery

**Total cost: $0/month** for the first 6+ months
