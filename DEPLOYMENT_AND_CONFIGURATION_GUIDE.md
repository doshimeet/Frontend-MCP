# Master Production Deployment Runbook: Nexus Design System (v2.0.0) Azure App Service QA Slot FastMCP Engine

A complete, zero-omission enterprise guide detailing how to configure, deploy, and operate the **Nexus Design System FastMCP Server (v2.0.0)** on **Azure App Service Linux (Python 3.11 Runtime)** across deployment slots (QA $\rightarrow$ Production), integrate with World Bank Group internal digital assets (`@wbg/nexus`), and connect AI coding agents (Antigravity, GitHub Copilot in VS Code, Claude Code).

---

## 1. Enterprise Architecture & Traffic Flow

```text
========================================================================================================================
                                      ENTERPRISE CLOUD ARCHITECTURE & TRAFFIC FLOW
========================================================================================================================

  DEVELOPER WORKSTATION / IDE
  ┌────────────────────────────────────────────────────────┐
  │ VS Code / Antigravity IDE / GitHub Copilot             │
  │ • Target: https://<wbg-mcp-qa>.azurewebsites.net/sse   │
  │ • Header: Authorization: Bearer <MCP_API_KEY>          │
  └───────────────────────────┬────────────────────────────┘
                              │
                              │ 1. HTTPS / SSE (Port 443)
                              ▼
  AZURE APP SERVICE QA DEPLOYMENT SLOT (<wbg-mcp-qa>.azurewebsites.net)
  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Managed Linux Host (Python 3.11 Stack) — Application Root: /home/site/wwwroot                                     │
  │                                                                                                                    │
  │   [Oryx Build Engine]                                                                                              │
  │   • Triggers on Git push to QA branch (SCM_DO_BUILD_DURING_DEPLOYMENT = true)                                      │
  │   • Executes: pip install -r requirements.txt                                                                      │
  │                                                                                                                    │
  │   [ASGI Startup Engine]                                                                                            │
  │   • Startup Command: python server.py (or startup.sh)                                                              │
  │   • Binds Uvicorn to 0.0.0.0:8000 (respecting $PORT and $WEBSITES_PORT)                                           │
  │                                                                                                                    │
  │   [FastMCP Application & Security Layer]                                                                           │
  │   ├── CloudAuthMiddleware: Validates Bearer Token / x-api-key header on /sse and /messages/                        │
  │   ├── GET /health: Dedicated unauthenticated probe for Azure ALB / App Service health monitor (HTTP 200)           │
  │   │                                                                                                                │
  │   ├── [Connectors Layer]                                                                                           │
  │   │   ├── ado_connector.py      ──► Azure DevOps REST API (Branch: starter-kit, MSAL / PAT fallback)               │
  │   │   ├── storybook_connector.py ──► Live WBG Storybook (https://storybook.internal.company.com)                 │
  │   │   │                             Target Manifest: /design-system/index.json                                     │
  │   │   │                             Priority: 1. Live Storybook ──► 2. components.json ──► 3. Local Cache          │
  │   │   └── npm_connector.py       ──► Verifies zero .npmrc repository compliance                                    │
  │   │                                                                                                                │
  │   └── [Embedded Baseline Assets]                                                                                   │
  │       ├── packages/tokens/       ──► DTCG Standard Tokens (wbg-enterprise.json, enterprise-dark.json)               │
  │       ├── packages/recipes/      ──► Canonical Recipes (@wbg/nexus shadcn architecture)                    │
  │       └── templates/frontend-starter/ ──► Next.js 14 Corporate Starter Kit (MSAL, AppInsights, AdobeAnalytics)     │
  └───────────────────────────┬────────────────────────────────────────────────────────┬───────────────────────────────┘
                              │                                                        │
                              │ 2. Azure DevOps REST ZIP Sync (Branch: starter-kit)    │ 3. Manifest Ingestion
                              ▼                                                        ▼
  ┌────────────────────────────────────────────────────────┐ ┌─────────────────────────────────────────────────────────┐
  │ Azure DevOps Git Repository                            │ │ Internal World Bank Group Storybook                     │
  │ https://dev.azure.com/{org}/{project}/_git/starter-kit │ │ https://storybook.internal.company.com/                 │
  │ (Resilient startup refresh; retains local snapshot)    │ │ Manifest: /design-system/index.json                     │
  └────────────────────────────────────────────────────────┘ └─────────────────────────────────────────────────────────┘
========================================================================================================================
```

---

## 2. Infrastructure & Application Specification Matrix

