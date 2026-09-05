# ?? KebunData AI SaaS Platform

This repository serves as the central command center for hosting and managing our **Workflow-as-a-Service (SaaS)** platform on Oracle Cloud Infrastructure (OCI). We specialize in B2B AI Agent automation (e.g., Threads Engagement Agents).

## ??? System Architecture

Our stack is fully Dockerized on an OCI Ampere A1 (ARM) instance and heavily relies on seamless integration between Odoo and n8n.

* **Odoo 18 (kebundata.my):** The ERP, CRM, and storefront. Handles client subscriptions, billing, and the white-labeled client dashboard.
* **n8n (
8n.kebundata.my):** The workflow orchestration engine. Upgraded to PostgreSQL for enterprise-level multi-client concurrency.
* **Ollama & Hermes:** Local AI model hosting for high-privacy, cost-effective inference.
* **Nginx Proxy Manager:** The secure gateway routing external traffic to the correct Docker containers via HTTPS.

*(For detailed architectural decisions and the multi-tenancy strategy, see docs/saas_architecture_plan.md).*

## ?? Repository Structure

- docs/: Technical specifications, architecture plans, and changelogs.
- workflows/templates/: Baseline n8n workflow JSON files (e.g., Threads Engagement Agent).
- workflows/clients/: Client-specific workflow configurations.
- infrastructure/docker/: Docker Compose configurations and deployment scripts.
- gents/prompts/: Master system prompts and personas used by the AI agents.

## ?? Recent Milestones

- **2026-09-05:** Successfully executed the OCI "Boot Volume Rescue" protocol to restore server access and inject new SSH keys.
- **2026-09-05:** Upgraded n8n from SQLite to PostgreSQL (using the Odoo database container) to prevent database locks during high-traffic client workflow executions.
- **2026-09-05:** Drafted the initial SaaS Multi-Tenancy Architecture Plan.

## ?? Security Best Practices

1. **Zero Secrets in Source Control:** Do not push .env, .pem, .key, or any files containing API keys, database passwords, or n8n credentials to this repository.
2. **Key-Based SSH Access:** The OCI instance is strictly locked down to specific SSH keys.
3. **No Direct Client Canvas Access:** Clients never interact directly with the n8n canvas; all interactions are routed through secure Odoo webhooks and portals to prevent accidental breakages.
