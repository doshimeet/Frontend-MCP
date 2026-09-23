# Master Production Deployment Runbook: Azure App Service FastMCP Engine

A complete, zero-omission guide detailing how to containerize, deploy, configure, and connect the **AI-Native Enterprise Design System FastMCP Server** in **Azure App Service (Linux Web App for Containers)**, connect it to your internal World Bank Group digital assets, and integrate it into developer IDEs (VS Code, Antigravity, GitHub Copilot).

---

## 1. Complete Architecture & Traffic Flow

```text
========================================================================================================================
                                      ENTERPRISE CLOUD ARCHITECTURE & TRAFFIC FLOW
========================================================================================================================

  DEVELOPER WORKSTATION
  ┌────────────────────────────────────────────────────────┐
  │ VS Code / Antigravity / GitHub Copilot                 │
  │ • .vscode/settings.json or global config               │
  │ • Target: https://wbg-mcp.azurewebsites.net/sse        │
  │ • Header: Authorization: Bearer <MCP_API_KEY>          │
  └───────────────────────────┬────────────────────────────┘
                              │
                              │ 1. HTTPS / SSE (Port 443)
                              ▼
  AZURE CLOUD INFRASTRUCTURE
  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Azure App Service / Application Gateway (wbg-mcp.azurewebsites.net)                                                │
  │                                                                                                                    │
  │   [Port Mapping & Ingress]                                                                                         │
  │   External HTTPS (Port 443) ──► WEBSITES_PORT=8000 ──► Uvicorn ASGI Server (Port 8000)                             │
  │                                                                                                                    │
  │   [FastMCP Python Linux Container]                                                                                 │
  │   ├── CloudAuthMiddleware: Validates Bearer Token / x-api-key header on /sse and message routes                    │
  │   ├── GET /health: Unauthenticated ALB / App Service liveness probe (Returns HTTP 200)                             │
  │   │                                                                                                                │
  │   ├── [Connectors Layer]                                                                                           │
  │   │   ├── ado_connector.py      ──► Azure DevOps REST API (MSAL DefaultAzureCredential)                           │
  │   │   ├── storybook_connector.py ──► Live WBG Storybook (https://design.wbg.org/storybook/index.json)               │
  │   │   └── npm_connector.py       ──► ~/.npmrc / Azure Artifacts feed validator                                    │
  │   │                                                                                                                │
  │   └── [Embedded Baseline Assets]                                                                                   │
  │       ├── packages/tokens/       ──► DTCG Standard Tokens (wbg-enterprise.json, enterprise-dark.json)               │
  │       ├── packages/recipes/      ──► Canonical Recipes (CrudTableRecipe.tsx, MetricsDashboardRecipe.tsx)            │
  │       └── templates/frontend-starter/ ──► Next.js 14 Starter Kit (Offline fallback bundle)                          │
  └───────────────────────────┬────────────────────────────────────────────────────────┬───────────────────────────────┘
                              │                                                        │
                              │ 2. Managed Identity (DefaultAzureCredential)           │ 3. HTTPS Component Sync
                              ▼                                                        ▼
  ┌────────────────────────────────────────────────────────┐ ┌─────────────────────────────────────────────────────────┐
  │ Azure DevOps Git Repository                            │ │ Internal World Bank Group Storybook                     │
  │ https://dev.azure.com/{org}/{project}/_git/starter-kit │ │ https://designsystem.worldbankgroup.org/storybook/      │
  │ (Live template updates pulled on demand)               │ │ (Harvests index.json & caches components)               │
  └────────────────────────────────────────────────────────┘ └─────────────────────────────────────────────────────────┘
========================================================================================================================
```

---

## 2. Exact Files & Folders Required for the App Service Codebase

When deploying the FastMCP server to Azure App Service (either from this monorepo or from a dedicated MCP server repository), the following files and folders **must be present in the container image**:

### Complete Directory Tree Required in the Container (`/app`):

