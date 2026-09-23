"""
Enterprise Design System MCP - Resources Package
Passive contextual data streams (design tokens and layout recipes).
"""

from resources.tokens_resource import register_tokens_resources
from resources.recipes_resource import register_recipes_resources

__all__ = [
    "register_tokens_resources",
    "register_recipes_resources",
]
