# Threads workflow operations

## Before import

Create the required credentials in n8n. Credentials are environment-specific and are intentionally not included in these workflow templates.

| Integration | Recommended n8n credential |
| --- | --- |
| Threads API | Query Auth with parameter name `access_token` |
| Gemini API | Header Auth with header name `x-goog-api-key` |
| Telegram | Telegram API |
| PostgreSQL | PostgreSQL credential with access only to the workflow schema |

After importing, connect each node to its saved credential. Configure non-secret values such as the Threads user ID and Telegram chat ID as n8n variables or explicit deployment configuration.

## Approval contract

The outbound workflow must:

1. Generate and safety-check a draft.
2. Store the exact draft and target post ID in PostgreSQL.
3. Send an approval card that identifies the stored approval record.

The publisher must:

1. Accept only a correctly formatted approval callback.
2. Load the referenced record using a parameterized query.
3. Require a nonblank draft, a valid target post ID and a pending/unpublished state.
4. Publish only after a valid human approval.
5. Record the final publish result.

## Activation checklist

- Confirm all credentials authenticate successfully.
- Authenticate the Telegram webhook and verify the approved reviewer identity.
- Test missing, malformed, rejected and repeated callbacks.
- Verify a failure from Threads does not report success.
- Verify database state changes are atomic enough to prevent duplicate publishing.
- Obtain explicit approval before enabling production triggers.

## Deployment status

The repository does not establish production status. Validate deployed n8n versions, credentials, workflow state and cloud firewall rules separately.
