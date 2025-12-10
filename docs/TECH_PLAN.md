# BarzMap - Server Tech Plan

## What We're Building
A backend API for BarzMap, a web app where people can find and share outdoor gyms and workout parks. This server handles data storage, user authentication, and admin workflows.

## Tech Stack

### Backend
- **FastAPI** - Handles requests and data
- **PostgreSQL (Supabase)** - Stores data
- **Auth0** - Handles user login
- **Python** - Core language
- **SQLAlchemy** - ORM for database interaction
- **Alembic** - Database migrations
- **Pytest** - Automated testing

### Hosting & Infrastructure
- **Render** - Hosts the API server
- **Supabase** - Hosts the PostgreSQL database
- **Cloudflare** - Image delivery / Storage (Optional)

## Features

### 1. API Endpoints
- **Parks**: Create, Read, Update, Delete (CRUD) parks
- **Equipment**: Manage park equipment inventory
- **Users**: User profiles and role management
- **Images**: Handle park image metadata and approvals
- **Reviews**: User reviews and ratings for parks
- **Admin**: Advanced management and approval workflows

### 2. Admin Workflows
- **Approval System**: Admins review user-submitted parks before they go live
- **Content Moderation**: Review reported images or comments

## Start Up Checklist

### 1. Set Up Accounts & Services
- [X] Create Supabase account and project
  - [X] Set up PostgreSQL database
  - [X] Configure authentication settings
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
- [X] Connect to Supabase/Postgres
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
- [X] Implement core CRUD operations
- [X] API Documentation (Swagger/OpenAPI auto-generated)

### Phase 2: Admin & Moderation
- [ ] Implement role-based access control (RBAC)
  - [ ] Admin-only endpoints
  - [ ] Moderator permissions
- [ ] Park approval workflow endpoints
  - [ ] "Pending" vs "Approved" status logic
- [ ] Image moderation endpoints

### Phase 3: Advanced Features
- [ ] Geospatial queries (PostGIS or simple bounding box)
  - [X] Simple lat/long bounding box implemented
  - [ ] Advanced distance/radius search
- [ ] AI Integration
  - [ ] Park equipment detection from images (Zero-shot / YOLO)

## Cost
- **Auth0**: Free for 7,500 users/month
- **Supabase**: Free for 500MB database
- **Render**: Free server hosting (API)
- **Cloudflare**: Free image delivery

**Total cost: $0/month** for the first 6+ months
