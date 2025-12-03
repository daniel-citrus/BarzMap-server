# PostgreSQL Setup Guide for BarzMap

This guide will walk you through installing PostgreSQL and setting up your database for the BarzMap project.

## Table of Contents
1. [Installation](#installation)
2. [Initial Setup](#initial-setup)
3. [Creating Your Database](#creating-your-database)
4. [Running Your Schema](#running-your-schema)
5. [Basic PostgreSQL Commands](#basic-postgresql-commands)
6. [Connecting from Python](#connecting-from-python)
7. [Useful Tips](#useful-tips)

---

## Installation

### Option 1: Homebrew (Recommended for macOS)

1. **Install PostgreSQL:**
   ```bash
   brew install postgresql@16
   ```

2. **Start PostgreSQL service:**
   ```bash
   brew services start postgresql@16
   ```

3. **Verify installation:**
   ```bash
   psql --version
   ```

### Option 2: Postgres.app (GUI Option)

1. Download from: https://postgresapp.com/
2. Install and launch the app
3. Click "Initialize" to create a new server

---

## Initial Setup

### First-Time Configuration

1. **Create a database user** (if using Homebrew, a default user is created):
   ```bash
   # Connect to PostgreSQL as the default user
   psql postgres
   ```

2. **Inside psql, create your database user:**
   ```sql
   CREATE USER barzmap_user WITH PASSWORD 'your_secure_password';
   ALTER USER barzmap_user CREATEDB;
   \q
   ```

3. **Create your database:**
   ```bash
   createdb barzmap_db
   # Or if you need to specify a user:
   createdb -U barzmap_user barzmap_db
   ```

---

## Creating Your Database

### Method 1: Using psql Command Line

```bash
# Connect to your database
psql barzmap_db

# Or with a specific user:
psql -U barzmap_user -d barzmap_db
```

### Method 2: Using SQL File

```bash
# Run your schema file
psql -U barzmap_user -d barzmap_db -f schema/database_setup.sql
```

---

## Running Your Schema

1. **Navigate to your project directory:**
   ```bash
   cd /Users/daniel/Documents/repo/BarzMap-server
   ```

2. **Run the setup script:**
   ```bash
   psql -U barzmap_user -d barzmap_db -f schema/database_setup.sql
   ```

   If you're using the default user:
   ```bash
   psql barzmap_db -f schema/database_setup.sql
   ```

3. **Verify the setup:**
   ```bash
   psql barzmap_db
   ```
   
   Then in psql:
   ```sql
   \dt  -- List all tables
   \d users  -- Describe the users table
   SELECT * FROM equipment;  -- View sample equipment data
   ```

---

## Basic PostgreSQL Commands

### Connecting to PostgreSQL

```bash
# Connect to default database
psql

# Connect to specific database
psql barzmap_db

# Connect with specific user
psql -U barzmap_user -d barzmap_db
```

### Inside psql (Interactive Commands)

```sql
-- List all databases
\l

-- Connect to a database
\c barzmap_db

-- List all tables
\dt

-- Describe a table structure
\d table_name

-- List all schemas
\dn

-- Show current database
SELECT current_database();

-- Show current user
SELECT current_user;

-- Exit psql
\q
```

### Common SQL Operations

```sql
-- Select data
SELECT * FROM users;
SELECT name, email FROM users WHERE role = 'admin';

-- Insert data
INSERT INTO users (auth0_id, email, name) 
VALUES ('auth0|123', 'user@example.com', 'John Doe');

-- Update data
UPDATE users SET name = 'Jane Doe' WHERE email = 'user@example.com';

-- Delete data
DELETE FROM users WHERE email = 'user@example.com';

-- Count records
SELECT COUNT(*) FROM parks WHERE status = 'approved';

-- Join tables
SELECT p.name, e.name as equipment_name
FROM parks p
JOIN park_equipment pe ON p.id = pe.park_id
JOIN equipment e ON pe.equipment_id = e.id;
```

---

## Connecting from Python

### Environment Variables

Create a `.env` file in your project root:

```env
DATABASE_URL=postgresql://barzmap_user:your_password@localhost:5432/barzmap_db
```

Or with individual components:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=barzmap_db
DB_USER=barzmap_user
DB_PASSWORD=your_password
```

### Using psycopg (Already in requirements.txt)

```python
import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to database
conn = psycopg.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "barzmap_db"),
    user=os.getenv("DB_USER", "barzmap_user"),
    password=os.getenv("DB_PASSWORD")
)

# Create a cursor with dict-like rows
cur = conn.cursor(row_factory=dict_row)

# Execute a query
cur.execute("SELECT * FROM users WHERE role = %s", ("admin",))
users = cur.fetchall()

# Execute with parameters (prevents SQL injection)
cur.execute(
    "INSERT INTO parks (name, latitude, longitude) VALUES (%s, %s, %s)",
    ("Central Park", 40.785091, -73.968285)
)
conn.commit()

# Close connections
cur.close()
conn.close()
```

### Using SQLAlchemy (Also in requirements.txt)

```python
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Create engine
engine = create_engine(os.getenv("DATABASE_URL"))

# Execute queries
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users"))
    for row in result:
        print(row)
```

---

## Useful Tips

### 1. Backup Your Database

```bash
# Create a backup
pg_dump barzmap_db > backup.sql

# Restore from backup
psql barzmap_db < backup.sql
```

### 2. Reset Your Database

```bash
# Drop and recreate
dropdb barzmap_db
createdb barzmap_db
psql barzmap_db -f schema/database_setup.sql
```

### 3. View Running Queries

```sql
-- In psql
SELECT pid, usename, query, state 
FROM pg_stat_activity 
WHERE datname = 'barzmap_db';
```

### 4. Check Table Sizes

```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 5. Common Issues

**Issue: "password authentication failed"**
- Check your password in the connection string
- Verify the user exists: `SELECT * FROM pg_user;`

**Issue: "database does not exist"**
- List databases: `\l` in psql
- Create it: `createdb barzmap_db`

**Issue: "permission denied"**
- Grant permissions: `GRANT ALL PRIVILEGES ON DATABASE barzmap_db TO barzmap_user;`

---

## Next Steps

1. ✅ Install PostgreSQL
2. ✅ Create database and user
3. ✅ Run your schema
4. ✅ Test connection from Python
5. 🔄 Set up connection pooling for production
6. 🔄 Add database migrations (consider Alembic)
7. 🔄 Set up database backups

---

## Resources

- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
- [psycopg Documentation](https://www.psycopg.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

