"""
Design Token Service
Manages DTCG tokens loading, theme cascading, and category slicing.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from config import TOKENS_DIR
from models.tokens import TokenItem, ThemeTokens, TokenCategoryResponse

# Default Embedded Tokens (Nexus Design System v2.0.0)
DEFAULT_RAW_TOKENS: Dict[str, Dict[str, Dict[str, str]]] = {
    "color": {
        "primary": {"value": "#002244", "type": "color", "description": "Nexus Design System Deep Navy"},
        "primary_hover": {"value": "#00172e", "type": "color"},
        "secondary": {"value": "#0071bc", "type": "color", "description": "Nexus Accent Blue"},
        "secondary_hover": {"value": "#005a96", "type": "color"},
        "danger": {"value": "#da1e28", "type": "color"},
        "success": {"value": "#24a148", "type": "color"},
        "warning": {"value": "#f1c21b", "type": "color"},
        "background": {"value": "#ffffff", "type": "color"},
        "surface": {"value": "#f4f6f8", "type": "color"},
        "text_primary": {"value": "#222222", "type": "color"},
        "text_secondary": {"value": "#555555", "type": "color"},
        "border_subtle": {"value": "#d0d7de", "type": "color"},
    },
    "spacing": {
        "xs": {"value": "0.25rem", "type": "spacing"},
        "sm": {"value": "0.5rem", "type": "spacing"},
        "md": {"value": "1rem", "type": "spacing"},
        "lg": {"value": "1.5rem", "type": "spacing"},
        "xl": {"value": "2rem", "type": "spacing"},
        "2xl": {"value": "3rem", "type": "spacing"},
    },
    "typography": {
        "font_family_sans": {"value": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"},
        "font_family_mono": {"value": "'JetBrains Mono', 'Menlo', 'DejaVu Sans Mono', monospace"},
        "font_size_sm": {"value": "0.875rem"},
        "font_size_base": {"value": "1rem"},
        "font_size_lg": {"value": "1.25rem"},
        "font_size_xl": {"value": "1.5rem"},
        "font_size_2xl": {"value": "2rem"},
    },
    "radius": {
        "none": {"value": "0px"},
        "sm": {"value": "2px"},
        "md": {"value": "6px"},
        "lg": {"value": "8px"},
    }
}


class TokenService:
    """Manages DTCG design tokens and multi-tenant theme overrides."""

    def __init__(self, tokens_dir: Path = TOKENS_DIR):
        self.tokens_dir = tokens_dir

    def get_theme_tokens(self, theme: str = "default") -> ThemeTokens:
        """Loads and parses tokens for a given theme."""
        token_file = self.tokens_dir / "tokens.json"
        if theme not in ("default", "all"):
            custom_theme_file = self.tokens_dir / "themes" / f"{theme}.json"
            if custom_theme_file.exists():
                token_file = custom_theme_file

        raw_data = DEFAULT_RAW_TOKENS
        if token_file.exists():
            try:
                with open(token_file, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
            except Exception:
                pass

        # Parse into Pydantic models (supporting both DTCG $value/$type and value/type)
        def parse_category(cat: str) -> Dict[str, TokenItem]:
            cat_dict = raw_data.get(cat, {})
            return {
                k: TokenItem(
                    value=v.get("$value", v.get("value", "")) if isinstance(v, dict) else str(v),
                    type=v.get("$type", v.get("type", cat)) if isinstance(v, dict) else cat,
                    description=v.get("$description", v.get("description")) if isinstance(v, dict) else None,
                )
                for k, v in cat_dict.items()
                if not k.startswith("$")
            }

        return ThemeTokens(
            theme_name=theme,
            color=parse_category("color"),
            spacing=parse_category("spacing"),
            typography=parse_category("typography"),
            radius=parse_category("radius"),
        )

    def get_category_tokens(self, category: str = "all", theme: str = "default") -> TokenCategoryResponse:
        """Returns tokens filtered by category."""
        theme_tokens = self.get_theme_tokens(theme)
        if category == "color":
            selected = theme_tokens.color
        elif category == "spacing":
            selected = theme_tokens.spacing
        elif category == "typography":
            selected = theme_tokens.typography
        elif category == "radius":
            selected = theme_tokens.radius
        else:
            selected = {
                **theme_tokens.color,
                **theme_tokens.spacing,
                **theme_tokens.typography,
                **theme_tokens.radius,
            }

        return TokenCategoryResponse(category=category, theme=theme, tokens=selected)
