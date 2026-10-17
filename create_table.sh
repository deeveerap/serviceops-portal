#!/bin/bash

# Configuration variables matching your Docker setup
CONTAINER_NAME="postgres"
DB_USER="serviceops"
DB_NAME="serviceops"

echo "=============================================="
echo "Initializing ServiceOps Database Schemas..."
echo "=============================================="

# Execute SQL directly inside the container via stdin
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" << 'EOF'

-- 1. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create Requests Table
CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    request_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_by INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create Approvals Table
CREATE TABLE IF NOT EXISTS approvals (
    id SERIAL PRIMARY KEY,
    request_id INTEGER REFERENCES requests(id),
    approved_by INTEGER REFERENCES users(id),
    approval_status VARCHAR(50),
    comments TEXT,
    approved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create Audit Log Table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    action VARCHAR(100),
    entity_type VARCHAR(100),
    entity_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Create Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    request_id INTEGER REFERENCES requests(id),
    recipient VARCHAR(200),
    message TEXT,
    status VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

EOF

if [ $? -eq 0 ]; then
    echo "=============================================="
    echo "✅ Success! All tables provisioned successfully."
    echo "=============================================="
else
    echo "=============================================="
    echo "❌ Error: Failed to execute database migrations."
    echo "=============================================="
fi
