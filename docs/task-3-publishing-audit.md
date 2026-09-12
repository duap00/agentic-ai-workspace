# Task 3 publishing audit — 2026-09-13

## Verdict

Do not activate the Threads publishing workflows yet. The repository has three direct publishing routes without human approval, and the shared approval handler needs additional work. This was a read-only production audit; no workflow, database record, credential, or activation state was changed and no messages or posts were sent.

## Evidence and scope

Inspected the five repository workflow templates, `infrastructure/schema_v2.sql`, and workflow operations instructions. Read the live workflow inventory, node types, connections, approval claim SQL, expiry-related code indicators, and table metadata from the n8n database in `odoo18-db-1`. Also inspected the installed n8n Telegram node output handling. Ran isolated JavaScript fixtures locally, without network calls.

| Component | Repository | Live n8n observation |
| --- | --- | --- |
| Autopost | Inactive; direct publisher | Absent from the full workflow inventory |
| Autoreply | Inactive; direct publisher | Absent from the full workflow inventory |
| Content Factory | Inactive; direct publisher | Present, inactive; same direct publishing route; webhook has no configured authentication |
| Outbound Engager | Inactive; stores draft before approval card | Present, inactive; same storage-to-card route |
| Approval Handler | Inactive; atomic record claim | Present, inactive; same claim and callback routing |

The security report is the only active workflow in the inspected instance. Inactivity prevents scheduled/production webhook execution but does not make a manually executed publisher safe.

This is a structural comparison, not certification of byte-for-byte deployment equality. Live Content Factory HTTP nodes use credential authentication, unlike the older repository template. Runtime credential secrets were not read. In particular, the database selected by the saved publishing credential was not decrypted or independently verified; schema observations below refer specifically to the inspected `n8n.public.threads_outbound_logs` table. Other hosts, host-side publishing scripts, and untracked `ali-social-automation/` are outside this audit.

## Findings

### F1 — High: three workflows bypass human approval

In `kebundata-threads-autopost.json`, `kebundata-threads-autoreply.json`, and `kebundata-threads-content-factory.json`, the successful output of `Is Safe for Meta Policy?` connects directly to container creation, wait, and publish. No PostgreSQL approval record or human callback intervenes. A model response of `PASS` is sufficient to reach publishing if executed with working credentials. The Content Factory route is also present in live n8n.

Remediation: make these workflows draft producers and route each proposed publication through a shared approval publisher. The current publisher requires `post_id` and always sends `reply_to_id`, so it cannot simply be reused for standalone posts without an explicit post/reply contract.

### F2 — High: approval expiry is absent

`Claim Pending Approval` checks only record ID, pending approval status, and unpublished status. Neither its SQL nor `Validate Stored Approval` checks age or expiry. The repository schema and inspected live table have no approval-expiry column. Live claim SQL matches the repository and the live code nodes have no expiry/created-at references.

Local fixture: a claimed row created in 2020 passes `Validate Stored Approval`. The SQL has no age condition to prevent claiming such a pending row. Earlier conversation claims that expiry was already implemented were incorrect.

Remediation: set expiry when storing the draft and enforce it in the atomic claim; test the boundary and expired callbacks.

### F3 — High: live claim SQL and inspected schema disagree

The deployed claim sets `approved_by_telegram_user_id` and `approval_claimed_at`. Both columns exist in the versioned schema, but neither exists in the inspected live table. The claim will fail against that table. Confirm the saved PostgreSQL credential's actual target before applying a migration.

Remediation: verify database/schema targeting, then deploy a reviewed additive migration and verify column availability before enabling the handler.

### F4 — High: callback acknowledgement loses approval context

Both repository and live connections are `Validate Stored Approval -> Answer Telegram Callback -> Is Approved?`. The IF reads `$json.action`, while the installed Telegram implementation outputs the Telegram API response, not the original approval item. A normal acknowledgement `{ok:true,result:true}` has no `action`. Approval therefore takes the false/rejection route; creation also reads configuration and draft fields from the current item, which the acknowledgement does not preserve.

Remediation: branch on explicit validated-node data and restore that data before publishing, or move acknowledgement to an independent branch. Verify approve and reject paths with a mocked Telegram response.

