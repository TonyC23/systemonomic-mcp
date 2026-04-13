"""Systemonomic WDA MCP Server — Work Domain Analysis tools and resources."""
import json
from typing import Optional
from mcp.server.fastmcp import FastMCP
from .client import api_get, api_post, api_put, api_delete

mcp = FastMCP(
    "Systemonomic WDA",
    instructions=(
        "Work Domain Analysis (WDA) server for Systemonomic. "
        "Use these tools to manage projects and build WDA models — "
        "hierarchical graphs of Purposes, Values, Functions, Processes, and Objects "
        "connected by means-ends links."
    ),
)


# ── Projects ─────────────────────────────────────────────────────────────────

@mcp.tool()
async def list_projects() -> str:
    """List all projects owned by the authenticated user.

    Returns a JSON array of project objects with id, name, description, and timestamps.
    """
    data = await api_get("/projects")
    return json.dumps(data, indent=2)


@mcp.tool()
async def get_project_state(project_id: str) -> str:
    """Get the complete state of a project: WDA nodes, links, tasks, ATSS results, and org design.

    This is the most efficient way to understand a project's current state in a single call.
    """
    data = await api_get(f"/projects/{project_id}/complete-state")
    return json.dumps(data, indent=2)


@mcp.tool()
async def create_project(name: str, description: str = "") -> str:
    """Create a new project.

    Args:
        name: Project name (e.g. "Procurement Process Analysis")
        description: Optional description of the project scope
    """
    data = await api_post("/projects", json={"name": name, "description": description})
    return json.dumps(data, indent=2)


@mcp.tool()
async def get_project_stats(project_id: str) -> str:
    """Get summary statistics for a project: node counts by level, task count, ATSS completion, etc."""
    data = await api_get(f"/projects/{project_id}/stats")
    return json.dumps(data, indent=2)


# ── WDA Nodes ────────────────────────────────────────────────────────────────

@mcp.tool()
async def list_wda_nodes(project_id: str) -> str:
    """List all WDA nodes in a project.

    Each node has an id, label, level (Purposes/Values/Functions/Processes/Objects),
    and optional description and attributes.
    """
    data = await api_get(f"/wda/projects/{project_id}/nodes")
    return json.dumps(data, indent=2)


@mcp.tool()
async def create_wda_node(
    project_id: str,
    label: str,
    level: str,
    description: str = "",
) -> str:
    """Create a new WDA node at a specific level.

    Args:
        project_id: The project to add the node to
        label: Node label (e.g. "Ensure Regulatory Compliance")
        level: One of: Purposes, Values, Functions, Processes, Objects
        description: Optional description of the node's role
    """
    data = await api_post(
        f"/wda/projects/{project_id}/nodes",
        json={"label": label, "level": level, "description": description},
    )
    return json.dumps(data, indent=2)


@mcp.tool()
async def update_wda_node(
    project_id: str,
    node_id: str,
    label: Optional[str] = None,
    level: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Update an existing WDA node's label, level, or description.

    Only provide the fields you want to change.
    """
    body: dict = {"id": node_id}
    if label is not None:
        body["label"] = label
    if level is not None:
        body["level"] = level
    if description is not None:
        body["description"] = description
    data = await api_put(f"/wda/projects/{project_id}/nodes/{node_id}", json=body)
    return json.dumps(data, indent=2)


@mcp.tool()
async def delete_wda_node(project_id: str, node_id: str) -> str:
    """Delete a WDA node and all its connected links."""
    data = await api_delete(f"/wda/projects/{project_id}/nodes/{node_id}")
    return json.dumps(data, indent=2)


# ── WDA Links ────────────────────────────────────────────────────────────────

@mcp.tool()
async def list_wda_links(project_id: str) -> str:
    """List all means-ends links in a project's WDA."""
    data = await api_get(f"/wda/projects/{project_id}/links")
    return json.dumps(data, indent=2)


@mcp.tool()
async def create_wda_link(project_id: str, from_node_id: str, to_node_id: str) -> str:
    """Create a means-ends link between two WDA nodes.

    Links connect higher-level nodes to lower-level nodes
    (e.g. a Purpose to a Value, or a Function to a Process).

    Args:
        project_id: The project containing the nodes
        from_node_id: The higher-level (parent) node ID
        to_node_id: The lower-level (child) node ID
    """
    data = await api_post(
        f"/wda/projects/{project_id}/links",
        json={"from": from_node_id, "to": to_node_id},
    )
    return json.dumps(data, indent=2)


@mcp.tool()
async def delete_wda_link(project_id: str, from_node_id: str, to_node_id: str) -> str:
    """Delete a means-ends link between two WDA nodes."""
    data = await api_delete(
        f"/wda/projects/{project_id}/links?from={from_node_id}&to={to_node_id}"
    )
    return json.dumps(data, indent=2)


# ── WDA Generation ───────────────────────────────────────────────────────────

@mcp.tool()
async def generate_wda(
    project_id: str,
    description: str,
    provider: str = "gemini",
    detail_level: str = "standard",
) -> str:
    """Generate a complete WDA from a text description using AI.

    Describe the work domain or organization in plain language and an AI model
    will generate the full WDA hierarchy (Purposes → Values → Functions → Processes → Objects).

    Args:
        project_id: Target project to populate with the generated WDA
        description: Natural language description of the work domain
            (e.g. "A hospital emergency department managing patient triage, treatment, and discharge")
        provider: LLM provider — one of: gemini, claude, openai (default: gemini)
        detail_level: Level of detail — basic, standard, or detailed (default: standard)
    """
    data = await api_post(
        "/wda-generation/generate",
        json={
            "projectId": project_id,
            "description": description,
            "provider": provider,
            "detailLevel": detail_level,
        },
    )
    return json.dumps(data, indent=2)


# ── Import / Export ──────────────────────────────────────────────────────────

@mcp.tool()
async def export_project(project_id: str) -> str:
    """Export a complete project (WDA, tasks, ATSS, org design) as JSON.

    The returned JSON can be used to import the project into another account
    or as a backup.
    """
    data = await api_get(f"/projects/{project_id}/export/complete")
    return json.dumps(data, indent=2)


@mcp.tool()
async def import_wda(project_id: str, nodes: list, links: list) -> str:
    """Import WDA nodes and links into an existing project.

    Args:
        project_id: Target project
        nodes: List of node objects, each with label, level, and optional description
        links: List of link objects, each with 'from' and 'to' node references
    """
    data = await api_post(
        f"/wda/projects/{project_id}/import/complete",
        json={"nodes": nodes, "links": links},
    )
    return json.dumps(data, indent=2)


# ── Resources ────────────────────────────────────────────────────────────────

@mcp.resource("wda://projects/{project_id}/nodes")
async def resource_wda_nodes(project_id: str) -> str:
    """Current WDA nodes for a project."""
    data = await api_get(f"/wda/projects/{project_id}/nodes")
    return json.dumps(data, indent=2)


@mcp.resource("wda://projects/{project_id}/links")
async def resource_wda_links(project_id: str) -> str:
    """Current WDA links for a project."""
    data = await api_get(f"/wda/projects/{project_id}/links")
    return json.dumps(data, indent=2)


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    mcp.run()


if __name__ == "__main__":
    main()
