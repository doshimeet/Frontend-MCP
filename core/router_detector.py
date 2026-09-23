"""
Frontend Router & Framework Detector
Detects Next.js App Router vs. Pages Router vs. Vite SPA.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

RouterType = Literal["nextjs_app_router", "nextjs_pages_router", "vite_spa", "unknown"]


def detect_project_router(project_path: Path) -> dict[str, str]:
    """
    Analyzes project directory structure and package.json to determine
    the routing architecture and page creation conventions.
    """
    result = {
        "framework": "unknown",
        "router_type": "unknown",
        "pages_dir": "src/app",
        "file_convention": "page.tsx",
        "requires_use_client": "true",
    }

    if not project_path.exists():
        return result

    # Check package.json dependencies
    pkg_file = project_path / "package.json"
    has_next = False
    has_vite = False

    if pkg_file.exists():
        try:
            with open(pkg_file, "r", encoding="utf-8") as f:
                pkg_data = json.load(f)
                deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                has_next = "next" in deps
                has_vite = "vite" in deps
        except Exception:
            pass

    # Next.js App Router check (app/ or src/app/)
    has_src_app = (project_path / "src" / "app").is_dir()
    has_root_app = (project_path / "app").is_dir()

    # Next.js Pages Router check (pages/ or src/pages/)
    has_src_pages = (project_path / "src" / "pages").is_dir()
    has_root_pages = (project_path / "pages").is_dir()

    if has_src_app or has_root_app or (has_next and not (has_src_pages or has_root_pages)):
        result["framework"] = "nextjs"
        result["router_type"] = "nextjs_app_router"
        result["pages_dir"] = "src/app" if has_src_app else "app"
        result["file_convention"] = "page.tsx"
        result["requires_use_client"] = "true"
        return result

    if has_src_pages or has_root_pages:
        result["framework"] = "nextjs"
        result["router_type"] = "nextjs_pages_router"
        result["pages_dir"] = "src/pages" if has_src_pages else "pages"
        result["file_convention"] = "[route].tsx"
        result["requires_use_client"] = "false"
        return result

    if has_vite or (project_path / "vite.config.ts").exists() or (project_path / "vite.config.js").exists():
        result["framework"] = "vite"
        result["router_type"] = "vite_spa"
        result["pages_dir"] = "src/routes"
        result["file_convention"] = "[Route].tsx"
        result["requires_use_client"] = "false"
        return result

    return result
