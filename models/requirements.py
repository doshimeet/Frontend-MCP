"""
Pydantic Schemas for Requirements & PRD Blueprints
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PlannedRoute(BaseModel):
    path: str = Field(description="URL path (e.g. '/' or '/invoices')")
    title: str = Field(description="Page or feature title")
    recipe: str = Field(description="Recommended page recipe template (e.g. CrudTableRecipe)")
    components: List[str] = Field(description="Key design system components needed")
    purpose: str = Field(description="Business purpose of this page")


class RequirementBlueprint(BaseModel):
    summary: str = Field(description="Executive summary of the feature or application")
    target_theme: str = Field(description="Selected design theme (enterprise-dark, client-warm-sage, etc.)")
    recommended_routes: List[PlannedRoute] = Field(description="Architectural route breakdown")
    design_rules_summary: List[str] = Field(description="Core constraints from DESIGN.md")
