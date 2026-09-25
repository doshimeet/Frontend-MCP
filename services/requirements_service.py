"""
Requirements & PRD Processing Service
Translates business requirements, PRDs, and visual mockups into structured architectural blueprints.
Supports both pattern-matching accelerators (recipes) and bespoke open compositions (anti-force-fitting).
"""

import re
from typing import List, Optional
from config import ACTIVE_MODE
from models.requirements import PlannedRoute, RequirementBlueprint


class RequirementsService:
    """Parses natural language requirements or visual mockups and outputs structured architectural plans."""

    COMMON_ENTITIES = [
        "projects", "disbursements", "tenders", "contracts", "clusters", "invoices",
        "patients", "members", "users", "assets", "accounts", "workflows", "reports",
        "models", "deployments", "providers", "transactions", "beneficiaries"
    ]

    BESPOKE_KEYWORDS = [
        "kanban", "board", "chat", "map", "canvas", "interactive map", "topology",
        "diagram", "split-pane", "document reviewer", "mockup", "screenshot", "wireframe",
        "single page", "single screen", "only page"
    ]

    def _extract_primary_entity(self, text: str) -> str:
        """Extracts primary domain entity name based on earliest appearance in prompt."""
        lower = text.lower()

        earliest_pos = 999999
        best_entity = None
        for entity in self.COMMON_ENTITIES:
            for form in (entity, entity.rstrip("s")):
                pattern = r'\b' + re.escape(form) + r'\b'
                match = re.search(pattern, lower)
                if match and match.start() < earliest_pos:
                    earliest_pos = match.start()
                    best_entity = entity

        if best_entity:
            return best_entity

        match = re.search(r'\b(manage|track|view|list|audit|monitor)\s+([a-z]{3,15}s)\b', lower)
        if match:
            return match.group(2)

        return "records"

    def _detect_input_modality(self, text: str) -> str:
        """Detects whether input is a text PRD, visual mockup, or hybrid."""
        lower = text.lower()
        has_mockup = any(k in lower for k in ["mockup", "screenshot", "wireframe", "image", "figma", "png", "jpg"])
        has_prd = any(k in lower for k in ["prd", "requirements", "user story", "acceptance criteria", "specification"])

        if has_mockup and has_prd:
            return "hybrid"
        if has_mockup:
            return "visual_mockup"
        return "text_prd"

    def _detect_bespoke_intent(self, text: str) -> bool:
        """Detects if the request demands a bespoke/custom layout rather than standard CRUD portals."""
        lower = text.lower()
        return any(k in lower for k in self.BESPOKE_KEYWORDS)

    def plan_architecture(
        self,
        requirements_text: str,
        theme: str = "default",
        mode: Optional[str] = None
    ) -> RequirementBlueprint:
        """
        Analyzes requirements text or visual mockup description and returns a typed RequirementBlueprint.
        Ensures zero force-fitting: leverages canonical recipes when matched, or provides open composition when bespoke.
        """
        lower = requirements_text.lower()
        primary_entity = self._extract_primary_entity(requirements_text)
        entity_title = primary_entity.replace("-", " ").title()
        modality = self._detect_input_modality(requirements_text)
        is_bespoke = self._detect_bespoke_intent(requirements_text)
        active_mode = mode or ACTIVE_MODE

        from config import NEXUS_PACKAGE_NAME
        if active_mode == "standalone":
            package_name = "Standalone (Tailwind CSS + Nexus Tokens)"
        else:
            package_name = NEXUS_PACKAGE_NAME

        routes: List[PlannedRoute] = []

        # -------------------------------------------------------------
        # Branch A: Bespoke / Custom Mockup Layout (Zero Force-Fitting)
        # -------------------------------------------------------------
        if is_bespoke and not any(k in lower for k in ["audit", "annual metrics", "multi-page", "system", "portal"]):
            target_path = f"/{primary_entity}" if primary_entity != "records" else "/workspace"
            routes.append(PlannedRoute(
                path=target_path,
                title=f"{entity_title} Custom Workspace",
                layout_type="open_composition",
                recipe=None,  # Anti-force-fit: NO generic recipe forced
                components=["Card", "Tabs", "Sheet", "Badge", "Button", "Dialog", "Input"],
                composition_guide=(
                    f"Bespoke layout: Assemble UI using atomic {package_name} components. "
                    "Bind colors, spacing, and typography strictly to DTCG design tokens. "
                    "Do NOT force into a standard table or dashboard template."
                ),
                suggested_test_file=f"src/tests/{primary_entity}.spec.ts",
                purpose=f"Specialized {entity_title.lower()} interface tailored to user mockup/specification.",
            ))
            archetype = "Bespoke Workspace"

        # -------------------------------------------------------------
        # Branch B: Standard Enterprise Portal (Table / Dashboard / Form)
        # -------------------------------------------------------------
        else:
            has_table = any(k in lower for k in ["table", "list", "grid", "log", "records", "view", "manage", "search", "procurement", "finance", "audit"] + self.COMMON_ENTITIES)
            has_dashboard = any(k in lower for k in ["dashboard", "metrics", "analytics", "kpi", "chart", "performance", "overview", "telemetry"])
            has_form = any(k in lower for k in ["form", "intake", "wizard", "create", "register", "booking", "new", "add"])
            has_master_detail = any(k in lower for k in ["master-detail", "split-pane", "inspector", "drawer", "detail view", "case review"])
            has_timeline = any(k in lower for k in ["timeline", "audit trail", "event stream", "history log"])
            has_settings = any(k in lower for k in ["settings", "preferences", "configuration", "credentials"])

            # 1. Executive Operations Landing (Root)
            routes.append(PlannedRoute(
                path="/",
                title=f"{entity_title} Overview & Operations",
                layout_type="recipe",
                recipe="MetricsDashboardRecipe",
                components=["Card", "Badge", "Table", "Button"],
                composition_guide=f"Pre-wired executive metrics dashboard importing from {package_name}.",
                suggested_test_file="src/tests/home.spec.ts",
                purpose="Executive operational landing page with summary metrics and quick actions.",
            ))

            # 2. Master-Detail Inspector or Tabular Directory Route
            if has_master_detail:
                routes.append(PlannedRoute(
                    path=f"/{primary_entity}",
                    title=f"{entity_title} Master-Detail Inspector",
                    layout_type="recipe",
                    recipe="MasterDetailRecipe",
                    components=["Table", "Sheet", "Tabs", "Badge", "Button"],
                    composition_guide=f"Split-pane layout: Searchable list on left, detail drawer on right importing from {package_name}.",
                    suggested_test_file=f"src/tests/{primary_entity}-inspector.spec.ts",
                    purpose=f"Master-detail review and inspection for {entity_title.lower()} records.",
                ))
            elif has_timeline:
                routes.append(PlannedRoute(
                    path=f"/{primary_entity}/audit",
                    title=f"{entity_title} Audit Timeline",
                    layout_type="recipe",
                    recipe="AuditTimelineRecipe",
                    components=["Card", "Badge", "Table", "Button"],
                    composition_guide=f"Chronological activity and governance stream importing from {package_name}.",
                    suggested_test_file=f"src/tests/{primary_entity}-timeline.spec.ts",
                    purpose=f"Audit trail and state change history for {entity_title.lower()}.",
                ))
            elif has_table or not has_dashboard:
                routes.append(PlannedRoute(
                    path=f"/{primary_entity}",
                    title=f"{entity_title} Directory & Management",
                    layout_type="recipe",
                    recipe="CrudTableRecipe",
                    components=["Table", "Input", "Tag", "Button", "Dialog"],
                    composition_guide=f"Accessible tabular record viewer with filters and pagination importing from {package_name}.",
                    suggested_test_file=f"src/tests/{primary_entity}.spec.ts",
                    purpose=f"Tabular {entity_title.lower()} viewer with search, filtering, and state management.",
                ))

            # 3. Dedicated entity creation / intake wizard route
            if has_form:
                routes.append(PlannedRoute(
                    path=f"/{primary_entity}/new",
                    title=f"New {entity_title.rstrip('s')} Intake & Setup Wizard",
                    layout_type="recipe",
                    recipe="FormWizardRecipe",
                    components=["Input", "Select", "Button", "Dialog"],
                    composition_guide=f"Multi-step progressive intake form with inline validation importing from {package_name}.",
                    suggested_test_file=f"src/tests/{primary_entity}-new.spec.ts",
                    purpose="Step-by-step form collection with validation and confirmation.",
                ))

            # 4. Settings route if requested
            if has_settings:
                routes.append(PlannedRoute(
                    path="/settings",
                    title=f"{entity_title} Configuration & Settings",
                    layout_type="recipe",
                    recipe="SettingsTabsRecipe",
                    components=["Tabs", "Input", "Button", "Card"],
                    composition_guide=f"Multi-section tabbed settings and credentials layout importing from {package_name}.",
                    suggested_test_file="src/tests/settings.spec.ts",
                    purpose="Application settings, access keys, and notification preferences.",
                ))

            archetype = "Entity Management Portal"

        return RequirementBlueprint(
            summary=f"Technical Architecture Plan for {entity_title} domain.",
            target_theme=theme,
            input_modality=modality,
            active_mode=active_mode,
            application_archetype=archetype,
            recommended_routes=routes,
            design_rules_summary=[
                "Follow DESIGN.md guidelines strictly.",
                (
                    "Active mode is 'standalone' (offline / personal laptop outside WBG VPN). "
                    "Assemble UI using standard React components styled with Tailwind CSS and Nexus tokens (var(--nexus-*)). "
                    "Do NOT import '@wbg/nexus', and NEVER synthesize fake mock packages or symlinks."
                    if active_mode == "standalone"
                    else f"Active mode is '{active_mode}'. Use components from '{package_name}'."
                ),
                "Prefer design system catalog components; compose or build token-constrained custom components with clean CSS variables when specialized UX is needed.",
                "Anti-Force-Fit: If a route has recipe: null, compose directly from atomic primitives rather than contorting into an ill-fitting pattern.",
                "Ensure high-contrast WCAG 2.1 AA compliance (4.5:1 text, 3:1 graphical elements).",
                "Wire structured data hooks with loading, error, and empty states.",
                "Co-generate companion Playwright .spec.ts tests for every generated page.",
                "Run Impeccable critique pass (/distill, /polish, /harden) before finalizing.",
            ],
        )

    # Convenience alias
    plan_from_text = plan_architecture

