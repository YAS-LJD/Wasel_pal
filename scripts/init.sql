-- ================================================
-- Wasel Palestine - Database Init (PostgreSQL)
-- ================================================

-- ENUMS
CREATE TYPE user_role AS ENUM ('citizen', 'moderator', 'admin');
CREATE TYPE checkpoint_type AS ENUM ('military', 'commercial', 'internal');
CREATE TYPE checkpoint_status AS ENUM ('open', 'closed', 'delayed', 'restricted');
CREATE TYPE incident_category AS ENUM ('closure', 'delay', 'accident', 'weather_hazard', 'military_activity', 'other');
CREATE TYPE incident_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE incident_status AS ENUM ('active', 'verified', 'resolved', 'rejected');
CREATE TYPE report_category AS ENUM ('checkpoint', 'road_closure', 'delay', 'accident', 'weather', 'other');
CREATE TYPE report_status AS ENUM ('pending', 'accepted', 'rejected', 'duplicate');
CREATE TYPE vote_type AS ENUM ('up', 'down');
CREATE TYPE route_strategy AS ENUM ('fastest', 'safest', 'balanced');

-- USERS
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

-- REFRESH TOKENS
CREATE TABLE refresh_tokens (
    id         SERIAL PRIMARY KEY,
    user_id    INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked    BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CHECKPOINTS
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

-- CHECKPOINT STATUS HISTORY
CREATE TABLE checkpoint_status_history (
    id            SERIAL PRIMARY KEY,
    checkpoint_id INT NOT NULL REFERENCES checkpoints(id),
    old_status    checkpoint_status,
    new_status    checkpoint_status NOT NULL,
    changed_by    INT REFERENCES users(id),
    reason        VARCHAR(255),
    changed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INCIDENTS
CREATE TABLE incidents (
    id            SERIAL PRIMARY KEY,
    checkpoint_id INT REFERENCES checkpoints(id),
    title         VARCHAR(200) NOT NULL,
    description   TEXT,
    category      incident_category NOT NULL,
    severity      incident_severity DEFAULT 'medium',
    status        incident_status DEFAULT 'active',
    latitude      DECIMAL(9,6),
    longitude     DECIMAL(9,6),
    region        VARCHAR(100),
    reported_by   INT REFERENCES users(id),
    verified_by   INT REFERENCES users(id),
    cluster_id    INT,
    starts_at     TIMESTAMP,
    ends_at       TIMESTAMP,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- REPORTS
CREATE TABLE reports (
    id           SERIAL PRIMARY KEY,
    user_id      INT NOT NULL REFERENCES users(id),
    latitude     DECIMAL(9,6) NOT NULL,
    longitude    DECIMAL(9,6) NOT NULL,
    category     report_category NOT NULL,
    description  TEXT,
    status       report_status DEFAULT 'pending',
    confidence   FLOAT DEFAULT 0.5,
    incident_id  INT REFERENCES incidents(id),
    upvotes      INT DEFAULT 0,
    downvotes    INT DEFAULT 0,
    moderated_by INT REFERENCES users(id),
    moderated_at TIMESTAMP,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- REPORT VOTES
CREATE TABLE report_votes (
    id         SERIAL PRIMARY KEY,
    report_id  INT NOT NULL REFERENCES reports(id),
    user_id    INT NOT NULL REFERENCES users(id),
    vote       vote_type NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (report_id, user_id)
);

-- ALERT SUBSCRIPTIONS
CREATE TABLE alert_subscriptions (
    id         SERIAL PRIMARY KEY,
    user_id    INT NOT NULL REFERENCES users(id),
    region     VARCHAR(100),
    category   VARCHAR(50),
    is_active  BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ALERTS
CREATE TABLE alerts (
    id          SERIAL PRIMARY KEY,
    incident_id INT NOT NULL REFERENCES incidents(id),
    region      VARCHAR(100),
    category    VARCHAR(50),
    message     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ROUTE CACHE
CREATE TABLE route_cache (
    id         SERIAL PRIMARY KEY,
    cache_key  VARCHAR(255) UNIQUE NOT NULL,
    origin_lat DECIMAL(9,6),
    origin_lng DECIMAL(9,6),
    dest_lat   DECIMAL(9,6),
    dest_lng   DECIMAL(9,6),
    strategy   route_strategy,
    response   JSON NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- WEATHER CACHE
CREATE TABLE weather_cache (
    id         SERIAL PRIMARY KEY,
    region     VARCHAR(100) NOT NULL,
    data       JSON NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SEED DATA
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@wasel.ps', '$2b$12$placeholder_hash', 'admin');
