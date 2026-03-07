-- ================================================
-- Wasel Palestine — Database Init (PostgreSQL)
-- ================================================

-- ─── ENUMS (PostgreSQL يستخدم TYPE بدل ENUM inline)
CREATE TYPE user_role AS ENUM ('citizen', 'moderator', 'admin');
CREATE TYPE checkpoint_type AS ENUM ('military', 'commercial', 'internal');
CREATE TYPE checkpoint_status AS ENUM ('open', 'closed', 'delayed', 'restricted');

-- ─── USERS ──────────────────────────────────────
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          user_role DEFAULT 'citizen',
    reputation    FLOAT DEFAULT 1.0,
    total_reports INT DEFAULT 0,
    valid_reports INT DEFAULT 0,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── REFRESH TOKENS ─────────────────────────────
CREATE TABLE refresh_tokens (
    id         SERIAL PRIMARY KEY,
    user_id    INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked    BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── CHECKPOINTS ────────────────────────────────
CREATE TABLE checkpoints (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    name_ar     VARCHAR(100),
    latitude    DECIMAL(9,6) NOT NULL,
    longitude   DECIMAL(9,6) NOT NULL,
    region      VARCHAR(100),
    type        checkpoint_type DEFAULT 'military',
    status      checkpoint_status DEFAULT 'open',
    description TEXT,
    created_by  INT REFERENCES users(id),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── SEED DATA ───────────────────────────────────
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@wasel.ps', '$2b$12$placeholder_hash', 'admin');