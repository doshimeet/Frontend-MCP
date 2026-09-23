# Enterprise Design System MCP Server

Model Context Protocol (MCP) server providing autonomous design system intelligence, business requirements parsing, component discovery, and application scaffolding.

## Transports Supported

1. **Local Mode (`stdio`)**: Default mode for local IDE integration (Antigravity, VS Code GitHub Copilot, Claude Desktop). Zero port conflicts, sub-millisecond IPC communication.
   ```bash
   python server.py
   ```
2. **Cloud Mode (`uvicorn` SSE)**: Containerized web service for Azure App Service or AWS hosting. Exposes Server-Sent Events (SSE) on port 8000.
   ```bash
   MCP_MODE=uvicorn python server.py
   ```

## Tools Provided

* `check_environment_health`: Pre-flight diagnostics for Python, Node, npm, system Edge browser, and network connectivity.
* `plan_application_from_requirements`: Converts PRD/BRD text into structured routes, entities, and component maps.
* `get_design_tokens`: Serves DTCG-compliant tokens for corporate B2B and custom client themes.
* `get_components`: Returns available component definitions, props, and canonical stories (IBM Carbon / Enterprise).
* `get_page_recipe`: Returns full-page boilerplate layouts (`CrudTable`, `MetricsDashboard`, `FormWizard`).
* `scaffold_greenfield_app`: Scaffolds a new Next.js application from the Azure DevOps starter kit.
* `integrate_into_existing_app`: Auto-detects Next.js App vs. Pages router and adds pages with safe conflict detection.
