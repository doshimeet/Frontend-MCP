"""
Pydantic Schemas for Component Specifications & Storybook Catalog
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class PropDefinition(BaseModel):
    type: str = Field(description="TypeScript type definition (e.g. 'primary' | 'secondary')")
    required: bool = Field(default=False, description="Whether the prop is required")
    default: Optional[str] = Field(default=None, description="Default value if not provided")
    description: Optional[str] = Field(default=None, description="Guidance on when to use this prop")


class ComponentSpec(BaseModel):
    name: str = Field(description="Component name (e.g. Button, DataTable, Modal)")
    import_statement: str = Field(description="Canonical import statement to copy into code")
    description: str = Field(description="Detailed usage guideline and purpose")
    props: Dict[str, PropDefinition] = Field(default_factory=dict, description="Component prop interfaces")
    example: str = Field(description="Production-tested TSX code example")


class ComponentCatalogSummary(BaseModel):
    source: str = Field(description="Source of components (carbon or enterprise)")
    total_components: int = Field(description="Total components available")
    components: Dict[str, str] = Field(description="Map of component names to brief descriptions")
