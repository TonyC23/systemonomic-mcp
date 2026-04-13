# Systemonomic MCP Servers

<!-- mcp-name: io.github.TonyC23/systemonomic-mcp -->

MCP (Model Context Protocol) servers that expose Systemonomic's Work Domain Analysis, ATSS assessment, and organizational design capabilities to AI agents (Claude Desktop, Cursor, Claude Code, etc.).

## Quick Start

### 1. Install

```bash
pip install systemonomic-mcp
```

### 2. Get an API Key

1. Log in to [Systemonomic](https://systemonomic.com)
2. Go to **Profile** → **API Keys**
3. Click **Generate API Key**
4. Copy the key (starts with `sk_sys_`) — it's shown only once

### 3. Configure

Set the environment variable:

```bash
export SYSTEMONOMIC_API_KEY="sk_sys_your_key_here"
```

Optionally, point to a different API endpoint (defaults to production):

```bash
export SYSTEMONOMIC_API_URL="https://your-dev-backend.up.railway.app"
```

### 4. Add to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "systemonomic-wda": {
      "command": "python",
      "args": ["-m", "systemonomic_mcp.wda_server"],
      "env": {
        "SYSTEMONOMIC_API_KEY": "sk_sys_your_key_here"
      }
    },
    "systemonomic-atss": {
      "command": "python",
      "args": ["-m", "systemonomic_mcp.atss_server"],
      "env": {
        "SYSTEMONOMIC_API_KEY": "sk_sys_your_key_here"
      }
    },
    "systemonomic-org": {
      "command": "python",
      "args": ["-m", "systemonomic_mcp.org_server"],
      "env": {
        "SYSTEMONOMIC_API_KEY": "sk_sys_your_key_here"
      }
    }
  }
}
```

### 5. Add to Cursor

In Cursor Settings → MCP Servers, add each server:

- **Name:** `systemonomic-wda`
- **Command:** `python -m systemonomic_mcp.wda_server`
- **Environment:** `SYSTEMONOMIC_API_KEY=sk_sys_...`

Repeat for `atss_server` and `org_server`.

## Available Servers

### `systemonomic-wda` — Work Domain Analysis

| Tool | Description |
|------|-------------|
| `list_projects` | List all projects |
| `get_project_state` | Get complete project state |
| `create_project` | Create a new project |
| `get_project_stats` | Get project statistics |
| `list_wda_nodes` | List WDA nodes |
| `create_wda_node` | Create a node at a WDA level |
| `update_wda_node` | Update a node's label/level/description |
| `delete_wda_node` | Delete a node |
| `list_wda_links` | List means-ends links |
| `create_wda_link` | Link two nodes |
| `delete_wda_link` | Remove a link |
| `generate_wda` | AI-generate a full WDA from a text description |
| `export_project` | Export project as JSON |
| `import_wda` | Import nodes and links |

### `systemonomic-atss` — Assessment & Tasks

| Tool | Description |
|------|-------------|
| `list_tasks` | List project tasks |
| `create_task` | Create a task |
| `generate_tasks_from_wda` | Auto-generate tasks from WDA Objects |
| `derive_task_suggestions` | AI-derived task suggestions |
| `list_suggestions` | List pending suggestions |
| `accept_suggestions` | Promote suggestions to tasks |
| `run_atss_batch` | Run ATSS assessment on all tasks |
| `get_atss_results` | Get stored assessment results |
| `persist_atss_results` | Save assessment results |
| `list_atss_runs` | List assessment run history |

### `systemonomic-org` — Organizational Design

| Tool | Description |
|------|-------------|
| `get_org_design` | Get current roles, org units, allocations |
| `persist_org_design` | Save org design |
| `propose_restructure` | AI-generated restructure proposal |
| `apply_proposal` | Apply a restructure proposal |
| `validate_raci` | Validate RACI matrix |
| `create_org_snapshot` | Create version snapshot |
| `list_org_snapshots` | List snapshots |
| `export_org_design_json` | Export as JSON |
| `generate_pdf_report` | Generate comprehensive PDF report |
| `get_report_status` | Check report readiness |

## Example Conversations

### "Help me model our procurement process"

> **You:** Generate a WDA for our university procurement department. They handle purchase requests, vendor management, contract negotiation, and compliance with government regulations.
>
> **Claude:** *Uses `create_project` → `generate_wda` → returns the generated hierarchy*

### "Assess which tasks can be automated"

> **You:** For the procurement project, derive tasks from the WDA and run an automation assessment.
>
> **Claude:** *Uses `generate_tasks_from_wda` → `run_atss_batch` → summarizes automation candidates*

### "Generate the full report"

> **You:** Create a PDF report for the procurement project.
>
> **Claude:** *Uses `generate_pdf_report` → saves the PDF*

## Development

```bash
# Run a server locally for testing
cd mcp
pip install -e .
SYSTEMONOMIC_API_KEY=sk_sys_... python -m systemonomic_mcp.wda_server

# Use the MCP inspector
SYSTEMONOMIC_API_KEY=sk_sys_... mcp dev src/systemonomic_mcp/wda_server.py
```