### F5 — High: Content Factory webhook is unauthenticated and defaults missing input

`Instant Webhook / API Trigger` has no authentication setting in the repository or live node. `Parse Topic & Input Context` substitutes a default topic and context when missing, and the graph leads to direct publication. This becomes an unauthenticated publishing entry point if activated with valid credentials. Input preservation through the preceding Set node also needs verification.

Remediation: authenticate requests, require explicit valid input, and store generated content for human review. Do not let missing inputs silently become publishable content.

### F6 — Medium: repository templates carry secrets through workflow data

Autopost, Autoreply, and Content Factory use Set-node `threadsAccessToken` and `geminiApiKey` values from `$vars`, then propagate tokens into item data and request parameters. This risks storing secrets in execution history. Live Content Factory already has credential-authenticated HTTP nodes, so the repository does not accurately represent that improvement.

Remediation: use n8n Credentials throughout and remove secrets from item JSON. This finding concerns secret handling design; it does not claim a live token was found in Git.

### F7 — Medium: duplicate prevention does not span approval records

The handler atomically claims a single record, which prevents two claims of the same pending row. However, `threads_outbound_logs.post_id` has only a non-unique index in both the schema and live table. Outbound filters read workflow static-data author/post caches; the inspected workflow does not update those caches after publication or consult PostgreSQL author memory when filtering. Separate records for the same target can therefore be approved independently. Autoreply also marks comment IDs processed before successful publication and uses a bounded static-data cache.

Remediation: define a business idempotency key and enforce it in PostgreSQL; use database-backed pending/published status and author cooldown checks. Do not describe the current record claim as complete duplicate-publication protection.

### F8 — Medium: failed claims/publications lack a recovery record

The handler sets `APPROVAL_CLAIMED/PUBLISHING` before validating stored data or calling Threads. There is no explicit error branch to record failed or uncertain publication, nor a durable container ID before the publish call. Failures can strand rows; successful external publishing followed by database failure creates uncertainty.

Remediation: validate required data as part of claiming, persist intermediate evidence, and distinguish definite failure from uncertain external outcome. Reconcile uncertain outcomes before retrying publication.

### F9 — Medium: outbound score validation permits missing risk

`Deterministic Opportunity Scoring1` uses `scoutResult.risk_score || 0` and does not validate numeric types or ranges. A local fixture with `decision: REPLY`, four scores of 100, and no risk score qualifies. The human approval gate still follows this stage, but malformed model output can pass the intended risk screen.

Remediation: validate required score fields and ranges; malformed or incomplete model output must fail the screening stage.

## Checks completed

- All five repository workflows parse as JSON and their Code-node JavaScript compiles.
- All five templates have `active: false`.
- Wrong reviewer and malformed callback fixtures emit no items; a correctly configured callback emits one item.
- Blank draft, invalid target, and consumed-state fixtures are rejected by the stored-approval validator.
- An old claimed draft is accepted: expiry defect reproduced.
- Telegram acknowledgement lacks the approval action: routing defect supported by installed node implementation.
- A scout response missing risk score qualifies: reproduced.
- Outbound stores and verifies the exact draft before constructing the approval card; database insertion failure does not continue.
- Container and published-ID validation nodes exist in the handler.

These are local code/graph checks, not a successful end-to-end publisher test. No SQL mutations, external publishing calls, or Telegram calls were executed. Concurrency, approval-message-to-draft immutability, credential identity, published-version equality, and network failure reconciliation remain to be tested during implementation.

## Implementation order

1. Verify the target database, add approval expiry and required audit columns, and define post/reply records and idempotency keys.
2. Repair callback data routing and claim validation; add durable error and uncertain-outcome handling.
3. Convert Autopost, Autoreply, and Content Factory to authenticated draft/approval flows with credential-backed requests.
4. Add database-backed duplicate/cooldown checks and strict model-output validation to Outbound.
5. Run mocked approval, expiry, concurrency, and API-failure scenarios; review the diff and prepare a PR.
6. Deploy reviewed changes with a rollback export. Keep activation and any live publication under named-human control.
