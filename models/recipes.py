"""
Pydantic Schemas for Canonical Page Recipes & Companion Playwright Specs
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PageRecipeResponse(BaseModel):
    name: str = Field(description="Canonical recipe name (e.g. CrudTableRecipe)")
    title: str = Field(description="Human-readable recipe title")
    description: str = Field(description="Detailed layout and pattern description")
    component_code: str = Field(description="Complete, ready-to-use TypeScript React component code (.tsx)")
    test_spec_code: str = Field(description="Companion Playwright end-to-end test specification (.spec.ts)")
    target_mode: str = Field(default="wbg", description="Design system target mode: 'carbon' or 'wbg'")
    required_components: List[str] = Field(default_factory=list, description="List of design system components used")
    states_handled: List[str] = Field(default_factory=list, description="Resilient states handled (loading, empty, error, etc.)")
    a11y_compliance: str = Field(description="WCAG compliance and accessibility features")
