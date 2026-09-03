# Agentic AI Workspace

This repository serves as the central command center for hosting and managing agentic AI workflows on Oracle Cloud Infrastructure (OCI) using n8n.

## Repository Structure

- `workflows/templates/`: Baseline workflow JSON files (e.g., Lead Gen AI Agent, Customer Support Agent).
- `workflows/clients/`: Client-specific workflow modifications.
- `infrastructure/docker/`: Docker Compose configurations and deployment scripts for the OCI instance.
- `agents/prompts/`: System prompts used by AI agents.
- `agents/scripts/`: Custom Python/Node.js scripts executed by agents or n8n nodes.

## Security Best Practices

1. **Never commit secrets**: Do not push `.env`, `.pem`, `.key`, or any files containing API keys, database passwords, or n8n credentials to this repository. Use the `.gitignore` to prevent this.
2. **Key-Based SSH**: Access to the OCI instance should strictly be via SSH key (`.pem` or `.ppk` files kept locally on your machine).
3. **Environment Variables**: Configure all secrets directly on the OCI server using `.env` files located securely on the server.

## Managing Workflows

Workflows are managed via n8n at `n8n.kebundata.my`. Changes to workflows should be exported as JSON and saved in the respective `workflows/` directory to track version history.
