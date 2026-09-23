"""
Pydantic Schemas for Design Tokens & Theming
Conforms to W3C Design Tokens Community Group (DTCG) specification.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class TokenItem(BaseModel):
    value: str = Field(description="The CSS variable or raw value of the token")
    type: Optional[str] = Field(default=None, description="Token type: color, spacing, typography, radius")
    description: Optional[str] = Field(default=None, description="Human-readable guideline on token usage")


class ThemeTokens(BaseModel):
    theme_name: str = Field(default="default", description="Name of the theme palette")
    color: Dict[str, TokenItem] = Field(default_factory=dict, description="Color tokens")
    spacing: Dict[str, TokenItem] = Field(default_factory=dict, description="Spacing tokens")
    typography: Dict[str, TokenItem] = Field(default_factory=dict, description="Typography scale tokens")
    radius: Dict[str, TokenItem] = Field(default_factory=dict, description="Border radius tokens")


class TokenCategoryResponse(BaseModel):
    category: str = Field(description="Category requested (color, spacing, etc.)")
    theme: str = Field(description="Theme applied")
    tokens: Dict[str, TokenItem] = Field(description="Tokens dictionary in requested category")
