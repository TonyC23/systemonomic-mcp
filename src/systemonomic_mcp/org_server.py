"""Systemonomic Org Design MCP Server — SOCA organizational design and PDF reports."""
import json
import base64
from mcp.server.fastmcp import FastMCP
from .client import api_get, api_post, api_post_blob

mcp = FastMCP(
    "Systemonomic Org Design",
    instructions=(
        "Organizational design (SOCA) server for Systemonomic. "
        "Use these tools to manage roles, org units, and task allocations; "
        "generate AI-powered restructure proposals from ATSS results; "
        "and create PDF reports."
    ),
)


# ── Org Design ───────────────────────────────────────────────────────────────

@mcp.tool()
async def get_org_design(project_id: str) -> str:
    """Get the current organizational design for a project.

    Returns roles, org units, allocations, RACI matrix, and team structure.
    """
    data = await api_get(f"/restructure/projects/{project_id}/design")
    return json.dumps(data, indent=2)


@mcp.tool()
async def persist_org_design(project_id: str, design: dict) -> str:
    """Save an organizational design to a project.

    Args:
        project_id: Target project
        design: Full org design object with roles, orgUnits, and allocations
    """
    data = await api_post(f"/restructure/projects/{project_id}/persist", json=design)
    return json.dumps(data, indent=2)


@mcp.tool()
async def propose_restructure(
    project_id: str,
    provider: str = "gemini",
) -> str:
    """Generate an AI-powered restructure proposal from ATSS results.

    Analyzes automation suitability scores and proposes optimal role definitions,
    org units, and task allocations. Requires ATSS results to be available.

    Args:
        project_id: The project to analyze
        provider: LLM provider — gemini, claude, or openai (default: gemini)
    """
    atss = await api_get(f"/assess/projects/{project_id}/results")
    if not atss:
        return json.dumps({"error": "No ATSS results found. Run ATSS assessment first."})

    data = await api_post(
        f"/restructure/projects/{project_id}/propose",
        json={"atssResults": atss, "provider": provider},
    )
    return json.dumps(data, indent=2)


@mcp.tool()
async def apply_proposal(project_id: str, proposal: dict) -> str:
    """Apply an AI-generated restructure proposal to the project.

    This replaces the current org design with the proposed one.

    Args:
        project_id: Target project
        proposal: The proposal object returned by propose_restructure
    """
    data = await api_post(
        f"/restructure/projects/{project_id}/propose/apply",
        json=proposal,
    )
    return json.dumps(data, indent=2)


@mcp.tool()
async def validate_raci(project_id: str) -> str:
    """Validate the RACI matrix for a project.

    Checks for gaps (tasks with no responsible role), overloads,
    and other RACI inconsistencies.
    """
    data = await api_get(f"/restructure/projects/{project_id}/raci/validate")
    return json.dumps(data, indent=2)


# ── Snapshots ────────────────────────────────────────────────────────────────

@mcp.tool()
async def create_org_snapshot(project_id: str, label: str = "") -> str:
    """Create a snapshot of the current org design for version control.

    Args:
        project_id: The project to snapshot
        label: Optional label for the snapshot
    """
    data = await api_post(
        f"/restructure/projects/{project_id}/snapshots/org",
        json={"label": label} if label else {},
    )
    return json.dumps(data, indent=2)


@mcp.tool()
async def list_org_snapshots(project_id: str) -> str:
    """List all org design snapshots for a project."""
    data = await api_get(f"/restructure/projects/{project_id}/snapshots/org")
    return json.dumps(data, indent=2)


# ── Export ───────────────────────────────────────────────────────────────────

@mcp.tool()
async def export_org_design_json(project_id: str) -> str:
    """Export the org design as a JSON document."""
    data = await api_get(f"/restructure/projects/{project_id}/export/design.json")
    return json.dumps(data, indent=2)


# ── PDF Report ───────────────────────────────────────────────────────────────

@mcp.tool()
async def generate_pdf_report(
    project_id: str,
    include_confidential: bool = True,
) -> str:
    """Generate a comprehensive PDF report for a project.

    The report includes the WDA overview, ATSS analysis with automation
    recommendations, organizational design, and next steps.

    Returns the PDF as a base64-encoded string. Save it to a file with:
        import base64; open("report.pdf", "wb").write(base64.b64decode(result))

    Args:
        project_id: The project to report on
        include_confidential: Whether to include the CONFIDENTIAL watermark (default: True)
    """
    pdf_bytes = await api_post_blob(
        f"/reports/{project_id}/pdf",
        json={"include_confidential": include_confidential},
    )
    encoded = base64.b64encode(pdf_bytes).decode("ascii")
    return json.dumps({
        "format": "pdf",
        "encoding": "base64",
        "size_bytes": len(pdf_bytes),
        "data": encoded,
    })


@mcp.tool()
async def get_report_status(project_id: str) -> str:
    """Check the readiness status of a project's report.

    Returns which sections have enough data to generate a meaningful report.
    """
    data = await api_get(f"/reports/{project_id}/report-status")
    return json.dumps(data, indent=2)


# ── Resources ────────────────────────────────────────────────────────────────

@mcp.resource("org://projects/{project_id}/design")
async def resource_org_design(project_id: str) -> str:
    """Current org design for a project."""
    data = await api_get(f"/restructure/projects/{project_id}/design")
    return json.dumps(data, indent=2)


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    mcp.run()


if __name__ == "__main__":
    main()
