"""
Enterprise Design System MCP - Prompts Package
Pre-engineered prompt templates for guided agent workflows.
"""

from prompts.plan_prd_prompt import register_plan_prd_prompt
from prompts.critique_ui_prompt import register_critique_ui_prompt

__all__ = [
    "register_plan_prd_prompt",
    "register_critique_ui_prompt",
]
