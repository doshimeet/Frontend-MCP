"""
Requirements & PRD Processing Service
Translates business requirements into structured architectural blueprints with dynamic domain routes.
"""

import re
from typing import List
from models.requirements import PlannedRoute, RequirementBlueprint


class RequirementsService:
    """Parses natural language requirements or PRDs and outputs structured architectural plans."""

    COMMON_ENTITIES = [
        "projects", "disbursements", "tenders", "contracts", "clusters", "invoices",
        "patients", "members", "users", "assets", "accounts", "workflows", "reports",
        "models", "deployments", "providers", "transactions", "beneficiaries"
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

    def plan_architecture(self, requirements_text: str, theme: str = "default") -> RequirementBlueprint:
        """Analyzes requirements text and returns a typed RequirementBlueprint."""
        lower = requirements_text.lower()
        primary_entity = self._extract_primary_entity(requirements_text)
        entity_title = primary_entity.replace("-", " ").title()

        has_table = any(k in lower for k in ["table", "list", "grid", "log", "records", "view", "manage", "search"] + self.COMMON_ENTITIES)
        has_dashboard = any(k in lower for k in ["dashboard", "metrics", "analytics", "kpi", "chart", "performance", "overview", "telemetry"])
        has_form = any(k in lower for k in ["form", "intake", "wizard", "create", "register", "booking", "new", "add"])

        routes: List[PlannedRoute] = []

        # Standard enterprise layout: Root dashboard
        routes.append(PlannedRoute(
            path="/",
            title=f"{entity_title} Overview & Operations",
            recipe="MetricsDashboardRecipe",
            components=["Tile", "Tag", "DataTable", "SkeletonText", "Button"],
            purpose="Executive operational landing page with summary metrics and quick actions.",
        ))

        # Dedicated entity tabular directory route
        if has_table or not has_dashboard:
            routes.append(PlannedRoute(
                path=f"/{primary_entity}",
                title=f"{entity_title} Directory & Management",
                recipe="CrudTableRecipe",
                components=["DataTable", "TextInput", "Tag", "Button", "Modal", "Pagination"],
                purpose=f"Tabular {entity_title.lower()} viewer with search, filtering, and state management.",
            ))

        # Dedicated entity creation / wizard route
        if has_form:
            routes.append(PlannedRoute(
                path=f"/{primary_entity}/new",
                title=f"New {entity_title.rstrip('s')} Intake & Setup Wizard",
                recipe="FormWizardRecipe",
                components=["TextInput", "Select", "Button", "Modal"],
                purpose="Step-by-step form collection with validation and confirmation.",
            ))

        return RequirementBlueprint(
            summary=f"Technical Architecture Plan for {entity_title} domain.",
            target_theme=theme,
            recommended_routes=routes,
            design_rules_summary=[
                "Follow DESIGN.md guidelines strictly.",
                "Prefer design system catalog components; compose or build token-constrained custom components with clean CSS variables when specialized UX is needed.",
                "Ensure high-contrast WCAG 2.1 AA compliance (4.5:1 text, 3:1 graphical elements).",
                "Wire structured data hooks with loading, error, and empty states.",
                "Enforce empty states and loading skeletons.",
                "Run Impeccable critique pass (/distill, /polish, /harden) before finalizing.",
            ],
        )
