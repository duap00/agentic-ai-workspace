# Abu security operations

Abu is the local security advisor for Robot People Industries. Abu interprets evidence from security tools and proposes remediation; Abu is not the security control itself.

## Evidence sources

| Area | Evidence to collect |
| --- | --- |
| GitHub | Secret scanning, Dependabot alerts, pull-request diffs and branch protection |
| Repository | Gitleaks, dependency checks and workflow JSON validation |
| OCI | Firewall rules, open ports, package status, disk capacity, backups and restore tests |
| Containers | Trivy findings, image age, running service inventory and container health |
| n8n | Failed executions, webhook authentication, credential references and publishing gates |
| Public services | TLS, security headers and approved non-intrusive external exposure checks |

## Operating cycle

1. Collect read-only evidence.
2. Run deterministic checks.
3. Have Abu assess severity and impact.
4. Send Ahmad a concise report with remediation options.
5. Apply production changes only after explicit approval.
6. Verify the result and record what changed.

## Required guardrails

- Do not send raw logs or secrets to an external model.
- Restrict active scanning to Robot People assets Ahmad has authorized.
- Do not run destructive security tests in production.
- Treat a security report as advisory until a deterministic check confirms it.
- Keep a restore-tested backup before material infrastructure changes.

## Initial weekly report

The first report should cover:

- New GitHub secret or dependency alerts
- Repository secret scan results
- n8n workflow failures and inactive publishing controls
- OCI open ports, disk capacity and pending updates
- Container image vulnerabilities
- Backup freshness and last successful restore test
