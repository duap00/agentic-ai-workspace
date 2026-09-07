# 🌿 KebunData AI SaaS Platform

This repository serves as the central command center for hosting and managing our **Workflow-as-a-Service (SaaS)** platform on Oracle Cloud Infrastructure (OCI). We specialize in B2B AI Agent automation (e.g., Threads Engagement Agents).

## 🏗️ System Architecture

Our stack is fully Dockerized on an OCI Ampere A1 (ARM) instance and heavily relies on seamless integration between Odoo and n8n.

* **Odoo 18 (kebundata.my):** The ERP, CRM, and storefront. Handles client subscriptions, billing, and the white-labeled client dashboard.
* **n8n (n8n.kebundata.my):** The workflow orchestration engine. Upgraded to PostgreSQL for enterprise-level multi-client concurrency.
* **Ollama & Hermes:** Local AI model hosting for high-privacy, cost-effective inference.
* **Nginx Proxy Manager:** The secure gateway routing external traffic to the correct Docker containers via HTTPS.

*(For detailed architectural decisions and the multi-tenancy strategy, see `docs/saas_architecture_plan.md`).*

## 📁 Repository Structure

- `docs/`: Technical specifications, architecture plans, and changelogs.
- `workflows/`: Baseline n8n workflow JSON files for Threads automation and client workflows.
- `workflows/templates/`: Template workflow JSON configurations.
- `workflows/clients/`: Client-specific workflow configurations.
- `infrastructure/docker/`: Docker Compose configurations and deployment scripts.
- `skills/`: Python client utilities (e.g., `threads_client.py`).

## 🚀 KebunData Threads Automation Workflows

The repository includes four specialized n8n automation workflows located in `workflows/`:

| Workflow JSON File | Purpose |
| :--- | :--- |
| [`kebundata-threads-token-setup.json`](workflows/kebundata-threads-token-setup.json) | 🔑 **Initial Setup & Token Exchanger** (Exchanges short-lived token to 60-day token & fetches `THREADS_USER_ID`). |
| [`kebundata-threads-outbound-engager.json`](workflows/kebundata-threads-outbound-engager.json) | 🎯 **Replying to random prospect posts** in your niche to get outbound engagement. |
| [`kebundata-threads-autoreply.json`](workflows/kebundata-threads-autoreply.json) | 💬 **Replying to comments on YOUR OWN posts** (Inbound engagement responder). |
| [`kebundata-threads-autopost.json`](workflows/kebundata-threads-autopost.json) | 📢 **Automated scheduled posting** at peak hours (8am, 12pm, 8pm). |
| [`kebundata-threads-content-factory.json`](workflows/kebundata-threads-content-factory.json) | ⚡ **Webhook trigger** for instant custom content generation & publishing. |

### Key Features & Safety Mechanisms
- **Niche Prospecting**: Searches Threads for niche keywords (*pokok cili*, *fertigasi*, *baja AB*, *hidroponik*, etc.) and selects fresh candidate posts.
- **Human Voice & Conversation Extender**: Generates helpful 2-3 sentence agronomy tips ending with an engaging question.
- **Meta Policy & Anti-Ban Shield**: Every generated post/reply undergoes a Gemini policy audit check (strictly verifying no external links/URLs, no hard sell, no toxic speech, and no illegal pesticide claims).
- **Human Jitter & Rate Pacing**: Introduces randomized delays (15–90s) between actions to maintain a natural posting cadence.

## 📅 Recent Milestones

- **2026-09-05:** Configured and updated Threads API credentials (`THREADS_APP_ID`, `THREADS_APP_SECRET`) and integrated Meta Policy Anti-Ban Shield across all Threads workflow JSON files.
- **2026-09-05:** Successfully executed the OCI "Boot Volume Rescue" protocol to restore server access and inject new SSH keys.
- **2026-09-05:** Upgraded n8n from SQLite to PostgreSQL (using the Odoo database container) to prevent database locks during high-traffic client workflow executions.
- **2026-09-05:** Drafted the initial SaaS Multi-Tenancy Architecture Plan.

## 🔒 Security Best Practices

1. **Zero Secrets in Source Control:** Do not push `.env`, `.pem`, `.key`, or any files containing API keys, database passwords, or n8n credentials to this repository.
2. **Key-Based SSH Access:** The OCI instance is strictly locked down to specific SSH keys.
3. **No Direct Client Canvas Access:** Clients never interact directly with the n8n canvas; all interactions are routed through secure Odoo webhooks and portals to prevent accidental breakages.
