-- SQLite Schema for Session Tracking & Management
-- Phase 3.1: Core session data storage with optimized indices
-- Features: WAL mode, ACID compliance, O(log n) queries, referential integrity

-- Sessions table (core session data)
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    pr_number INTEGER,
    branch TEXT,
    timestamp TEXT,  -- ISO 8601 format (e.g., '2026-06-23T02:34:59Z')
    git_sha TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'in-progress', 'complete', 'failed')),
    agent_name TEXT,
    duration_minutes INTEGER,
    lane_bucket TEXT,
    checkpoint_state TEXT,
    budget_remaining REAL,
    estimated_cost REAL,
    cost_score REAL,
    tool_name TEXT,
    tool_complete_call_id TEXT,
    usage_input_tokens INTEGER,
    usage_output_tokens INTEGER,
    credits REAL,
    blockers TEXT,
    checkpoint_markers TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id)
);

-- Session metadata (key-value pairs for extensibility)
-- Allows storing arbitrary metadata without schema migration
CREATE TABLE IF NOT EXISTS session_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    UNIQUE(session_id, key)
);

-- Session patterns (many-to-many: sessions -> patterns)
-- Tracks which patterns were applied in each session
CREATE TABLE IF NOT EXISTS session_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    pattern_id TEXT NOT NULL,
    pattern_name TEXT,
    success BOOLEAN DEFAULT 1,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Session outcomes (CI check results)
-- Aggregated CI/CD results for each session
CREATE TABLE IF NOT EXISTS session_outcomes (
    session_id TEXT PRIMARY KEY,
    ci_checks_green INTEGER DEFAULT 0,
    ci_checks_red INTEGER DEFAULT 0,
    ci_checks_total INTEGER DEFAULT 0,
    test_coverage REAL,  -- Percentage (0-100)
    linting_errors INTEGER DEFAULT 0,
    linting_warnings INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Session events (audit trail for detailed session tracking)
-- Tracks key events during session execution
CREATE TABLE IF NOT EXISTS session_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('start', 'pattern_applied', 'check_passed', 'check_failed', 'error', 'complete')),
    event_details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Performance indices for common query patterns
-- These indices provide O(log n) performance for typical queries

-- Query by timestamp and status (most common filter combination)
CREATE INDEX IF NOT EXISTS idx_timestamp_status ON sessions(timestamp DESC, status);

-- Query by PR number and branch (CI pipeline tracking)
CREATE INDEX IF NOT EXISTS idx_pr_number_branch ON sessions(pr_number, branch);

-- Query by agent name (agent performance tracking)
CREATE INDEX IF NOT EXISTS idx_agent_name ON sessions(agent_name);

-- Query by session ID (lookups)
CREATE INDEX IF NOT EXISTS idx_session_id ON sessions(session_id);

-- Query by creation time (recent sessions)
CREATE INDEX IF NOT EXISTS idx_created_at ON sessions(created_at DESC);

-- Query metadata efficiently
CREATE INDEX IF NOT EXISTS idx_metadata_session_key ON session_metadata(session_id, key);

-- Query patterns by session
CREATE INDEX IF NOT EXISTS idx_patterns_session ON session_patterns(session_id);

-- Query events by session and timestamp
CREATE INDEX IF NOT EXISTS idx_events_session_time ON session_events(session_id, timestamp DESC);

-- Query outcomes by session
CREATE INDEX IF NOT EXISTS idx_outcomes_session ON session_outcomes(session_id);

-- Covering indices for performance (include frequently selected columns)
-- Allows index-only scans without accessing main table
CREATE INDEX IF NOT EXISTS idx_sessions_status_created ON sessions(status, created_at DESC);

-- SQLite Performance Optimizations
-- Enable Write-Ahead Logging for concurrent access
PRAGMA journal_mode = WAL;

-- Balance between durability and performance
PRAGMA synchronous = NORMAL;

-- Increase cache size to 64MB for better performance
PRAGMA cache_size = -64000;

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Journal size limit: 10MB
PRAGMA wal_autocheckpoint = 10000;

-- Enable query optimizer
PRAGMA optimize;