| Component | Target Cloud Specification (QA Slot) | Operational Rule |
| :--- | :--- | :--- |
| **Hosting Platform** | Azure App Service Linux | Standard Code Deployment (Python 3.11 Runtime) |
| **Deployment Slot** | `QA` (or `staging`) | Connected to Azure DevOps Git branch `QA` |
| **Root Directory** | `/home/site/wwwroot` | Unified flat structure across root files |
| **Build Engine** | Azure Oryx | `SCM_DO_BUILD_DURING_DEPLOYMENT = true` |
| **Dependencies** | `requirements.txt` at root | Pinned Python packages (`mcp`, `starlette`, `uvicorn`, etc.) |
| **Startup Command** | `python server.py` | Launches Uvicorn in cloud mode on `0.0.0.0:8000` |
| **Ingress Port** | Port 8000 | Configured via `PORT=8000` or `WEBSITES_PORT=8000` |
| **Container Engine**| **Zero Docker** | Dockerfile and container registry retired |
| **Liveness Probe** | `GET /health` | Unauthenticated HTTP 200 JSON status |
| **Transport** | Server-Sent Events (SSE) | Authenticated via `MCP_API_KEY` header |
| **Design System** | `@wbg/nexus@version` | Internal Artifactory package (`design-system-shadcn-1`) |
| **Global Styles** | `@wbg/nexus/styles.css` | Plain CSS import in `globals.css` / `layout.tsx` |
| **Artifactory Auth**| Workstation / CI/CD Global | **Zero `.npmrc`** in Git repository |
| **Storybook URL** | `https://storybook.internal.company.com` | Configurable via `STORYBOOK_URL` app setting |
| **Storybook Path**| `/design-system/index.json` | Harvester prioritizes `/design-system/index.json` |
| **Catalog Priority**| 3-Tier Resilient Resolution | 1. Live Storybook $\rightarrow$ 2. `components.json` $\rightarrow$ 3. Local Cache |
| **Starter Kit Branch**| `starter-kit` | `versionDescriptor.version=starter-kit&versionDescriptor.versionType=branch` |
| **Startup Refresh**| Cloud Boot Auto-Sync | Pulls latest starter kit; retains local snapshot on failure |

---

## 3. Azure App Service Slot Setup & Configuration

### Step 1: Provision App Service Plan and QA Slot
1. In the Azure Portal or Azure CLI, ensure an App Service Plan with Linux Python 3.11 is created (Standard S1 or Premium P1v3 recommended for SLA and deployment slot support):
   ```bash
   az appservice plan create \
     --name asp-wbg-mcp-prod \
     --resource-group rg-wbg-mcp-prod \
     --is-linux \
     --sku P1v3
   ```
2. Create the main Web App:
   ```bash
   az webapp create \
     --name wbg-mcp-service \
     --resource-group rg-wbg-mcp-prod \
     --plan asp-wbg-mcp-prod \
     --runtime "PYTHON:3.11"
   ```
3. Create the **QA Deployment Slot**:
   ```bash
   az webapp deployment slot create \
     --name wbg-mcp-service \
     --resource-group rg-wbg-mcp-prod \
     --slot qa
   ```

---

### Step 2: Configure Application Settings & Secrets
Navigate to the QA slot under **Settings > Environment variables** (or **Configuration**):

| Key | Value / Example | Slot Setting (Sticky)? |
| :--- | :--- | :---: |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | Yes |
| `MCP_MODE` | `uvicorn` | Yes |
| `PORT` | `8000` | Yes |
| `MCP_HOST` | `0.0.0.0` | Yes |
| `MCP_API_KEY` | *(Secret GUID or 64-char key)* | Yes |
| `STORYBOOK_URL` | `https://storybook.internal.company.com` | No |
| `STORYBOOK_MANIFEST_PATH` | `/design-system/index.json` | No |
| `AZURE_DEVOPS_ORG` | `https://dev.azure.com/wbg-digital` | No |
| `AZURE_DEVOPS_PROJECT` | `EnterprisePlatform` | No |
| `AZURE_DEVOPS_STARTER_REPO_ID` | `wbg-frontend-starter` | No |
| `AZURE_DEVOPS_BRANCH` | `starter-kit` | Yes |
| `AZURE_DEVOPS_PAT` | *(Secret read-only PAT for fallback)* | Yes |

*Note: Check "Deployment slot setting" on slot-specific secrets (`MCP_API_KEY`, `AZURE_DEVOPS_BRANCH`) so they remain with the QA slot during slot swaps.*

---

### Step 3: Configure Startup Command
In the QA slot, navigate to **Settings > Configuration > General settings > Startup Command** and enter:
```bash
python server.py
```
*(Alternatively, you can specify `startup.sh`)*

