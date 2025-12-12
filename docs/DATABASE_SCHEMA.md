# BarzMap Database Schema

## Overview
This document defines the database schema for BarzMap, an outdoor gym and workout park discovery application. The schema is designed to support user management, park submissions, equipment tracking, and image management.

## Database Tables

### 1. Users Table
Stores user account information and authentication details.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth0_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    profile_picture_url TEXT,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'moderator', 'admin')),
    join_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Fields:**
- `id`: Unique identifier for the user
- `auth0_id`: Auth0 user identifier (external auth)
- `email`: User's email address
- `name`: User's display name
- `profile_picture_url`: URL to user's profile picture
- `role`: User role (user, moderator, admin)
- `join_date`: When the user joined
- `is_active`: Whether the account is active
- `created_at`: Record creation timestamp
- `updated_at`: Record last update timestamp

### 2. Parks Table
Stores information about outdoor gyms and workout parks with integrated approval workflow.

```sql
CREATE TABLE parks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    address TEXT,
    city VARCHAR(255),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    submitted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    submit_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMP WITH TIME ZONE,
    admin_notes TEXT,
    rating DECIMAL(3, 2) CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Fields:**
- `id`: Unique identifier for the park
- `name`: Name of the park
- `description`: Detailed description of the park
- `latitude`: Geographic latitude coordinate
- `longitude`: Geographic longitude coordinate
- `address`: Street address
- `city`, `state`, `country`, `postal_code`: Location details
- `status`: Approval status (pending, approved, rejected)
- `submitted_by`: User who submitted the park
- `submit_date`: When the park was submitted
- `approved_by`: Admin who approved/rejected the park
- `approved_at`: When the park was approved/rejected
- `admin_notes`: Notes from admin review
- `rating`: Average user rating (0-5)
- `review_count`: Number of reviews
- `created_at`, `updated_at`: Timestamps

### 3. Equipment Table
Stores different types of workout equipment.

```sql
CREATE TABLE equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Fields:**
- `id`: Unique identifier for equipment type
- `name`: Name of the equipment (e.g., "Pull-up bars", "Bench press")
- `description`: Description of the equipment
- `icon_name`: Icon identifier for UI display
- `created_at`: Record creation timestamp

### 4. Park_Equipment Table (Junction Table)
Links parks to their available equipment.

```sql
CREATE TABLE park_equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    park_id UUID REFERENCES parks(id) ON DELETE CASCADE,
    equipment_id UUID REFERENCES equipment(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(park_id, equipment_id)
);
```

**Fields:**
- `id`: Unique identifier for the relationship
- `park_id`: Reference to the park
- `equipment_id`: Reference to the equipment type
- `created_at`: Record creation timestamp

### 5. Images Table
Stores park photos and images.

```sql
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    park_id UUID REFERENCES parks(id) ON DELETE CASCADE,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    image_url TEXT NOT NULL,
    thumbnail_url TEXT,
    alt_text VARCHAR(255),
    is_approved BOOLEAN DEFAULT FALSE,
    is_primary BOOLEAN DEFAULT FALSE,
    is_inappropriate BOOLEAN DEFAULT FALSE,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Fields:**
- `id`: Unique identifier for the image
- `park_id`: Park the image belongs to
- `uploaded_by`: User who uploaded the image
- `image_url`: Full-size image URL
- `thumbnail_url`: Thumbnail image URL
- `alt_text`: Alt text for accessibility
- `is_approved`: Whether the image is approved by admin
- `is_primary`: Whether this is the main park image
- `is_inappropriate`: Flag for inappropriate content
- `upload_date`: When the image was uploaded
- `created_at`: Record creation timestamp

### 6. Reviews Table
Stores user reviews and ratings for parks.

```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    park_id UUID REFERENCES parks(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    is_approved BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(park_id, user_id)
);
```

**Fields:**
- `id`: Unique identifier for the review
- `park_id`: Park being reviewed
- `user_id`: User writing the review
- `rating`: Rating from 1-5
- `comment`: Review text
- `is_approved`: Whether the review is approved
- `created_at`, `updated_at`: Timestamps

### 7. Events Table
Stores events happening at parks (workout sessions, community gatherings, etc.).

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    park_id UUID REFERENCES parks(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    host VARCHAR(255),
    event_date DATE,
    event_time TIME,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Fields:**
- `id`: Unique identifier for the event
- `park_id`: Park where the event takes place
- `name`: Name of the event
- `description`: Event description text
- `host`: Name of the event host or organization
- `event_date`: Date of the event (optional)
- `event_time`: Time of the event (optional, 24-hour format)
- `created_by`: User who created the event
- `created_at`, `updated_at`: Timestamps


## Indexes

```sql
-- Performance indexes for common queries
CREATE INDEX idx_parks_status ON parks(status);
CREATE INDEX idx_parks_location ON parks(latitude, longitude);
CREATE INDEX idx_parks_submitted_by ON parks(submitted_by);
CREATE INDEX idx_parks_approved_by ON parks(approved_by);
CREATE INDEX idx_park_equipment_park_id ON park_equipment(park_id);
CREATE INDEX idx_images_park_id ON images(park_id);
CREATE INDEX idx_images_approved ON images(is_approved);
CREATE INDEX idx_reviews_park_id ON reviews(park_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_events_park_id ON events(park_id);
CREATE INDEX idx_events_date ON events(event_date);
```

## Constraints and Relationships

### Foreign Key Relationships:
- `parks.submitted_by` → `users.id`
- `parks.approved_by` → `users.id`
- `park_equipment.park_id` → `parks.id`
- `park_equipment.equipment_id` → `equipment.id`
- `images.park_id` → `parks.id`
- `images.uploaded_by` → `users.id`
- `reviews.park_id` → `parks.id`
- `reviews.user_id` → `users.id`
- `events.park_id` → `parks.id`
- `events.created_by` → `users.id`

## Sample Data
### Sample Equipment Data:
```sql
-- Insert sample equipment types
INSERT INTO equipment (id, name, description, icon_name) VALUES
    (gen_random_uuid(), 'Pull-up Bar', 'Horizontal bar for pull-ups and chin-ups', 'pull-up-bar'),
    (gen_random_uuid(), 'Gymnastics Rings', 'Suspension rings for advanced bodyweight training', 'gymnastics-rings'),
    (gen_random_uuid(), 'Push-up Bars', 'Elevated handles for push-ups and planks', 'push-up-bars'),
    (gen_random_uuid(), 'Ab Station', 'Station for abdominal and core exercises', 'ab-station'),
    (gen_random_uuid(), 'Parallel Bars', 'Parallel bars for dips, L-sits, and handstands', 'parallel-bars'),
    (gen_random_uuid(), 'Monkey Bars', 'Overhead bars for traversing and pull-ups', 'monkey-bars'),
    (gen_random_uuid(), 'Running Track', 'Designated path for running and jogging', 'running-track'),
```

## Notes
1. **Geographic Data**: Latitude and longitude are stored as DECIMAL for precision
2. **Single Table Approach**: Parks table handles both submission and approval workflow
3. **Image Storage**: Images are stored as URLs (Supabase Storage handles the actual files)
4. **Audit Trail**: The schema includes timestamps for audit purposes
5. **Scalability**: Indexes are designed for common query patterns (location-based searches, status filtering)