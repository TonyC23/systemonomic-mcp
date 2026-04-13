"""Systemonomic ATSS MCP Server — Task derivation and automation suitability scoring."""
import json
from typing import Optional
from mcp.server.fastmcp import FastMCP
from .client import api_get, api_post, api_delete

mcp = FastMCP(
    "Systemonomic ATSS",
    instructions=(
        "Automated Task Suitability Scoring (ATSS) server for Systemonomic. "
        "Use these tools to derive tasks from a WDA, run AI-powered automation "
        "suitability assessments, and manage task suggestions. "
        "Typical workflow: derive tasks from WDA objects → run ATSS batch → "
        "review results and recommendations."
    ),
)


# ── Tasks ────────────────────────────────────────────────────────────────────

@mcp.tool()
async def list_tasks(project_id: str) -> str:
    """List all tasks in a project.

    Each task has an id, name, description, mode (manual/semi-auto/auto),
    and links to WDA nodes.
    """
    data = await api_get(f"/tasks/projects/{project_id}")
    return json.dumps(data, indent=2)


@mcp.tool()
async def create_task(
    project_id: str,
    name: str,
    description: str = "",
    mode: str = "manual",
) -> str:
    """Create a new task in a project.

    Args:
        project_id: The project to add the task to
        name: Task name
        description: Optional task description
        mode: One of: manual, semi-auto, auto (default: manual)
    """
    data = await api_post(
        f"/tasks/projects/{project_id}",
        json={"name": name, "description": description, "mode": mode},
    )
    return json.dumps(data, indent=2)


@mcp.tool()
async def generate_tasks_from_wda(project_id: str) -> str:
    """Auto-generate tasks from the WDA Objects level.

    Analyzes the Objects (lowest level) of the WDA and creates corresponding
    control tasks. This is the standard first step before running ATSS.
    """
    data = await api_post(f"/tasks/projects/{project_id}/generate-from-wda")
    return json.dumps(data, indent=2)


@mcp.tool()
async def derive_task_suggestions(
    project_id: str,
    provider: str = "gemini",
) -> str:
    """Use AI to derive detailed task suggestions from WDA objects.

    More sophisticated than generate_tasks_from_wda — uses an LLM to analyze
    each WDA object and suggest tasks with descriptions.

    Args:
        project_id: The project to analyze
        provider: LLM provider — gemini, claude, or openai (default: gemini)
    """
    data = await api_post(
        f"/tasks/projects/{project_id}/suggestions/derive-batch",
        json={"provider": provider},
    )
    return json.dumps(data, indent=2)


@mcp.tool()
async def list_suggestions(project_id: str) -> str:
    """List all pending task suggestions for a project.

    Suggestions are AI-generated task proposals that haven't been accepted yet.
    """
    data = await api_get(f"/tasks/projects/{project_id}/suggestions")
    return json.dumps(data, indent=2)


@mcp.tool()
async def accept_suggestions(project_id: str, suggestion_ids: list) -> str:
    """Accept task suggestions, promoting them to actual project tasks.

    Args:
        project_id: The project containing the suggestions
        suggestion_ids: List of suggestion IDs to accept
    """
    data = await api_post(
        f"/tasks/projects/{project_id}/suggestions/accept",
        json={"suggestionIds": suggestion_ids},
    )
    return json.dumps(data, indent=2)


# ── ATSS Assessment ──────────────────────────────────────────────────────────

@mcp.tool()
async def run_atss_batch(
    project_id: str,
    provider: str = "gemini",
    model: Optional[str] = None,
) -> str:
    """Run ATSS (Automated Task Suitability Scoring) on all tasks in a project.

    Each task is assessed across multiple gates (data availability, rule-base,
    exception handling, etc.) and scored 0-100 for automation suitability.

    Args:
        project_id: The project whose tasks to assess
        provider: LLM provider — gemini, claude, or openai (default: gemini)
        model: Specific model name (optional, uses provider default)

    Returns scored results for each task with classification
    (Automate / Augment / Manual) and reasoning.
    """
    tasks = await api_get(f"/tasks/projects/{project_id}")
    if not tasks:
        return json.dumps({"error": "No tasks found. Generate tasks from WDA first."})

    body = {
        "tasks": tasks,
        "project_id": project_id,
        "provider": provider,
    }
    if model:
        body["model"] = model

    data = await api_post("/llm/atss-assessment-batch", json=body)
    return json.dumps(data, indent=2)


@mcp.tool()
async def get_atss_results(project_id: str) -> str:
    """Get stored ATSS results for a project.

    Returns previously persisted assessment results, including scores,
    classifications, and reasoning for each task.
    """
    data = await api_get(f"/assess/projects/{project_id}/results")
    return json.dumps(data, indent=2)


@mcp.tool()
async def persist_atss_results(project_id: str, rows: list) -> str:
    """Persist ATSS assessment results to the project.

    Args:
        project_id: The project to save results to
        rows: List of ATSS result objects (from run_atss_batch output)
    """
    data = await api_post(f"/assess/projects/{project_id}/persist", json=rows)
    return json.dumps(data, indent=2)


@mcp.tool()
async def list_atss_runs(project_id: str) -> str:
    """List all ATSS assessment runs for a project, with timestamps and summaries."""
    data = await api_get(f"/assess/projects/{project_id}/runs")
    return json.dumps(data, indent=2)


# ── Resources ────────────────────────────────────────────────────────────────

@mcp.resource("atss://projects/{project_id}/tasks")
async def resource_tasks(project_id: str) -> str:
    """Current tasks for a project."""
    data = await api_get(f"/tasks/projects/{project_id}")
    return json.dumps(data, indent=2)


@mcp.resource("atss://projects/{project_id}/results")
async def resource_atss_results(project_id: str) -> str:
    """Stored ATSS results for a project."""
    data = await api_get(f"/assess/projects/{project_id}/results")
    return json.dumps(data, indent=2)


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    mcp.run()


if __name__ == "__main__":
    main()
