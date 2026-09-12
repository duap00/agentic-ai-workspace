-- Disposable PostgreSQL regression test. All objects are session-local.
\set ON_ERROR_STOP on
BEGIN;
CREATE TEMP TABLE threads_outbound_logs (
id integer PRIMARY KEY, post_id text,draft_reply text,approval_status text,publish_status text,
approved_by_telegram_user_id bigint,approval_claimed_at timestamptz,approval_expires_at timestamptz,
approval_execution_id text,approved_reply text,threads_container_id text,publish_attempted_at timestamptz,
published_at timestamptz,threads_reply_id text,error_code text,error_message text,author_id text,username text,matched_topic text
);
CREATE TEMP TABLE threads_authors(author_id text PRIMARY KEY,username text,last_engaged_at timestamptz,engagement_count integer,last_topic text);
INSERT INTO threads_outbound_logs(id,post_id,draft_reply,approval_status,publish_status,approval_expires_at)
SELECT id,'42','Saved draft','PENDING_HUMAN_APPROVAL','UNPUBLISHED',
CASE WHEN id=2 THEN CURRENT_TIMESTAMP-INTERVAL '1 second' WHEN id=3 THEN NULL ELSE CURRENT_TIMESTAMP+INTERVAL '1 day' END
FROM generate_series(1,5) id;
UPDATE threads_outbound_logs SET draft_reply=' ' WHERE id=4;
PREPARE claim(text,bigint,integer,text) AS UPDATE pg_temp.threads_outbound_logs
SET approval_status=CASE WHEN $1='approve' THEN 'APPROVAL_CLAIMED' ELSE 'REJECTED_BY_HUMAN' END,
publish_status=CASE WHEN $1='approve' THEN 'PUBLISHING' ELSE 'REJECTED' END,
approved_by_telegram_user_id=$2, approval_claimed_at=CURRENT_TIMESTAMP,
approval_execution_id=$4,
approved_reply=CASE WHEN $1='approve' THEN draft_reply ELSE NULL END
WHERE id=$3 AND $1 IN ('approve','reject')
AND approval_status='PENDING_HUMAN_APPROVAL' AND publish_status='UNPUBLISHED'
AND approval_expires_at > CURRENT_TIMESTAMP
AND ($1='reject' OR (post_id ~ '^[1-9][0-9]*$' AND draft_reply ~ '[^[:space:]]'))
RETURNING *;
EXECUTE claim('approve',123,1,'first');
EXECUTE claim('approve',123,1,'duplicate');
EXECUTE claim('approve',123,2,'expired');
EXECUTE claim('approve',123,3,'missing-expiry');
EXECUTE claim('approve',123,4,'blank');
EXECUTE claim('reject',123,5,'reject');
DO $test$ BEGIN
IF NOT EXISTS(SELECT 1 FROM threads_outbound_logs WHERE id=1 AND approval_execution_id='first' AND approved_reply='Saved draft') THEN RAISE EXCEPTION 'Claim snapshot/ownership failed'; END IF;
IF EXISTS(SELECT 1 FROM threads_outbound_logs WHERE id IN (2,3,4) AND approval_status<>'PENDING_HUMAN_APPROVAL') THEN RAISE EXCEPTION 'Invalid approval claimed'; END IF;
IF NOT EXISTS(SELECT 1 FROM threads_outbound_logs WHERE id=5 AND publish_status='REJECTED') THEN RAISE EXCEPTION 'Rejection failed'; END IF;
END $test$;
PREPARE container(text,integer,text) AS UPDATE pg_temp.threads_outbound_logs SET threads_container_id=$1
WHERE id=$2 AND approval_execution_id=$3 AND approval_status='APPROVAL_CLAIMED' AND publish_status='PUBLISHING' AND threads_container_id IS NULL AND publish_attempted_at IS NULL
RETURNING threads_container_id AS id;
EXECUTE container('100',1,'wrong-execution');
EXECUTE container('101',1,'first');
EXECUTE container('102',1,'first');
DO $test$ BEGIN
IF NOT EXISTS(SELECT 1 FROM threads_outbound_logs WHERE id=1 AND threads_container_id='101') THEN RAISE EXCEPTION 'Container guard failed'; END IF;
END $test$;
PREPARE attempt(text,integer,text) AS UPDATE pg_temp.threads_outbound_logs SET publish_attempted_at=CURRENT_TIMESTAMP
WHERE id=$2 AND approval_execution_id=$3 AND approval_status='APPROVAL_CLAIMED' AND publish_status='PUBLISHING' AND threads_container_id=$1 AND publish_attempted_at IS NULL
RETURNING threads_container_id AS id;
EXECUTE attempt('101',1,'first');
EXECUTE attempt('101',1,'first');
PREPARE complete(text,integer,text) AS WITH updated AS (
UPDATE pg_temp.threads_outbound_logs SET approval_status='APPROVED_BY_HUMAN',publish_status='PUBLISHED',threads_reply_id=$1, published_at=CURRENT_TIMESTAMP
WHERE id=$2 AND approval_execution_id=$3 AND publish_attempted_at IS NOT NULL AND approval_status='APPROVAL_CLAIMED' AND publish_status='PUBLISHING'
RETURNING id,author_id,username,matched_topic
), author_update AS (
INSERT INTO pg_temp.threads_authors (author_id,username,last_engaged_at,engagement_count,last_topic)
SELECT COALESCE(author_id,username),username,CURRENT_TIMESTAMP,1,matched_topic FROM updated WHERE username IS NOT NULL
ON CONFLICT (author_id) DO UPDATE SET last_engaged_at=CURRENT_TIMESTAMP,engagement_count=threads_authors.engagement_count+1,last_topic=EXCLUDED.last_topic
RETURNING author_id
) SELECT id FROM updated;
EXECUTE complete('999',1,'wrong-execution');
DO $test$ BEGIN
IF EXISTS(SELECT 1 FROM threads_outbound_logs WHERE id=1 AND publish_status='PUBLISHED') THEN RAISE EXCEPTION 'Wrong execution completed publication'; END IF;
END $test$;
EXECUTE complete('201',1,'first');
DO $test$ BEGIN
IF NOT EXISTS(SELECT 1 FROM threads_outbound_logs WHERE id=1 AND publish_status='PUBLISHED' AND threads_reply_id='201' AND published_at IS NOT NULL) THEN RAISE EXCEPTION 'Publication evidence failed'; END IF;
END $test$;
INSERT INTO threads_outbound_logs(id,post_id,draft_reply,approval_status,publish_status,approval_expires_at)
VALUES(6,'43','Other draft','PENDING_HUMAN_APPROVAL','UNPUBLISHED',CURRENT_TIMESTAMP+INTERVAL '1 day');
EXECUTE claim('approve',123,6,'uncertain');
PREPARE uncertain(integer,text) AS UPDATE pg_temp.threads_outbound_logs
SET publish_status='PUBLISH_UNKNOWN',error_code='MANUAL_RECONCILIATION_REQUIRED',
error_message='Publication flow failed; verify external outcome before any retry.'
WHERE id=$1 AND approval_execution_id=$2 AND approval_status='APPROVAL_CLAIMED' AND publish_status='PUBLISHING'
RETURNING id;
EXECUTE uncertain(6,'uncertain');
EXECUTE claim('approve',123,6,'retry');
DO $test$ BEGIN
IF NOT EXISTS(SELECT 1 FROM threads_outbound_logs WHERE id=6 AND publish_status='PUBLISH_UNKNOWN' AND approval_execution_id='uncertain') THEN RAISE EXCEPTION 'Uncertain outcome became retryable'; END IF;
END $test$;
ROLLBACK;
SELECT 'Approval SQL regressions passed; all temporary writes rolled back' AS result;
