"""
Composable Pattern Anatomies & Micro-Primitive Models
Defines structural layout slots, primitive requirements, and anti-slop rules
to ensure enterprise UI components compose gracefully rather than as rigid monoliths.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PatternSlot(BaseModel):
    """Defines a customizable slot in an enterprise page pattern anatomy."""
    slot_id: str = Field(description="Unique identifier for the slot (e.g., 'header_slot', 'kpi_grid_slot')")
    name: str = Field(description="Display name for the slot")
    description: str = Field(description="Functional purpose of the slot")
    recommended_primitives: List[str] = Field(
        default_factory=list,
        description="Recommended micro-primitives for this slot (e.g., 'StatCard', 'FilterToolbar')"
    )
    is_required: bool = Field(default=True, description="Whether this slot is required for the pattern to be valid")
    anti_slop_guideline: Optional[str] = Field(
        default=None,
        description="Specific aesthetic and hierarchy rules for content in this slot"
    )


class PatternAnatomy(BaseModel):
    """Architectural anatomy defining how an enterprise page is composed."""
    pattern_id: str = Field(description="Identifier for the pattern (e.g., 'operations_dashboard', 'portfolio_browser')")
    title: str = Field(description="Human-readable title")
    description: str = Field(description="Architecture and operational goal of the layout")
    category: str = Field(default="dashboard", description="Pattern category: dashboard, data_browser, workflow, audit")
    slots: List[PatternSlot] = Field(default_factory=list, description="Ordered composition slots")
    applied_elevation_classes: List[str] = Field(
        default_factory=lambda: [".nexus-card", ".nexus-kpi-card", ".nexus-toolbar"],
        description="Predefined CSS utility classes handling depth and surface layering"
    )
    anti_slop_rules: List[str] = Field(
        default_factory=lambda: [
            "Exactly one <h1> per screen",
            "No raw inline styles (style={{ ... }})",
            "Status badges reserved strictly for operational states, not raw metrics",
            "Tabular figures enabled for numeric/monetary columns",
            "Minimum contrast ratio 4.5:1 against canvas"
        ],
        description="Explicit anti-slop constraints enforced by the verification engine"
    )
