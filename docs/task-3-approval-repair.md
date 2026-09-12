# Task 3: shared approval-handler repair

## Change and scope

This first repair addresses audit findings F2, F4, and the schema migration needed for F3. It adds recovery evidence for F8 but does not eliminate the need to reconcile external API results after an outage. Autopost, Autoreply, and Content Factory are not hardened by this change and must remain inactive.

New outbound approval records expire after 24 hours. The SQL claim rejects expired or missing expiry values and incomplete approval drafts before consuming them. Existing rows without expiry are deliberately not renewed. The claim records the execution owner and copies the text to `approved_reply`; publication uses that snapshot.

After Telegram acknowledgement, the handler explicitly restores the validated approval data. Both successful acknowledgements and acknowledgement errors therefore retain the approve/reject decision and target configuration.

Before publication the handler persists the container ID and a single publish-attempt timestamp. Guarded writes require the claiming execution. HTTP and validation failures take an error output to `PUBLISH_UNKNOWN` and never proceed to the success notification. Automatic node retries are disabled on these steps. If PostgreSQL itself is unavailable, failure recording may also fail: the row remains claimed/PUBLISHING and must be reconciled, not reset. A container-creation error is conservatively classified as unknown as well.

## Deployment gates

1. Verify the actual database selected by every assigned PostgreSQL credential. The audit inspected the `n8n` database but did not decrypt the saved credential to prove its target.
2. Back up the relevant table schema and workflow exports. Run `infrastructure/migrations/003_approval_lifecycle.sql` on the verified target. It is additive and does not backfill old approvals.
3. Import the two reviewed inactive workflows. Assign the saved credential to the new PostgreSQL nodes (`Persist Container ID`, `Record Publish Attempt`, `Record Uncertain Publication`) as well as existing nodes. Configure the named reviewer, chat, Threads account, and webhook authentication.
4. Generate fresh approval cards only after the updated producer is installed. Old cards with null expiry cannot publish. The 24-hour duration is an initial policy choice that can be changed explicitly in the producer.
5. Test approve/reject routing in a non-publishing environment with Telegram acknowledgement fixtures. Verify credentials and published versions independently before activation.
6. Continue the remaining Task 3 repairs before enabling any production publisher. A real Threads publication still requires the named human's explicit approval of the content.

No production workflow or schema was changed in preparing this patch. The repository templates are inactive and contain no deployed credential references.

## Verification

Run `node --test tests/approval-handler.test.cjs` for JavaScript, graph, claim validation, acknowledgement context, and error-routing tests.

Run `psql -X -v ON_ERROR_STOP=1 -f tests/approval-handler.postgres.sql` against a PostgreSQL test connection. This fixture creates session-local temporary tables and rolls all writes back. It exercises the workflow's SQL for expiry, missing expiry, blank drafts, same-record repeated claims, execution ownership, durable container IDs, single publish attempts, successful completion evidence, rejection, and blocking uncertain outcomes. It is a sequential regression test, not a concurrent-session load test.

Both test sets passed during preparation. No Telegram or Threads request was made.

## Remaining Task 3 work

- Remove the three direct publishing routes and authenticate Content Factory input.
- Introduce a post/reply contract suitable for standalone posts.
- Enforce PostgreSQL uniqueness across separate approval records and author cooldowns.
- Bind approval cards to immutable stored content/target versions.
- Reject malformed model scores and remove credentials from item JSON.
- Test concurrent claims, n8n import/runtime behaviour, and reconciliation after external publication succeeds but the database update fails.
