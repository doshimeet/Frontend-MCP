"""
Pydantic Schemas for Scaffolding & Brownfield Conflict Management
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ScaffoldResult(BaseModel):
    success: bool = Field(description="Whether the scaffolding succeeded")
    app_name: str = Field(description="Name of the scaffolded application")
    target_directory: str = Field(description="Absolute path to created application")
    source: str = Field(description="Source of template (azure_devops or local_starter_template)")
    next_steps: List[str] = Field(description="Actionable commands to run after scaffolding")
    error_message: Optional[str] = Field(default=None, description="Error explanation if failed")


class ConflictReport(BaseModel):
    conflict_detected: bool = Field(description="Whether the destination file already exists")
    target_file: str = Field(description="Target file path")
    router_type: str = Field(description="Detected Next.js router convention (app_router or pages_router)")
    warning_message: str = Field(description="Instruction for the AI to ask the user in chat before overwriting")


class IntegrationPlan(BaseModel):
    safe_to_generate: bool = Field(description="Whether it is safe to create the page file")
    target_file: str = Field(description="Absolute destination file path")
    relative_path: str = Field(description="Path relative to project root")
    framework: str = Field(description="Detected frontend framework (nextjs or vite)")
    router_type: str = Field(description="nextjs_app_router or nextjs_pages_router")
    requires_use_client: bool = Field(description="Whether 'use client' directive is required")
    instructions: str = Field(description="Step-by-step guidance for code generation")