---

### Step 4: Link Azure DevOps Git Repository (Continuous Deployment)
1. Open the QA slot in Azure Portal and go to **Deployment > Deployment Center**.
2. Select **Source**: Azure Repos (or GitHub).
3. Select your organization, project, repository (`Frontend-MCP` or `Design System`), and set **Branch**: `QA`.
4. Click **Save**. Azure App Service will link the webhook and trigger an automated Oryx build on every commit pushed to `QA`.

---

## 4. API Endpoints & Developer IDE Integration

### The Live MCP Endpoints
Once running, the QA slot exposes three endpoints:

1. **ALB / Load Balancer Health Probe**:
   - `GET https://wbg-mcp-service-qa.azurewebsites.net/health`
   - Unauthenticated. Returns:
     ```json
     {
       "status": "UP",
       "service": "nexus-mcp",
       "version": "2.0.0",
       "transport": "uvicorn"
     }
     ```
2. **Server-Sent Events (SSE) Channel**:
   - `GET https://wbg-mcp-service-qa.azurewebsites.net/sse`
   - Headers: `Authorization: Bearer <MCP_API_KEY>` or `x-api-key: <MCP_API_KEY>`
3. **JSON-RPC Message Dispatcher**:
   - `POST https://wbg-mcp-service-qa.azurewebsites.net/messages/?session_id=<id>`
   - Authenticated tool invocations (`create_enterprise_app`, `audit_accessibility`, `plan_application_architecture`).

---

### Developer IDE Configuration

#### VS Code (`.vscode/settings.json`)
```json
{
  "mcp": {
    "servers": {
      "nexus-design-system": {
        "url": "https://wbg-mcp-service-qa.azurewebsites.net/sse",
        "headers": {
          "Authorization": "Bearer YOUR_MCP_API_KEY_HERE"
        }
      }
    }
  }
}
```

#### Antigravity IDE (`~/.gemini/config/mcp_config.json`)
```json
{
  "mcpServers": {
    "nexus-design-system": {
      "serverUrl": "https://wbg-mcp-service-qa.azurewebsites.net/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY_HERE"
      }
    }
  }
}
```

---

## 5. Enterprise Verification & Zero-Downtime Slot Swapping

### Verification Checklist on QA Slot
Before swapping to Production, verify the QA slot:
1. Verify Health:
   ```bash
   curl -I https://wbg-mcp-service-qa.azurewebsites.net/health
   # Must return HTTP/2 200 OK
   ```
2. Verify Tool Invocations:
   Use the CLI test harness or IDE chat to run `check_system_health` and `list_page_recipes`.
3. Verify Storybook Manifest:
   Ensure `get_components` returns components from live Storybook or `components.json`.

---

### Zero-Downtime Slot Swap
Once verified on the QA slot, swap QA into Production with **zero downtime**:

```bash
az webapp deployment slot swap \
  --resource-group rg-wbg-mcp-prod \
  --name wbg-mcp-service \
  --slot qa \
  --target-slot production
```

During the swap:
- Azure warms up the target instances using the `/health` probe.
- Traffic is dynamically routed via Azure front-end load balancers.
- Zero requests are dropped.

---

## 6. Corporate Scaffolding & Zero `.npmrc` Policy

When developers invoke `create_enterprise_app` through the cloud MCP server:
1. **Source**: The server extracts the corporate starter kit from the `starter-kit` branch in Azure DevOps (with resilient local snapshot fallback).
2. **Architecture**: It provisions:
   - `src/components/MsalAuthentication.tsx` (MSAL auth shell)
   - `src/components/AdobeAnalytics.tsx` (Omniture event tracking)
   - `src/components/AppInsights.tsx` (Azure Application Insights)
   - `src/services/` & `src/data/` (Clean service layer separation)
   - `web.config` and `copymain.js` (Azure App Service IIS / Node hosting)
   - `src/tests/home.spec.ts` (Playwright E2E suite)
   - Plain CSS tokens importing `@wbg/nexus/styles.css`
3. **Zero `.npmrc` Enforcement**:
   - The engine explicitly deletes any `.npmrc` file during scaffolding.
   - Developers install `@wbg/nexus` seamlessly using their corporate laptop `~/.npmrc` or Azure DevOps `NpmAuthenticate@0` pipeline tasks without leaking credentials into Git.

---

## 7. Multi-Environment Architecture & Auto-Detection

The MCP server operates seamlessly across 3 development environments with zero-config auto-detection:

