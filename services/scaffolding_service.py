"""
Greenfield Scaffolding Service
Integrates security sandboxing with Azure DevOps repository downloads.
"""

import json
import shutil
import subprocess
from pathlib import Path
from connectors.ado_connector import AzureDevOpsConnector
from services.security_service import SecurityService, SecurityException
from models.scaffolding import ScaffoldResult


class ScaffoldingService:
    """Manages greenfield application scaffolding with security validation."""

    def __init__(self, ado_connector: AzureDevOpsConnector = None, security_service: SecurityService = None):
        self.ado_connector = ado_connector or AzureDevOpsConnector()
        self.security_service = security_service or SecurityService()

    def scaffold(self, app_name: str, target_directory_str: str) -> ScaffoldResult:
        """
        Scaffolds a clean Next.js project into target_directory.
        Validates path sandboxing, downloads starter kit, updates package.json, and inits Git.
        """
        try:
            target_path = self.security_service.sanitize_and_validate_path(target_directory_str)
        except SecurityException as sec_err:
            return ScaffoldResult(
                success=False,
                app_name=app_name,
                target_directory=target_directory_str,
                source="security_blocked",
                next_steps=[],
                error_message=str(sec_err),
            )

        # Do not overwrite an existing non-empty directory
        if target_path.exists() and any(target_path.iterdir()):
            return ScaffoldResult(
                success=False,
                app_name=app_name,
                target_directory=str(target_path),
                source="validation_error",
                next_steps=[],
                error_message=(
                    f"Target directory '{target_path}' already exists and is not empty. "
                    "Please specify an empty directory or choose a new folder name."
                ),
            )

        # Download starter kit archive
        download_res = self.ado_connector.download_starter_archive(target_path)
        if not download_res.get("success"):
            return ScaffoldResult(
                success=False,
                app_name=app_name,
                target_directory=str(target_path),
                source=download_res.get("source", "unknown"),
                next_steps=[],
                error_message=download_res.get("message", "Failed to download starter kit."),
            )

        # Update package.json name
        pkg_file = target_path / "package.json"
        if pkg_file.exists():
            try:
                with open(pkg_file, "r", encoding="utf-8") as f:
                    pkg_data = json.load(f)
                pkg_data["name"] = app_name
                with open(pkg_file, "w", encoding="utf-8") as f:
                    json.dump(pkg_data, f, indent=2)
            except Exception:
                pass

        # Guarantee zero .npmrc file compliance (adheres to enterprise credential policy)
        npmrc_file = target_path / ".npmrc"
        if npmrc_file.exists():
            try:
                npmrc_file.unlink()
            except Exception:
                pass

        # Re-initialize clean Git repository
        git_dir = target_path / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir, ignore_errors=True)

        git_bin = shutil.which("git")
        if git_bin:
            try:
                subprocess.run([git_bin, "init"], cwd=target_path, check=True, capture_output=True)
            except Exception:
                pass

        return ScaffoldResult(
            success=True,
            app_name=app_name,
            target_directory=str(target_path),
            source=download_res.get("source", "template"),
            next_steps=[
                f"1. Navigate to target folder: cd '{target_path}'",
                "2. Install dependencies: npm install",
                "3. Start dev server: npm run dev",
                "4. Implement features using get_page_recipe() and design system components",
            ],
            error_message=None,
        )
