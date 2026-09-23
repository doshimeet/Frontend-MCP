"""
Brownfield Integration & Conflict Prevention Service
Safely inspects existing projects and avoids destructive file overwrites.
"""

from pathlib import Path
from typing import Union
from core.router_detector import detect_project_router
from services.security_service import SecurityService, SecurityException
from models.scaffolding import ConflictReport, IntegrationPlan


class BrownfieldService:
    """Manages integration into existing projects with conflict detection."""

    def __init__(self, security_service: SecurityService = None):
        self.security_service = security_service or SecurityService()

    def inspect_and_plan(self, project_path_str: str, page_route: str) -> Union[ConflictReport, IntegrationPlan]:
        """
        Validates target project, detects router type, and checks if target file already exists.
        Returns ConflictReport if file exists, or IntegrationPlan if clear to create.
        """
        target_root = self.security_service.sanitize_and_validate_path(project_path_str)

        if not target_root.exists() or not (target_root / "package.json").exists():
            raise FileNotFoundError(f"Path '{target_root}' does not appear to be an active project (missing package.json).")

        router_info = detect_project_router(target_root)
        clean_route = page_route.strip("/").replace(" ", "-").lower()

        # Determine target file path based on detected router convention
        if router_info["router_type"] == "nextjs_app_router":
            target_file = target_root / router_info["pages_dir"] / clean_route / "page.tsx"
        elif router_info["router_type"] == "nextjs_pages_router":
            target_file = target_root / router_info["pages_dir"] / f"{clean_route}.tsx"
        else:
            target_file = target_root / "src" / "pages" / f"{clean_route.capitalize()}.tsx"

        # Conflict Detection: Check if file already exists
        if target_file.exists():
            return ConflictReport(
                conflict_detected=True,
                target_file=str(target_file),
                router_type=router_info["router_type"],
                warning_message=(
                    f"CRITICAL SAFETY WARNING: File '{target_file}' already exists! "
                    "DO NOT silently overwrite this file. "
                    "Ask the user in chat: "
                    "(1) Overwrite existing file, "
                    f"(2) Create parallel file '{clean_route}-new.tsx', or "
                    "(3) Cancel operation."
                ),
            )

        requires_use_client = router_info["requires_use_client"] == "true"
        use_client_note = 'Include "use client"; at top of file for App Router interactive components.' if requires_use_client else ""

        return IntegrationPlan(
            safe_to_generate=True,
            target_file=str(target_file),
            relative_path=str(target_file.relative_to(target_root)),
            framework=router_info["framework"],
            router_type=router_info["router_type"],
            requires_use_client=requires_use_client,
            instructions=f"File '{target_file.relative_to(target_root)}' is clear for creation. {use_client_note}".strip(),
        )
