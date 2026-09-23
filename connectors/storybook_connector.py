"""
Dynamic Storybook & Component Catalog Harvester
Fetches live component definitions from Storybook (index.json / stories.json)
or local manifests, with offline disk caching and resilient fallback.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

from config import CARBON_STORYBOOK_URL, REPO_ROOT

# Rich baseline catalog for offline resilience
OFFLINE_CARBON_CATALOG: Dict[str, Dict[str, Any]] = {
    "Button": {
        "import_statement": "import { Button } from '@carbon/react';",
        "description": "Buttons initialize actions. Labels express what action will occur with primary, secondary, tertiary, and danger styles.",
        "props": {
            "kind": {"type": "'primary' | 'secondary' | 'tertiary' | 'ghost' | 'danger'", "default": "'primary'"},
            "size": {"type": "'sm' | 'md' | 'lg' | 'xl' | '2xl'", "default": "'md'"},
            "disabled": {"type": "boolean", "default": "false"},
        },
        "example": '<Button kind="primary" size="md">Submit Application</Button>',
    },
    "DataTable": {
        "import_statement": "import { DataTable, Table, TableHead, TableRow, TableHeader, TableBody, TableCell, TableContainer } from '@carbon/react';",
        "description": "DataTable presents structured data sets with sorting, filtering, row selection, and pagination.",
        "props": {
            "rows": {"type": "Array<{ id: string, [key: string]: any }>", "required": "true"},
            "headers": {"type": "Array<{ key: string, header: string }>", "required": "true"},
            "isSortable": {"type": "boolean", "default": "true"},
            "size": {"type": "'xs' | 'sm' | 'md' | 'lg' | 'xl'", "default": "'lg'"},
        },
        "example": "<DataTable rows={rows} headers={headers}>...</DataTable>",
    },
    "Modal": {
        "import_statement": "import { Modal } from '@carbon/react';",
        "description": "Modals focus the user's attention exclusively on one task or critical decision.",
        "props": {
            "open": {"type": "boolean", "required": "true"},
            "modalHeading": {"type": "string", "required": "true"},
            "primaryButtonText": {"type": "string", "required": "true"},
            "secondaryButtonText": {"type": "string", "default": "'Cancel'"},
            "danger": {"type": "boolean", "default": "false"},
        },
        "example": '<Modal open={isOpen} modalHeading="Confirm Action" primaryButtonText="Confirm" />',
    },
    "TextInput": {
        "import_statement": "import { TextInput } from '@carbon/react';",
        "description": "Text inputs enable users to enter text, numbers, or symbols with built-in validation states.",
        "props": {
            "id": {"type": "string", "required": "true"},
            "labelText": {"type": "string", "required": "true"},
            "placeholder": {"type": "string"},
            "invalid": {"type": "boolean", "default": "false"},
            "invalidText": {"type": "string"},
        },
        "example": '<TextInput id="username" labelText="User Name" placeholder="Enter username" />',
    },
    "Select": {
        "import_statement": "import { Select, SelectItem } from '@carbon/react';",
        "description": "Select allows users to choose one option from a predefined list of options.",
        "props": {
            "id": {"type": "string", "required": "true"},
            "labelText": {"type": "string", "required": "true"},
            "defaultValue": {"type": "string"},
            "invalid": {"type": "boolean", "default": "false"},
        },
        "example": '<Select id="role" labelText="Role"><SelectItem value="admin" text="Admin" /></Select>',
    },
    "Tag": {
        "import_statement": "import { Tag } from '@carbon/react';",
        "description": "Tags categorize content using keywords and status colors.",
        "props": {
            "type": {"type": "'red' | 'magenta' | 'purple' | 'blue' | 'cyan' | 'teal' | 'green' | 'gray'"},
            "size": {"type": "'sm' | 'md'", "default": "'md'"},
        },
        "example": '<Tag type="green">Active</Tag>',
    },
    "Tile": {
        "import_statement": "import { Tile, ClickableTile, ExpandableTile } from '@carbon/react';",
        "description": "Tiles group related information and actions into bounded, distinct visual blocks.",
        "props": {
            "light": {"type": "boolean", "default": "false"},
        },
        "example": "<Tile><h4>System Metric</h4><p>Value</p></Tile>",
    },
    "SkeletonText": {
        "import_statement": "import { SkeletonText } from '@carbon/react';",
        "description": "Skeleton text visually placeholders loading typography to prevent layout shifts.",
        "props": {
            "heading": {"type": "boolean", "default": "false"},
            "paragraph": {"type": "boolean", "default": "false"},
            "lineCount": {"type": "number", "default": "3"},
        },
        "example": "<SkeletonText paragraph lineCount={3} />",
    },
    "Pagination": {
        "import_statement": "import { Pagination } from '@carbon/react';",
        "description": "Pagination splits large sets of data into discrete page views.",
        "props": {
            "totalItems": {"type": "number", "required": "true"},
            "page": {"type": "number", "default": "1"},
            "pageSize": {"type": "number", "default": "10"},
            "pageSizes": {"type": "number[]", "default": "[10, 25, 50, 100]"},
        },
        "example": "<Pagination totalItems={100} page={1} pageSize={10} pageSizes={[10, 25, 50]} />",
    },
    "Header": {
        "import_statement": "import { Header, HeaderName, HeaderNavigation, HeaderMenuItem, HeaderGlobalBar, HeaderGlobalAction } from '@carbon/react';",
        "description": "Top-level enterprise application navigation shell with brand branding, links, and global actions.",
        "props": {
            "aria-label": {"type": "string", "required": "true"},
        },
        "example": '<Header aria-label="Portal"><HeaderName prefix="WBG">Operations</HeaderName></Header>',
    },
}


class StorybookConnector:
    """Connects to Storybook index or local manifest to fetch live component schemas."""

    def __init__(self, endpoint_url: Optional[str] = None, cache_dir: Optional[Path] = None):
        self.endpoint_url = endpoint_url or os.getenv("STORYBOOK_URL", CARBON_STORYBOOK_URL)
        self.cache_dir = cache_dir or (REPO_ROOT / ".cache")
        self.cache_file = self.cache_dir / "storybook_catalog.json"
        self._memory_cache: Optional[Dict[str, Dict[str, Any]]] = None

    def _ensure_cache_dir(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _load_disk_cache(self) -> Optional[Dict[str, Dict[str, Any]]]:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def _save_disk_cache(self, catalog: Dict[str, Dict[str, Any]]) -> None:
        try:
            self._ensure_cache_dir()
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(catalog, f, indent=2)
        except Exception:
            pass

    def harvest_catalog(self) -> Dict[str, Dict[str, Any]]:
        """
        Dynamically harvests component definitions.
        Order of priority:
        1. Memory cache (if warm)
        2. Live Storybook index (index.json / stories.json)
        3. Local disk cache (.cache/storybook_catalog.json)
        4. Curated OFFLINE_CARBON_CATALOG
        """
        if self._memory_cache is not None:
            return self._memory_cache

        # Check local disk cache first for fast offline bootstrap
        disk_data = self._load_disk_cache()
        if disk_data:
            self._memory_cache = {**OFFLINE_CARBON_CATALOG, **disk_data}
            return self._memory_cache

        # Attempt to harvest from remote / local Storybook URL if configured
        if self.endpoint_url and self.endpoint_url.startswith("http"):
            try:
                index_url = self.endpoint_url.rstrip("/") + "/index.json"
                with httpx.Client(timeout=3.0) as client:
                    resp = client.get(index_url)
                    if resp.status_code == 200:
                        stories_data = resp.json()
                        harvested = self._parse_storybook_index(stories_data)
                        combined = {**OFFLINE_CARBON_CATALOG, **harvested}
                        self._save_disk_cache(combined)
                        self._memory_cache = combined
                        return self._memory_cache
            except Exception:
                # Network down, fallback gracefully
                pass

        # Check for local static storybook-static/index.json
        local_index = REPO_ROOT / "storybook-static" / "index.json"
        if local_index.exists():
            try:
                with open(local_index, "r", encoding="utf-8") as f:
                    stories_data = json.load(f)
                    harvested = self._parse_storybook_index(stories_data)
                    combined = {**OFFLINE_CARBON_CATALOG, **harvested}
                    self._save_disk_cache(combined)
                    self._memory_cache = combined
                    return self._memory_cache
            except Exception:
                pass

        # Final resilient baseline
        self._memory_cache = OFFLINE_CARBON_CATALOG
        return self._memory_cache

    def _parse_storybook_index(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Parses Storybook v7+ index.json into structured component specifications."""
        result: Dict[str, Dict[str, Any]] = {}
        entries = data.get("entries", {}) or data.get("stories", {})
        for key, entry in entries.items():
            comp_name = entry.get("title", "").split("/")[-1] or entry.get("name", "")
            if not comp_name or comp_name in result:
                continue
            package_name = os.getenv("DESIGN_SYSTEM_PACKAGE", "@carbon/react")
            result[comp_name] = {
                "import_statement": f"import {{ {comp_name} }} from '{package_name}';",
                "description": f"Enterprise design system {comp_name} component from {entry.get('title', 'catalog')}.",
                "props": {},
                "example": f"<{comp_name} />",
            }
        return result

    def get_catalog_summary(self, source: str = "carbon") -> Dict[str, str]:
        """Returns map of component names to brief descriptions."""
        catalog = self.harvest_catalog()
        return {name: data.get("description", "") for name, data in catalog.items()}

    def get_component_spec(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Returns detailed spec for a given component."""
        catalog = self.harvest_catalog()
        return catalog.get(component_name)