```text
/app/
├── pyproject.toml                         <-- Python package metadata and pip dependencies
├── Dockerfile                             <-- Container definition for Azure App Service
├── server.py                              <-- Main FastMCP entrypoint (SSE + /health probe)
├── config.py                              <-- Environment variables & path resolver
│
├── models/                                <-- Strict Pydantic domain models
│   ├── __init__.py
│   ├── a11y.py                            <-- A11yAuditReport, A11yViolation, A11yNode
│   ├── component.py                       <-- ComponentSpec, PropDefinition, ComponentCatalogSummary
│   ├── health.py                          <-- HealthReport, RuntimeDiagnostic
│   ├── requirements.py                    <-- RequirementBlueprint, PlannedRoute
│   ├── scaffolding.py                     <-- ScaffoldResult, ConflictReport, IntegrationPlan
│   ├── security.py                        <-- PathValidationResult
│   └── tokens.py                          <-- TokenItem, ThemeTokens, TokenCategoryResponse
│
├── connectors/                            <-- External client integrations
│   ├── __init__.py
│   ├── ado_connector.py                   <-- Azure DevOps Git REST API client (MSAL auth)
│   ├── npm_connector.py                   <-- .npmrc Azure Artifacts feed reader
│   └── storybook_connector.py             <-- Dynamic Storybook harvester & cache engine
│
├── services/                              <-- Pure business logic (Decoupled from transport)
│   ├── __init__.py
│   ├── a11y_service.py                    <-- Headless Playwright / axe-core audit invoker
│   ├── brownfield_service.py              <-- Router detector & conflict analyzer
│   ├── health_service.py                  <-- Workstation diagnostic runner
│   ├── requirements_service.py            <-- Dynamic domain routing & prompt planner
│   ├── scaffolding_service.py             <-- Greenfield unpacker & package configurer
│   ├── security_service.py                <-- Path traversal prevention & sandboxing
│   └── token_service.py                   <-- DTCG token loader & theme cascader
│
├── tools/                                 <-- Thin FastMCP protocol wrappers (@mcp.tool)
│   ├── __init__.py
│   ├── brownfield_tools.py                <-- extend_existing_app (alias: integrate_into_existing_app)
│   ├── catalog_tools.py                   <-- get_components, get_component_props
│   ├── diagnostics_tools.py               <-- check_system_health, audit_accessibility
│   ├── recipes_tools.py                   <-- list_page_recipes, get_page_recipe
│   ├── requirements_tools.py              <-- plan_application_architecture
│   ├── scaffolding_tools.py               <-- create_enterprise_app (alias: scaffold_greenfield_app)
│   └── tokens_tools.py                    <-- get_design_tokens
│
├── resources/                             <-- Passive context streams (@mcp.resource)
│   ├── __init__.py
│   ├── recipes_resource.py                <-- recipe://{recipe_name}
│   └── tokens_resource.py                 <-- design://tokens/{theme}
│
├── prompts/                               <-- Guided agent prompts (@mcp.prompt)
│   ├── __init__.py
│   ├── critique_ui_prompt.py              <-- /impeccable_design_critique
│   └── plan_prd_prompt.py                 <-- /plan_prd_feature
│
├── core/                                  <-- Low-level helpers
│   ├── __init__.py
│   ├── ado_client.py                      <-- Azure DevOps low-level HTTP client
│   ├── auth.py                            <-- DefaultAzureCredential MSAL wrapper
│   ├── health.py                          <-- System diagnostics probe
│   └── router_detector.py                 <-- Next.js App vs Pages router detector
│
├── packages/                              <-- Design System Assets
│   ├── tokens/
│   │   ├── tokens.json                    <-- Master DTCG tokens specification
│   │   └── themes/
│   │       ├── wbg-enterprise.json        <-- Official World Bank Group DTCG token theme
│   │       ├── enterprise-dark.json       <-- IBM Carbon dark enterprise palette
│   │       └── client-warm-sage.json      <-- Client-facing warm sage palette
│   └── recipes/
│       ├── recipes.json                   <-- Recipe catalog metadata
│       ├── CrudTableRecipe.tsx            <-- Data Table + TanStack Query + FilterBar
│       ├── MetricsDashboardRecipe.tsx     <-- KPI Cards + Trend Delta + Activity Log
│       └── FormWizardRecipe.tsx           <-- Multi-Step Form Wizard + Sticky Actions
│
├── templates/
│   └── frontend-starter/                  <-- Bundled Starter Kit (Resilient Local Fallback)
│       ├── package.json                   <-- Next.js + @carbon/react + TanStack Query + Playwright
│       ├── tsconfig.json
│       ├── next.config.mjs
│       ├── playwright.config.ts
│       ├── .npmrc
│       ├── messages/                      <-- i18n dictionaries (en.json, fr.json, es.json)
│       ├── e2e/
│       │   └── a11y.spec.ts               <-- Pre-wired WCAG 2.1 AA Playwright spec
│       ├── scripts/
│       │   └── generate-scorecard.mjs     <-- test-summary.md generator
│       └── src/
│           ├── app/ (layout.tsx, page.tsx, globals.scss)
│           ├── providers/ (QueryProvider.tsx)
│           ├── hooks/ (useTranslation.ts)
│           └── components/ (AppShell.tsx, auth/AuthProvider.tsx)
│
└── scripts/
    └── verify-a11y.mjs                    <-- Headless browser axe-core execution engine
```

