-- BarzMap Database Setup

-- Idempotent reset (safe re-run): drop existing objects, then recreate
BEGIN;
DROP FUNCTION IF EXISTS set_updated_at() CASCADE;
DROP TABLE IF EXISTS images CASCADE;
DROP TABLE IF EXISTS park_equipment CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS parks CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS users CASCADE;
COMMIT;

-- Required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Users Table
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

-- 2. Parks Table
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Equipment Table
CREATE TABLE equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Park_Equipment Table (Junction Table)
CREATE TABLE park_equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    park_id UUID REFERENCES parks(id) ON DELETE CASCADE,
    equipment_id UUID REFERENCES equipment(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(park_id, equipment_id)
);

-- 5. Images Table
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

-- 6. Reviews Table
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

-- Performance Indexes
CREATE INDEX idx_parks_status ON parks(status);
CREATE INDEX idx_parks_location ON parks(latitude, longitude);
CREATE INDEX idx_parks_submitted_by ON parks(submitted_by);
CREATE INDEX idx_parks_approved_by ON parks(approved_by);
CREATE INDEX idx_park_equipment_park_id ON park_equipment(park_id);
CREATE INDEX idx_images_park_id ON images(park_id);
CREATE INDEX idx_images_approved ON images(is_approved);
CREATE INDEX idx_reviews_park_id ON reviews(park_id);
CREATE INDEX idx_users_role ON users(role);

-- Data quality constraints and enhancements
-- Coordinate ranges
ALTER TABLE parks
  ADD CONSTRAINT parks_latitude_range CHECK (latitude >= -90 AND latitude <= 90),
  ADD CONSTRAINT parks_longitude_range CHECK (longitude >= -180 AND longitude <= 180);

-- Enforce NOT NULL on key foreign keys
ALTER TABLE park_equipment
  ALTER COLUMN park_id SET NOT NULL,
  ALTER COLUMN equipment_id SET NOT NULL;

ALTER TABLE images
  ALTER COLUMN park_id SET NOT NULL;

ALTER TABLE reviews
  ALTER COLUMN park_id SET NOT NULL,
  ALTER COLUMN user_id SET NOT NULL;

-- Ensure equipment names are unique
ALTER TABLE equipment
  ADD CONSTRAINT equipment_name_unique UNIQUE (name);

-- Only one primary image per park
CREATE UNIQUE INDEX IF NOT EXISTS uq_primary_image_per_park
  ON images (park_id)
  WHERE is_primary;

-- Helpful FK indexes
CREATE INDEX IF NOT EXISTS idx_images_uploaded_by ON images(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id);

-- Auto-update updated_at columns
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_users
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_updated_at_parks
BEFORE UPDATE ON parks
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_updated_at_reviews
BEFORE UPDATE ON reviews
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Sample Equipment Data
INSERT INTO equipment (id, name, description, icon_name) VALUES
    (gen_random_uuid(), 'Pull-up Bar', 'Horizontal bar for pull-ups and chin-ups', 'pull-up-bar'),
    (gen_random_uuid(), 'Gymnastics Rings', 'Suspension rings for advanced bodyweight training', 'gymnastics-rings'),
    (gen_random_uuid(), 'Push-up Bars', 'Elevated handles for push-ups and planks', 'push-up-bars'),
    (gen_random_uuid(), 'Ab Station', 'Station for abdominal and core exercises', 'ab-station'),
    (gen_random_uuid(), 'Parallel Bars', 'Parallel bars for dips, L-sits, and handstands', 'parallel-bars'),
    (gen_random_uuid(), 'Monkey Bars', 'Overhead bars for traversing and pull-ups', 'monkey-bars'),
    (gen_random_uuid(), 'Running Track', 'Designated path for running and jogging', 'running-track');

-- Success message
SELECT 'BarzMap database setup completed successfully!' as message;