| Mode | Environment Target | Component Package | Dependency Registry | Auto-Detection Trigger |
| :--- | :--- | :--- | :--- | :--- |
| **`standalone`** | Local Personal Laptop / Offline Outside VPN | Pure React + Tailwind CSS + `nexus-tokens.css` | Public npm (Zero private package required) | Default fallback when Artifactory is unreachable |
| **`wbg`** | Local Enterprise Laptop | `@wbg/nexus` | Private Artifactory | Active Azure DevOps PAT or reachable internal Artifactory |
| **`cloud`** | Azure App Service Container | Official `@wbg/nexus` / Standalone Engine | Linux Python 3.11 / Oryx | `WEBSITE_SITE_NAME` or `MCP_MODE=uvicorn` |

### 7.1 Native Tailwind CSS Compilation & Zero-Mock Policy
1. **Native Tailwind Pipeline**: The starter template compiles Tailwind CSS via `postcss.config.mjs` and `tailwind.config.ts`, directly mapping DTCG design tokens (`--nexus-color-*`, `--nexus-elevation-*`). Utility classes (`flex`, `grid`, `justify-between`, `gap-4`) compile natively without requiring private package downloads.
2. **Strict Zero-Mock Policy**: Codified in `.agents/skills/wbg-enterprise-rules.md` (Section 1.4), AI coding agents are strictly forbidden from synthesizing fake mock packages (e.g. `src/nexus/index.tsx`) or manual `node_modules` symlinks. When private packages are unavailable, agents compose standard React, Tailwind CSS, and Nexus token CSS variables directly.

### Dynamic Port Probing Chain
To avoid rigid localhost assumptions, the runtime probes candidate ports in order:
1. **Port 3000 / 3001**: Next.js / Create-React-App default
2. **Port 4200**: Angular CLI / Enterprise Micro-Frontends
3. **Port 5173**: Vite default dev server

---

## 8. Canonical Page Recipes & Companion Playwright Specs

The enterprise catalog delivers 6 pre-composed, production-tested layout patterns with companion Playwright `.spec.ts` test suites using semantic W3C ARIA locators (`getByRole`, `getByLabel`):

1. **`CrudTableRecipe`**: Tabular records, status badges, search filter, loading skeleton, empty states.
2. **`MetricsDashboardRecipe`**: Executive KPI cards, trend comparisons, event telemetry table, date filters.
3. **`FormWizardRecipe`**: Multi-step intake flow, step progress tracker, field validation, confirmation summary.
4. **`MasterDetailRecipe`**: Split-pane directory on left, comprehensive inspector with approval chain and tabs on right.
5. **`SettingsTabsRecipe`**: Tabbed portal governance layout covering domains, Entra ID MFA, and API secrets.
6. **`AuditTimelineRecipe`**: Chronological event stream, status transition badges, expandable JSON diff telemetry.

### Dual-Asset FastMCP Retrieval:
- `get_page_recipe(recipe_name)`: Returns `PageRecipeResponse` with both `.tsx` component code and `.spec.ts` companion test spec.
- `get_recipe_test(recipe_name)`: Directly extracts the companion Playwright test specification.

---

## 9. Universal Application Health Diagnostics

The server provides a universal, starter-kit agnostic health diagnostics tool:
```json
verify_application_health({
  "url": null
})
```

### Capabilities:
- **Automatic Port Probing**: Scans candidate ports `[3000, 3001, 4200, 5173]` if no explicit URL is passed.
- **Console Exception Trapping**: Captures browser runtime `console.error` and unhandled page exceptions.
- **Network Failure Detection**: Logs failing HTTP 4xx and 5xx API calls.
- **Interactive Element Audit**: Counts focusable landmarks (`button`, `a[href]`, `input`, `select`, `tab`).
- **WCAG 2.1 AA Evaluation**: Injects and runs `axe-core` to flag critical and serious accessibility violations.

---

## 10. Single Source of Truth & Cloud Deployment Workflow

To eliminate drift between local development and cloud deployment, maintain `/Users/.../Design System` as the **Single Source of Truth (SSOT)**:

### Daily Workflow:
1. **Develop & Test in `Design System`**:
   ```bash
   npm run mcp:test    # Runs all 69 unit and integration tests
   ```
2. **Synchronize to Cloud Mirror**:
   ```bash
   npm run sync:cloud  # Safe rsync preserving .git, node_modules, and cache
   ```
3. **Deploy to Azure App Service QA Slot**:
   ```bash
   cd "/Users/meetketankumardoshi/Frontend-MCP"
   git add .
   git commit -m "feat: synchronize latest design system updates"
   git push origin QA
   ```

