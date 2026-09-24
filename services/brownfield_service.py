"""
Brownfield Integration & Conflict Prevention Service
Safely inspects existing projects, injects Nexus design tokens, micro-primitives,
and anti-slop design taste skills without destructive overwrites.
"""

import json
import shutil
from pathlib import Path
from typing import Union, Dict, Any, List, Optional
from core.router_detector import detect_project_router
from services.security_service import SecurityService, SecurityException
from models.scaffolding import ConflictReport, IntegrationPlan
from config import REPO_ROOT, TOKENS_DIR


class BrownfieldService:
    """Manages integration into existing projects with conflict detection and token/skill injection."""

    def __init__(self, security_service: SecurityService = None):
        self.security_service = security_service or SecurityService()

    def inspect_and_plan(
        self,
        project_path_str: str,
        page_route: str,
        inject_design_system: bool = False,
    ) -> Union[ConflictReport, IntegrationPlan]:
        """
        Validates target project, detects router type, and checks if target file already exists.
        Returns ConflictReport if file exists, or IntegrationPlan if clear to create.
        Optionally bootstraps design tokens and micro-primitives if requested.
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

        injected_artifacts: List[str] = []
        if inject_design_system:
            injection_res = self.inject_design_system(str(target_root))
            injected_artifacts = injection_res.get("created_files", [])

        requires_use_client = router_info["requires_use_client"] == "true"
        use_client_note = 'Include "use client"; at top of file for App Router interactive components.' if requires_use_client else ""

        return IntegrationPlan(
            safe_to_generate=True,
            target_file=str(target_file),
            relative_path=str(target_file.relative_to(target_root)),
            framework=router_info["framework"],
            router_type=router_info["router_type"],
            requires_use_client=requires_use_client,
            instructions=f"File '{target_file.relative_to(target_root)}' is clear for creation. {use_client_note} {('Injected: ' + ', '.join(injected_artifacts)) if injected_artifacts else ''}".strip(),
        )

    def inject_design_system(
        self,
        project_path_str: str,
        inject_tokens: bool = True,
        inject_primitives: bool = True,
        inject_skills: bool = True,
    ) -> Dict[str, Any]:
        """
        Non-destructively injects Nexus design tokens, micro-primitives, and
        enterprise anti-slop skills into an existing brownfield project.
        """
        target_root = self.security_service.sanitize_and_validate_path(project_path_str)
        pkg_file = target_root / "package.json"
        if not pkg_file.exists():
            raise FileNotFoundError(f"Missing package.json in target project: {target_root}")

        created_files: List[str] = []
        modified_files: List[str] = []

        # 1. Non-destructively inject Nexus tokens CSS
        if inject_tokens:
            source_css = REPO_ROOT / "packages" / "tokens" / "nexus-tokens.css"
            if source_css.exists():
                if (target_root / "src").exists():
                    styles_dir = target_root / "src" / "styles"
                else:
                    styles_dir = target_root / "styles"
                styles_dir.mkdir(parents=True, exist_ok=True)

                dest_css = styles_dir / "nexus-tokens.css"
                if not dest_css.exists():
                    shutil.copy2(source_css, dest_css)
                    created_files.append(str(dest_css.relative_to(target_root)))

        # 2. Inject Micro-Primitives into src/components/nexus/
        if inject_primitives:
            primitives_src = REPO_ROOT / "packages" / "primitives"
            if primitives_src.exists():
                dest_primitives_dir = target_root / "src" / "components" / "nexus"
                dest_primitives_dir.mkdir(parents=True, exist_ok=True)

                for item in primitives_src.glob("*.tsx"):
                    dest_file = dest_primitives_dir / item.name
                    if not dest_file.exists():
                        shutil.copy2(item, dest_file)
                        created_files.append(str(dest_file.relative_to(target_root)))

                dest_index = dest_primitives_dir / "index.ts"
                src_index = primitives_src / "index.ts"
                if src_index.exists() and not dest_index.exists():
                    shutil.copy2(src_index, dest_index)
                    created_files.append(str(dest_index.relative_to(target_root)))

        # 3. Inject Enterprise Design Skills into .agents/skills/
        if inject_skills:
            skills_src = REPO_ROOT / ".agents" / "skills"
            if skills_src.exists():
                dest_skills_dir = target_root / ".agents" / "skills"
                dest_skills_dir.mkdir(parents=True, exist_ok=True)

                for skill_name in ["design-taste-frontend", "impeccable"]:
                    src_skill_dir = skills_src / skill_name
                    dest_skill_dir = dest_skills_dir / skill_name
                    if src_skill_dir.exists() and not dest_skill_dir.exists():
                        shutil.copytree(src_skill_dir, dest_skill_dir)
                        created_files.append(f".agents/skills/{skill_name}/")

                bridge_rules = skills_src / "wbg-enterprise-rules.md"
                dest_rules = dest_skills_dir / "wbg-enterprise-rules.md"
                if bridge_rules.exists() and not dest_rules.exists():
                    shutil.copy2(bridge_rules, dest_rules)
                    created_files.append(".agents/skills/wbg-enterprise-rules.md")

        # 4. Non-destructively inject .github/copilot-instructions.md if absent
        copilot_src = REPO_ROOT / ".github" / "copilot-instructions.md"
        if copilot_src.exists():
            github_dir = target_root / ".github"
            dest_copilot = github_dir / "copilot-instructions.md"
            if not dest_copilot.exists():
                github_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(copilot_src, dest_copilot)
                created_files.append(".github/copilot-instructions.md")

        # 5. Safely inspect package.json to ensure dependencies without overwriting existing
        try:
            with open(pkg_file, "r", encoding="utf-8") as f:
                pkg_data = json.load(f)

            deps = pkg_data.get("dependencies", {})
            modified_pkg = False

            if "@wbg/nexus" not in deps:
                # Add non-destructively
                deps["@wbg/nexus"] = "^2.0.0"
                pkg_data["dependencies"] = deps
                modified_pkg = True

            if modified_pkg:
                with open(pkg_file, "w", encoding="utf-8") as f:
                    json.dump(pkg_data, f, indent=2)
                modified_files.append("package.json")
        except Exception:
            pass

        return {
            "status": "success",
            "project_path": str(target_root),
            "created_files": created_files,
            "modified_files": modified_files,
            "summary": f"Injected {len(created_files)} design assets and skills into {target_root.name}.",
        }
