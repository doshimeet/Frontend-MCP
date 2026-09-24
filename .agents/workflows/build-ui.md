# Master Workflow: AI-Native Frontend Generation Pipeline (`build-ui.md`)

This workflow defines the mandatory, end-to-end execution pipeline for AI coding agents (Antigravity, VS Code GitHub Copilot, Claude Code) generating or extending user interfaces within this enterprise ecosystem.

```text
====================================================================================================
                        AUTOMATED 5-STAGE FRONTEND EXECUTION PIPELINE
====================================================================================================
  [PRD / Prompt OR Visual Mockup (Figma/Screenshot)]
        │
        ▼
  Stage 1: Ingestion & Architectural Planning  ──► resolve_active_mode ('carbon' | 'wbg' | 'cloud')
        │                                          & plan_application_from_requirements
        ▼
  Stage 2: Project Context & Safety Check      ──► scaffold_greenfield_app OR integrate_into_existing_app
        │
        ▼
  Stage 3: Canonical Recipe Assembly           ──► list_page_recipes, get_page_recipe, get_recipe_test
        │                                          (Canonical Recipes OR Open Composition)
        ▼
  Stage 4: The 4-Pass Impeccable Critique Loop ──► /distill ──► /polish ──► /clarify ──► /harden
        │
        ▼
  Stage 5: Verification & Compilation          ──► verify_application_health (ports 3000, 3001, 4200, 5173)
====================================================================================================
```

---

## Stage 1: Ingestion & Architectural Planning

1. **Auto-Detect Active Environment Mode**:
   The system automatically selects the target mode:
   - `carbon`: Non-enterprise local machine / personal laptop (uses `@carbon/react` on public npm; zero VPN or private credentials required).
   - `wbg`: Enterprise workstation (uses `@wbg/design-system` on private Artifactory).
   - `cloud`: Azure App Service container (Linux Python 3.11, Oryx, Server-Sent Events).
2. **Detect Input Modality**:
   - **Text PRD**: Ingest user requirements or functional specifications.
   - **Visual Mockup**: Ingest design screenshots, wireframes, or Figma exports.
3. **Invoke MCP Requirement Planner**:
   Call FastMCP tool:
   ```json
   plan_application_from_requirements({
     "requirements_text": "<USER_PRD_OR_FEATURE_PROMPT>",
     "theme": "default" | "enterprise-dark" | "client-warm-sage"
   })
   ```
4. **Stream Target Theme Tokens**:
   Read FastMCP passive resource `design://tokens/{theme}` to extract approved primary color, canvas backgrounds, typography scales, and border radii.

---

## Stage 2: Project Context & Safety Check

### Greenfield Mode (New Application)
1. **Confirm Path in Chat**: You MUST confirm the target directory with the user before writing files.
2. **Invoke Scaffolder**:
   ```json
   scaffold_greenfield_app({
     "app_name": "<app-name>",
     "target_directory": "<confirmed-path>"
   })
   ```

### Brownfield Mode (Existing Application)
1. **Inspect Target Application**:
   Call FastMCP tool:
   ```json
   integrate_into_existing_app({
     "project_path": "<project-root>",
     "page_route": "<route-path>"
   })
   ```
2. **Evaluate Conflict Alert**:
   - If `file_exists: true`: **HALT EXECUTION IMMEDIATELY**.
   - Output structured warning to user:
     `WARNING: Target file already exists at '<path>'. Request explicit permission to overwrite or provide an alternative route name.`

---

## Stage 3: Canonical Recipe Assembly

1. **Anti-Force-Fit Verification & Layout Selection**:
   Call `list_page_recipes()` and select the matching foundation:
   - Tabular records, entity lists, logs, pagination $\rightarrow$ `CrudTableRecipe`
   - Executive analytics, telemetry, KPIs $\rightarrow$ `MetricsDashboardRecipe`
   - Multi-step intake, registration, wizard $\rightarrow$ `FormWizardRecipe`
   - Split-pane case reviews, inspection drawers $\rightarrow$ `MasterDetailRecipe`
   - Portal governance, security controls, MFA, API keys $\rightarrow$ `SettingsTabsRecipe`
   - Chronological event streams, status badges, diffs $\rightarrow$ `AuditTimelineRecipe`
   - **Bespoke Layouts / Visual Mockups**: If the request requires custom composition, set `recipe: null`, `layout_type: "open_composition"`, and compose using atomic components (`packages/components/`) and design tokens (`packages/tokens/tokens.json`).
2. **Fetch Starter Blueprint**:
   Call FastMCP tool `get_page_recipe(recipe_name)` or read `recipe://{recipe_name}`.
3. **Retrieve Companion Playwright Spec**:
   Call `get_recipe_test(recipe_name)` to integrate semantic W3C ARIA test assertions.
4. **Verify Component Interfaces**:
   Call `get_component_props(component_name)` to ensure all TypeScript prop types match design system specifications.

---

## Stage 4: The 4-Pass Impeccable Critique Loop

Before presenting or saving any generated TSX code, execute the 4 Impeccable design passes:

### Pass 1: `/distill` ([distill.md](../skills/impeccable/distill.md))
- [ ] Are there nested cards inside cards? $\rightarrow$ Flatten to single-level elevation.
- [ ] Is there "status-chip soup"? $\rightarrow$ Remove badges from non-status fields.
- [ ] Is information density appropriate for enterprise desktop scanning?

### Pass 2: `/polish` ([polish.md](../skills/impeccable/polish.md))
- [ ] Are there random italicized words in headers? $\rightarrow$ Remove italics.
- [ ] Are there AI beige or muddy washed-out backgrounds? $\rightarrow$ Replace with crisp theme tokens.
- [ ] Are border radii consistent? $\rightarrow$ Enforce `none`, `sm` (2px), or `md` (4px).

### Pass 3: `/clarify` ([clarify.md](../skills/impeccable/clarify.md))
- [ ] Are button labels passive ("Submit", "Click here")? $\rightarrow$ Change to action verbs ("Register Service", "Export Log").
- [ ] Are destructive actions clear? $\rightarrow$ Specify exact resource name in danger modal.
- [ ] Do error messages provide a clear recovery path and retry button?

### Pass 4: `/harden` ([harden.md](../skills/impeccable/harden.md))
- [ ] Does loading state match the table/grid geometry using `SkeletonText`?
- [ ] Is there an empty state with a primary action button when zero items exist?
- [ ] Are color contrasts compliant with WCAG 2.1 AA (minimum 4.5:1)?
- [ ] Are all interactive elements accessible via keyboard with visible focus rings?

---

## Stage 5: Verification & Compilation

1. **Compile Production Bundle**:
   Run in terminal:
   ```bash
   npm run build
   ```
   Verify 0 TypeScript errors and 100% static page generation.
2. **Universal Health Diagnostics Tool**:
   Call FastMCP tool:
   ```json
   verify_application_health({
     "url": null
   })
   ```
   *Auto-Probes Candidate Ports*: `[3000, 3001, 4200, 5173]`.
   Verifies:
   - Dev server HTTP 200 response
   - 0 trapped browser `console.error` and unhandled exceptions
   - 0 failing HTTP 4xx/5xx network requests
   - Interactive element focusability
   - 0 critical `axe-core` accessibility violations
3. **Execute Companion Playwright Test Suite**:
   Run Playwright tests using semantic ARIA locators to validate resilient functional states.
