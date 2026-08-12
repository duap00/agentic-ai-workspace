# 🤖 Agentic AI Workspace

This repository serves as the central control plane, configuration hub, and skill library for the AI Agents running on my OCI infrastructure, integrated with **Google Gemini Pro** and **n8n**.

It connects autonomous agent intelligence with Odoo ERP, Takaful insurance tools, and automated business workflows.

---

## 🏛️ The 5 Pillars of My Agentic Stack

This architecture is built on the 5 pillars of persistent, autonomous AI:

1. **Soul (`/agents/hermes/SOUL.md`)**: The identity, rules, and behavioral constraints of the agent (e.g. friendly sales rep, strategic planner).
2. **Memory (`/agents/hermes/memories/`)**: Contextual logs and customer details stored in Odoo and database files to maintain continuity.
3. **Skills (`/skills/`)**: Custom Python and API connector scripts that allow Gemini to:
   - **Odoo ERP**: Read and write business records.
   - **WhatsApp/Messaging**: Interface with customers to reply to leads.
   - **Web Tools**: Search and extract agricultural data for KebunData.
4. **Crons (`/workflows/cron-jobs/`)**: Automation tasks run on schedule via **n8n** (e.g., weekly CEO analysis, daily content generation).
5. **Self-Improvement**: Performance logging to refine sales scripts and copywriting.

---

## 🚀 Infrastructure Architecture

Our setup offloads heavy LLM computing to the cloud while keeping orchestration and database systems private:

```mermaid
graph TD
    User([Customer on WhatsApp]) -->|Webhook| Responder[1. Lead Responder Agent]
    Cron[Weekly Timer] -->|Trigger| Marketing[2. Marketing Agent]
    
    subgraph n8n [n8n on OCI Server]
        Responder
        Marketing
    end
    
    subgraph OCI [Your OCI Server]
        n8n -->|Save/Fetch Leads| Odoo[(Odoo CRM)]
    end
    
    subgraph Cloud [Google Cloud]
        n8n -->|API Requests| Gemini[Google Gemini Pro API]
    end
```

---

## 📂 Repository Layout

```text
agentic-ai-workspace/
├── README.md                 # Project dashboard and setup guide
├── docker-compose.yml        # Setup for Odoo, Postgres, and Nginx on OCI
│
├── agents/                   # Agent configurations and system instructions
│   └── hermes/
│       ├── SOUL.md           # The agent's identity, rules, and behavior
│       └── .env.example      # Environment variables template (API keys)
│
├── skills/                   # Custom scripts the agent can execute
│   ├── odoo-connector/       # Python scripts to query/insert leads into Odoo
│   └── server-health/        # Scripts to monitor OCI docker container health
│
└── workflows/                # n8n Automation JSON blueprints
    ├── lead-responder.json   # Real-time WhatsApp sales agent workflow
    └── B2B-prospector.json   # Automated cold outreach workflow
```
