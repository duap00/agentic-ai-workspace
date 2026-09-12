-- Run against the database used by the approval handler's PostgreSQL credential.
-- Additive and repeatable. Existing pending approvals intentionally remain blocked:
-- do not backfill expiry, renew old approvals, or reset consumed records.
BEGIN;
ALTER TABLE public.threads_outbound_logs
  ADD COLUMN IF NOT EXISTS approved_by_telegram_user_id BIGINT,
  ADD COLUMN IF NOT EXISTS approval_claimed_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS approval_expires_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS approval_execution_id TEXT,
  ADD COLUMN IF NOT EXISTS threads_container_id TEXT,
  ADD COLUMN IF NOT EXISTS publish_attempted_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS published_at TIMESTAMPTZ;
COMMIT;
