"""
Pydantic Schemas for Requirements, PRDs & Visual Mockup Blueprints
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class PlannedRoute(BaseModel):
    path: str = Field(description="URL path (e.g. '/' or '/invoices' or '/clusters')")
    title: str = Field(description="Page or feature title")
    layout_type: Literal["recipe", "open_composition", "custom_token_component"] = Field(
        default="recipe",
        description="Layout strategy: 'recipe' for canonical patterns, 'open_composition' for bespoke UIs, or 'custom_token_component'"
    )
    recipe: Optional[str] = Field(
        default=None,
        description="Canonical recipe accelerator (e.g. CrudTableRecipe), or None when layout is bespoke (anti-force-fit)"
    )
    components: List[str] = Field(
        default_factory=list,
        description="Key design system components needed (Button, Table, Card, Sheet, etc.)"
    )
    composition_guide: Optional[str] = Field(
        default=None,
        description="Architectural composition guidance for assembling atomic components when recipe is None"
    )
    suggested_test_file: str = Field(
        default="src/tests/page.spec.ts",
        description="Path to the companion Playwright E2E test file (e.g. src/tests/disbursements.spec.ts)"
    )
    purpose: str = Field(description="Business purpose of this page")


class RequirementBlueprint(BaseModel):
    summary: str = Field(description="Executive summary of the feature or application")
    target_theme: str = Field(description="Selected design theme (wbg-enterprise, enterprise-dark, client-warm-sage, etc.)")
    input_modality: Literal["text_prd", "visual_mockup", "hybrid"] = Field(
        default="text_prd",
        description="Input format: text_prd, visual_mockup (screenshot/Figma), or hybrid"
    )
    active_mode: str = Field(
        default="standalone",
        description="Active operational mode: 'standalone' (non-enterprise / offline), 'wbg' (local enterprise), 'cloud', or 'carbon'"
    )
    application_archetype: str = Field(
        default="Enterprise Portal",
        description="Classified archetype: e.g. 'Entity Management Portal', 'Bespoke Workspace', 'Analytical Dashboard'"
    )
    recommended_routes: List[PlannedRoute] = Field(description="Architectural route breakdown")
    design_rules_summary: List[str] = Field(description="Core constraints from DESIGN.md")