---

## 3. Containerization & Startup Command

### 3.1: The Production Dockerfile
Place this Dockerfile at the root of the App Service codebase (or use [`packages/mcp-server/Dockerfile`](file:///Users/meetketankumardoshi/Design%20System/packages/mcp-server/Dockerfile)):

```dockerfile
# ==============================================================================
# ENTERPRISE DESIGN SYSTEM MCP SERVER - AZURE APP SERVICE DOCKERFILE
# Linux Container for Azure App Service / Azure Container Apps deployment
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cloud Mode Defaults
ENV MCP_MODE=uvicorn
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV WEBSITES_PORT=8000
ENV REPO_ROOT=/app

WORKDIR /app

# Install system dependencies & Node.js for Playwright / axe-core audits
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy packaging configuration and install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Install minimal Node runtime dependencies for accessibility auditing
RUN npm install -g playwright-core axe-core

# Copy application source code, assets, and starter kit templates
COPY . .

# Expose internal listening port for Azure App Service
EXPOSE 8000

# Azure Health Check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch the FastMCP server in cloud SSE mode via Uvicorn
CMD ["python", "server.py"]
```

### 3.2: The Startup Command
The startup command configured in Azure App Service is:
```bash
python server.py
```
When `MCP_MODE=uvicorn` is set, `server.py` executes:
```python
uvicorn.run(mcp.sse_app, host="0.0.0.0", port=8000, log_level="info")
```
* **SSE Endpoint**: `https://<app-name>.azurewebsites.net/sse`
* **Message POST Endpoint**: `https://<app-name>.azurewebsites.net/messages/`
* **Liveness Probe**: `https://<app-name>.azurewebsites.net/health` (HTTP 200 without authentication)

---

## 4. Azure App Service Configuration & Environment Variables

Configure these settings in the Azure Portal under **App Service $\rightarrow$ Configuration $\rightarrow$ Application settings**:

| Setting Name | Production Value | Purpose & Why It Is Needed |
|---|---|---|
| `WEBSITES_PORT` | `8000` | **Mandatory for Azure App Service.** Informs Azure's frontend proxy to forward incoming port 443 HTTPS traffic to port 8000 inside the container. |
| `MCP_MODE` | `uvicorn` | Instructs `server.py` to start the Uvicorn ASGI Server for Server-Sent Events (SSE) instead of `stdio`. |
| `MCP_HOST` | `0.0.0.0` | Binds server to all interfaces inside container. |
| `MCP_PORT` | `8000` | Internal listening port. |
| `MCP_API_KEY` | *(Generate a 64-character secret)* | **Security Token.** Required for cloud authorization. `CloudAuthMiddleware` checks this on all `/sse` connections. |
| `REPO_ROOT` | `/app` | Sets root workspace path for locating tokens, recipes, and templates. |
| `AZURE_DEVOPS_ORG` | `https://dev.azure.com/<YourWBGOrg>` | Organization URL for Azure DevOps REST API sync. |
| `AZURE_DEVOPS_PROJECT` | `<YourProjectName>` | Azure DevOps project containing the starter kit. |
| `AZURE_DEVOPS_STARTER_REPO_ID` | `frontend-starter-kit` | Repository ID or Git repo name for starter kit. |
| `STORYBOOK_URL` | `https://designsystem.worldbankgroup.org/storybook` | URL of the live WBG Storybook to dynamically harvest component specs. |
| `DESIGN_SYSTEM_PACKAGE` | `@wbg/design-system` | The scoped npm package name injected into scaffolded applications. |

---

## 5. Connecting with the Internal Design System Package

When switching from the working `@carbon/react` proof-of-concept to the official World Bank Group design system package:

### File 1: `templates/frontend-starter/package.json`
Update dependencies to reference the private package:
```json
{
  "name": "enterprise-frontend-starter",
  "dependencies": {
    "@wbg/design-system": "^2.0.0",
    "@tanstack/react-query": "^5.56.2",
    "next": "^14.2.13",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "sass": "^1.79.4"
  }
}
```

### File 2: `templates/frontend-starter/.npmrc`
Point the scoped namespace `@wbg` to your internal Azure Artifacts npm registry:
```ini
# Scoped registry for World Bank Group packages
@wbg:registry=https://pkgs.dev.azure.com/<YourWBGOrg>/<YourProject>/_packaging/<FeedName>/npm/registry/
always-auth=true
```

### File 3: `templates/frontend-starter/src/components/AppShell.tsx`
Replace generic navigation elements with official institutional headers:
```tsx
import { WBGHeader, WBGFooter } from "@wbg/design-system";

// Inside AppShell component:
<WBGHeader
  title="Digital Platform"
  classification="OFFICIAL USE ONLY"
  user={user}
/>
{children}
<WBGFooter copyright="© 2026 World Bank Group" />
```

### File 4: `packages/mcp-server/connectors/storybook_connector.py`
Zero code edits required! The connector automatically reads the `DESIGN_SYSTEM_PACKAGE` environment variable and imports components accordingly:
```python
package_name = os.getenv("DESIGN_SYSTEM_PACKAGE", "@carbon/react")
result[comp_name] = {
    "import_statement": f"import {{ {comp_name} }} from '{package_name}';",
}
```

---

## 6. Connecting with the Internal Starter Kit (Azure DevOps)

### 6.1: Push Starter Kit to Azure DevOps Git
Create a repository named `frontend-starter-kit` in your Azure DevOps project and push the contents of `templates/frontend-starter/`.

### 6.2: Configure Passwordless Azure Managed Identity
1. In Azure Portal, navigate to the App Service $\rightarrow$ **Identity** $\rightarrow$ Turn **System assigned status** to **On**.
2. Copy the **Object ID** (Principal ID).
3. In Azure DevOps $\rightarrow$ **Project Settings** $\rightarrow$ **Repositories** $\rightarrow$ Select `frontend-starter-kit` $\rightarrow$ **Security**.
4. Add the App Service Managed Identity and grant **Read** permission.

### 6.3: How the Sync Works in Code (`ado_connector.py`)
Our connector in `packages/mcp-server/connectors/ado_connector.py` executes:
1. Obtains a cloud token via `DefaultAzureCredential()` (`core/auth.py`).
2. Queries `https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/items?recursionLevel=full&includeContent=true`.
3. If cloud is reachable, unpacks the latest commit directly into the developer's target directory.
4. **Resilient Fallback**: If Azure DevOps is offline or VPN drops, it immediately unpacks `/app/templates/frontend-starter/` locally with **zero developer failure**.

---

## 7. Connecting with Live Internal Storybook

1. Set the App Setting:
   ```env
   STORYBOOK_URL=https://designsystem.worldbankgroup.org/storybook
   ```
2. When the MCP server initializes or when `get_components` is called, [`StorybookConnector`](file:///Users/meetketankumardoshi/Design%20System/packages/mcp-server/connectors/storybook_connector.py):
   * Queries `${STORYBOOK_URL}/index.json` (or `stories.json`).
   * Extracts component names, stories, arguments, and descriptions.
   * Caches the output in `.cache/storybook_catalog.json`.
   * If Storybook is unreachable, loads the cached JSON or embedded catalog.

---

## 8. Configuring VS Code & AI Coding Agents to Connect via SSE

Once the App Service is deployed, developers configure their tools to use the cloud endpoint.

### Configuration Option A: Workspace Settings (`.vscode/settings.json`)
Commit this into your team’s frontend repository so every developer is automatically connected:

```json
{
  "mcp": {
    "servers": {
      "enterprise-design-system": {
        "type": "sse",
        "url": "https://wbg-design-system-mcp.azurewebsites.net/sse",
        "headers": {
          "Authorization": "Bearer <YOUR_PRODUCTION_MCP_API_KEY>"
        }
      }
    }
  }
}
```

### Configuration Option B: Global Configuration (`~/.gemini/config/mcp_config.json`)
For developers using the Antigravity IDE or Claude Desktop globally:

```json
{
  "mcpServers": {
    "enterprise-design-system": {
      "type": "sse",
      "url": "https://wbg-design-system-mcp.azurewebsites.net/sse",
      "headers": {
        "Authorization": "Bearer <YOUR_PRODUCTION_MCP_API_KEY>"
      }
    }
  }
}
```

### Verification in Chat:
In VS Code Copilot or Antigravity Chat:
```text
@enterprise-design-system check_system_health
```
The remote server immediately executes workstation diagnostics and returns the health report.

---

## 9. Azure Network & Security Hardening

For World Bank Group institutional compliance:

1. **Virtual Network (VNet) Integration**:
   * Enable **VNet Integration** on the App Service so the container communicates privately with internal Storybook instances and Azure DevOps without exposing traffic to the public internet.
2. **Private Endpoint**:
   * Create an Azure Private Endpoint for the App Service so only workstations connected to the corporate VPN or internal corporate network can access `https://wbg-design-system-mcp.azurewebsites.net`.
3. **API Key Protection**:
   * The `MCP_API_KEY` prevents unauthorized AI agents or crawlers from executing tools or streaming tokens.
   * `CloudAuthMiddleware` in `server.py` validates the `Authorization: Bearer <key>` header on every incoming SSE request.
4. **ALB Probe Exemption**:
   * `GET /health` is explicitly bypassed from authentication in `CloudAuthMiddleware`, ensuring Azure Load Balancers and Application Gateways never receive 401 Unauthorized errors during health probes.

---

## 10. Operational Verification & Troubleshooting Cheatsheet

### 1. Test Server Liveness Probe from Terminal:
```bash
curl -i https://wbg-design-system-mcp.azurewebsites.net/health
```
**Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status":"healthy","service":"enterprise-design-system-mcp"}
```

### 2. Test Protected SSE Endpoint Without Auth (Should Return 401):
```bash
curl -i https://wbg-design-system-mcp.azurewebsites.net/sse
```
**Expected Response**:
```http
HTTP/1.1 401 Unauthorized
{"error": "Unauthorized. Missing or invalid Authorization header."}
```

### 3. Test Protected SSE Endpoint With Auth (Should Return SSE Stream):
```bash
curl -N -H "Authorization: Bearer <YOUR_MCP_API_KEY>" https://wbg-design-system-mcp.azurewebsites.net/sse
```
**Expected Response**:
```text
event: endpoint
data: /messages/?session_id=...
```

### 4. View Container Logs in Real Time:
```bash
az webapp log tail --resource-group rg-wbg-mcp-prod --name wbg-design-system-mcp
```
