-- ==============================================================================
-- KebunData / Robot People Threads Engagement v2 Database Schema
-- File: infrastructure/schema_v2.sql
-- ==============================================================================

-- 1. Persistent Author Memory Table
CREATE TABLE IF NOT EXISTS threads_authors (
    author_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_engaged_at TIMESTAMP,
    engagement_count INT DEFAULT 0,
    last_topic VARCHAR(255),
    relationship_status VARCHAR(50) DEFAULT 'PROSPECT'
);

CREATE INDEX IF NOT EXISTS idx_threads_authors_username ON threads_authors(username);
CREATE INDEX IF NOT EXISTS idx_threads_authors_last_engaged ON threads_authors(last_engaged_at);

-- 2. Comprehensive Outbound Engagement Analytics & Audit Log
CREATE TABLE IF NOT EXISTS threads_outbound_logs (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(255),
    post_id VARCHAR(255),
    author_id VARCHAR(255),
    username VARCHAR(255),
    original_post TEXT,
    matched_topic VARCHAR(255),
    scout_decision VARCHAR(50),
    relevance_score INT DEFAULT 0,
    conversation_score INT DEFAULT 0,
    value_score INT DEFAULT 0,
    risk_score INT DEFAULT 0,
    final_score INT DEFAULT 0,
    reply_type VARCHAR(100),
    draft_reply TEXT,
    approval_status VARCHAR(50) DEFAULT 'PENDING',
    approved_by_telegram_user_id BIGINT,
    approval_claimed_at TIMESTAMPTZ,
    approved_reply TEXT,
    publish_status VARCHAR(50) DEFAULT 'UNPUBLISHED',
    threads_reply_id VARCHAR(255),
    error_code VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ensure v2 columns are added if table already existed from v1
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS execution_id VARCHAR(255);
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS post_id VARCHAR(255);
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS author_id VARCHAR(255);
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS original_post TEXT;
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS matched_topic VARCHAR(255);
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS scout_decision VARCHAR(50);
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS relevance_score INT DEFAULT 0;
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS conversation_score INT DEFAULT 0;
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS value_score INT DEFAULT 0;
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS risk_score INT DEFAULT 0;
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS final_score INT DEFAULT 0;
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS reply_type VARCHAR(100);
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS draft_reply TEXT;
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'PENDING';
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS approved_by_telegram_user_id BIGINT;
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS approval_claimed_at TIMESTAMPTZ;
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS approved_reply TEXT;
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS publish_status VARCHAR(50) DEFAULT 'UNPUBLISHED';
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS threads_reply_id VARCHAR(255);
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS error_code VARCHAR(100);
ALTER TABLE threads_outbound_logs ADD COLUMN IF NOT EXISTS error_message TEXT;

CREATE INDEX IF NOT EXISTS idx_threads_outbound_post_id ON threads_outbound_logs(post_id);
CREATE INDEX IF NOT EXISTS idx_threads_outbound_author_id ON threads_outbound_logs(author_id);
CREATE INDEX IF NOT EXISTS idx_threads_outbound_status ON threads_outbound_logs(approval_status, publish_status);
CREATE INDEX IF NOT EXISTS idx_threads_outbound_created_at ON threads_outbound_logs(created_at);

-- 3. Fix auto-increment sequence for primary key if needed
CREATE SEQUENCE IF NOT EXISTS threads_outbound_logs_id_seq;
SELECT setval('threads_outbound_logs_id_seq', COALESCE((SELECT MAX(id) FROM threads_outbound_logs), 0) + 1, false);
ALTER TABLE threads_outbound_logs ALTER COLUMN id SET DEFAULT nextval('threads_outbound_logs_id_seq');
ALTER SEQUENCE threads_outbound_logs_id_seq OWNED BY threads_outbound_logs.id;
