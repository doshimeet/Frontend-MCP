# Master Workflow: AI-Native Frontend Generation Pipeline (`build-ui.md`)

This workflow defines the mandatory, end-to-end execution pipeline for AI coding agents (Antigravity, VS Code GitHub Copilot, Claude Code) generating or extending user interfaces within this enterprise ecosystem.

```text
====================================================================================================
                        AUTOMATED 5-STAGE FRONTEND EXECUTION PIPELINE
====================================================================================================
  [PRD / Prompt]
        │
        ▼
  Stage 1: Ingest & Architectural Planning  ──► plan_application_from_requirements & design://tokens
        │
        ▼
  Stage 2: Project Context & Safety Check   ──► scaffold_greenfield_app OR integrate_into_existing_app
        │
        ▼
  Stage 3: Canonical Recipe Assembly        ──► list_page_recipes, get_page_recipe, get_component_props
        │
        ▼
  Stage 4: 4-Pass Impeccable Critique Loop  ──► /distill ──► /polish ──► /clarify ──► /harden
        │
        ▼
  Stage 5: Verification & Compilation       ──► npm run build & Headless Edge Playwright Audit
====================================================================================================
```

---

## Stage 1: Ingestion & Architectural Planning

1. **Invoke MCP Requirement Planner**:
   Call FastMCP tool:
   ```json
   plan_application_from_requirements({
     "requirements_text": "<USER_PRD_OR_FEATURE_PROMPT>",
     "theme": "default" | "enterprise-dark" | "client-warm-sage"
   })
   ```
2. **Stream Target Theme Tokens**:
   Read FastMCP passive resource:
   `design://tokens/{theme}`
   Extract approved primary color, canvas backgrounds, typography scales, and border radii.

---

## Stage 2: Project Context & Safety Check

### Greenfield Mode (New Project)
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

1. **Select Canonical Layout**:
   Call `list_page_recipes()` and select the matching foundation:
   - Tabular data, lists, logs $\rightarrow$ `CrudTableRecipe`
   - Executive analytics, telemetry, KPIs $\rightarrow$ `MetricsDashboardRecipe`
   - Multi-step intake, registration, wizard $\rightarrow$ `FormWizardRecipe`
2. **Fetch Starter Blueprint**:
   Call FastMCP tool `get_page_recipe(recipe_name)` or read `recipe://{recipe_name}`.
3. **Verify Component Interfaces**:
   For any custom controls added, call `get_component_props(component_name)` to ensure all TypeScript prop types match `@carbon/react` specifications.

---

## Stage 4: The 4-Pass Impeccable Critique Loop

Before presenting or saving any generated TSX code, execute the 4 Impeccable design passes:

### Pass 1: `/distill` ([distill.md](../skills/impeccable/distill.md))
- [ ] Are there nested cards inside cards? $\rightarrow$ Flatten to single-level elevation.
- [ ] Is there "status-chip soup"? $\rightarrow$ Remove badges from non-status fields.
- [ ] Is information density appropriate for enterprise desktop scanning?

### Pass 2: `/polish` ([polish.md](../skills/impeccable/polish.md))
- [ ] Are there random italicized words in headers? $\rightarrow$ Remove italics.
- [ ] Are there AI beige or muddy washed-out backgrounds? $\rightarrow$ Replace with crisp tokens.
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
2. **Headless Browser Verification**:
   Execute the automated Playwright verification loop (Edge channel) with `axe-core` accessibility audit.
