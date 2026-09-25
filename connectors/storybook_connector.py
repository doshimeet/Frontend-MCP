"""
Dynamic Storybook & Component Catalog Harvester
Fetches live component definitions from Storybook (index.json / stories.json)
or local manifests, with offline disk caching and resilient fallback.
Strictly configured for official @wbg/nexus design system.
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

from config import REPO_ROOT

logger = logging.getLogger("nexus-mcp.catalog")

# Rich baseline catalog for offline resilience (Official @wbg/nexus components)
OFFLINE_NEXUS_CATALOG: Dict[str, Dict[str, Any]] = {
    "Button": {
        "import_statement": "import { Button } from '@wbg/nexus';",
        "description": "Primary interactive action component with institutional styling variants (default, secondary, destructive, outline, ghost, link).",
        "props": {
            "variant": {"type": "'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'", "default": "'default'"},
            "size": {"type": "'default' | 'sm' | 'lg' | 'icon'", "default": "'default'"},
            "disabled": {"type": "boolean", "default": "false"},
        },
        "example": '<Button variant="default" size="default">Submit Application</Button>',
    },
    "Table": {
        "import_statement": "import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from '@wbg/nexus';",
        "description": "High-density institutional data table supporting sorting, filtering, row selection, and responsive layouts.",
        "props": {
            "className": {"type": "string", "default": "''"},
        },
        "example": "<Table><TableHeader><TableRow><TableHead>ID</TableHead></TableRow></TableHeader><TableBody><TableRow><TableCell>WBG-001</TableCell></TableRow></TableBody></Table>",
    },
    "DataTable": {
        "import_statement": "import { Table as DataTable, TableHeader, TableBody, TableHead, TableRow, TableCell } from '@wbg/nexus';",
        "description": "Enterprise data table layout with sorting and filtering capabilities.",
        "props": {
            "className": {"type": "string", "default": "''"},
        },
        "example": "<DataTable><TableHeader><TableRow><TableHead>ID</TableHead></TableRow></TableHeader><TableBody><TableRow><TableCell>WBG-001</TableCell></TableRow></TableBody></DataTable>",
    },
    "Card": {
        "import_statement": "import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@wbg/nexus';",
        "description": "Container card for grouping related information, metrics, and actions into distinct visual blocks.",
        "props": {
            "className": {"type": "string", "default": "''"},
        },
        "example": '<Card><CardHeader><CardTitle>Portfolio Health</CardTitle></CardHeader><CardContent><p>Active</p></CardContent></Card>',
    },
    "Dialog": {
        "import_statement": "import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@wbg/nexus';",
        "description": "Modal overlay dialog for focused workflows, sign-offs, and critical confirmations.",
        "props": {
            "open": {"type": "boolean"},
            "onOpenChange": {"type": "(open: boolean) => void"},
        },
        "example": '<Dialog open={isOpen} onOpenChange={setIsOpen}><DialogContent><DialogHeader><DialogTitle>Confirm Sign-off</DialogTitle></DialogHeader></DialogContent></Dialog>',
    },
    "Input": {
        "import_statement": "import { Input } from '@wbg/nexus';",
        "description": "Text input component with built-in focus-visible rings and validation states.",
        "props": {
            "type": {"type": "string", "default": "'text'"},
            "placeholder": {"type": "string"},
            "disabled": {"type": "boolean", "default": "false"},
        },
        "example": '<Input placeholder="Search project portfolio..." />',
    },
    "Tabs": {
        "import_statement": "import { Tabs, TabsList, TabsTrigger, TabsContent } from '@wbg/nexus';",
        "description": "Tabbed content container for organizing dense enterprise views into layered sections.",
        "props": {
            "defaultValue": {"type": "string"},
            "className": {"type": "string", "default": "''"},
        },
        "example": '<Tabs defaultValue="overview"><TabsList><TabsTrigger value="overview">Overview</TabsTrigger></TabsList><TabsContent value="overview">Content</TabsContent></Tabs>',
    },
    "Sheet": {
        "import_statement": "import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@wbg/nexus';",
        "description": "Side-drawer overlay panel for secondary inspect panes and detail drawers.",
        "props": {
            "open": {"type": "boolean"},
            "onOpenChange": {"type": "(open: boolean) => void"},
        },
        "example": '<Sheet open={isOpen} onOpenChange={setIsOpen}><SheetContent><SheetHeader><SheetTitle>Details</SheetTitle></SheetHeader></SheetContent></Sheet>',
    },
    "Select": {
        "import_statement": "import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@wbg/nexus';",
        "description": "Select allows users to choose one option from a predefined list of options.",
        "props": {
            "defaultValue": {"type": "string"},
            "disabled": {"type": "boolean", "default": "false"},
        },
        "example": '<Select><SelectTrigger><SelectValue placeholder="Select Sector" /></SelectTrigger><SelectContent><SelectItem value="energy">Energy</SelectItem></SelectContent></Select>',
    },
    "Badge": {
        "import_statement": "import { Badge } from '@wbg/nexus';",
        "description": "Status badge component for visual tagging and status indication.",
        "props": {
            "variant": {"type": "'default' | 'secondary' | 'destructive' | 'outline'", "default": "'default'"},
        },
        "example": '<Badge variant="outline">In Review</Badge>',
    },
    "Skeleton": {
        "import_statement": "import { Skeleton } from '@wbg/nexus';",
        "description": "Skeleton loading placeholder to prevent cumulative layout shift.",
        "props": {
            "className": {"type": "string", "default": "''"},
        },
        "example": '<Skeleton className="h-4 w-full" />',
    },
}


def normalize_component_name(raw_name: str) -> str:
    """
    Converts raw Storybook IDs or slugs into canonical PascalCase component names.
    Preserves existing PascalCase names (e.g. 'DataTable', 'Button', 'TextInput').
    Examples:
        'components-button' -> 'Button'
        'components-button--default' -> 'Button'
        'forms-text-input' -> 'TextInput'
        'DataTable' -> 'DataTable'
    """
    clean = raw_name.strip()
    # Strip story suffix e.g. '--default'
    if "--" in clean:
        clean = clean.split("--")[0]
    # If title has path e.g. 'Components/Button'
    if "/" in clean:
        clean = clean.split("/")[-1]
    
    # If already PascalCase without separators e.g. 'DataTable', 'Button', preserve exact casing
    if re.match(r"^[A-Z][a-zA-Z0-9]*$", clean) and not any(c in clean for c in "-_ "):
        return clean

    # If slug has prefix e.g. 'components-button'
    parts = re.split(r"[-_]+", clean)
    if len(parts) > 1 and parts[0].lower() in ("components", "patterns", "elements", "primitives", "forms"):
        parts = parts[1:]
    
    # Capitalize segments without destroying internal capitalization
    pascal = "".join(p[:1].upper() + p[1:] for p in parts if p)
    return pascal or raw_name


def normalize_component_spec(comp_name: str, raw_entry: Dict[str, Any], package_name: str = "@wbg/nexus") -> Dict[str, Any]:
    """
    Normalizes arbitrary raw entry (from Storybook, docgen, or components.json)
    into a guaranteed schema with import_statement, description, props, and example.
    Guarantees no KeyError when accessing fields.
    """
    import_stmt = (
        raw_entry.get("import_statement")
        or raw_entry.get("import")
        or f"import {{ {comp_name} }} from '{package_name}';"
    )
    desc = raw_entry.get("description") or f"Nexus design system {comp_name} component."
    example = raw_entry.get("example") or f"<{comp_name} />"

    raw_props = raw_entry.get("props", {})
    normalized_props: Dict[str, Dict[str, Any]] = {}
    if isinstance(raw_props, dict):
        for prop_name, prop_data in raw_props.items():
            if isinstance(prop_data, dict):
                # Handle docgen format where type is {"name": "string"}
                prop_type = prop_data.get("type")
                if isinstance(prop_type, dict):
                    prop_type_str = prop_type.get("name", "any")
                elif isinstance(prop_type, str):
                    prop_type_str = prop_type
                else:
                    prop_type_str = "any"

                default_val = prop_data.get("default") or prop_data.get("defaultValue")
                if isinstance(default_val, dict):
                    default_val_str = default_val.get("value")
                else:
                    default_val_str = str(default_val) if default_val is not None else None

                normalized_props[prop_name] = {
                    "type": prop_type_str,
                    "required": str(prop_data.get("required", False)).lower(),
                    "default": default_val_str,
                    "description": prop_data.get("description", ""),
                }
            elif isinstance(prop_data, str):
                normalized_props[prop_name] = {
                    "type": prop_data,
                    "required": "false",
                    "default": None,
                    "description": "",
                }

    return {
        "import_statement": import_stmt,
        "description": desc,
        "props": normalized_props,
        "example": example,
    }


class StorybookConnector:
    """Connects to Storybook index or local manifest to fetch live component schemas."""

    def __init__(self, endpoint_url: Optional[str] = None, cache_dir: Optional[Path] = None):
        self.endpoint_url = endpoint_url or os.getenv("STORYBOOK_URL", "https://storybook.internal.company.com")
        self.cache_dir = cache_dir or (REPO_ROOT / ".cache")
        self.cache_file = self.cache_dir / "storybook_catalog.json"
        self._memory_cache: Optional[Dict[str, Dict[str, Any]]] = None

    def _ensure_cache_dir(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _load_disk_cache(self) -> Optional[Dict[str, Dict[str, Any]]]:
        if not self.cache_file.exists():
            return None
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                content = f.read()
            # Strict Zero-Carbon Policy: If cache contains legacy Carbon artifacts, purge it
            if "@carbon" in content or "carbondesignsystem" in content:
                logger.warning("[catalog] Detected legacy Carbon references in disk cache. Invalidating cache.")
                try:
                    self.cache_file.unlink()
                except Exception:
                    pass
                return None

            raw_data = json.loads(content)
            if not isinstance(raw_data, dict):
                return None

            # Normalize cached specifications
            clean_cache: Dict[str, Dict[str, Any]] = {}
            package_name = os.getenv("DESIGN_SYSTEM_PACKAGE", "@wbg/nexus")
            for k, v in raw_data.items():
                if isinstance(v, dict):
                    norm_name = normalize_component_name(k)
                    clean_cache[norm_name] = normalize_component_spec(norm_name, v, package_name)
            return clean_cache if clean_cache else None
        except Exception as exc:
            logger.debug("[catalog] Error loading disk cache: %s", exc)
            return None

    def _save_disk_cache(self, catalog: Dict[str, Dict[str, Any]]) -> None:
        try:
            self._ensure_cache_dir()
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(catalog, f, indent=2)
            logger.debug("[catalog] Saved %d components to disk cache.", len(catalog))
        except Exception as exc:
            logger.debug("[catalog] Failed to save disk cache: %s", exc)

    def _load_components_json(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """Loads static Tier-2 fallback from components.json, normalizing raw schemas defensively."""
        from config import COMPONENTS_JSON_PATH
        if not COMPONENTS_JSON_PATH.exists():
            return None
        try:
            with open(COMPONENTS_JSON_PATH, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            if not isinstance(raw_data, dict):
                return None

            # Defensively unwrap if schema is wrapped, e.g. {"version": 2, "components": {...}}
            if "components" in raw_data and isinstance(raw_data["components"], dict):
                components_dict = raw_data["components"]
            else:
                components_dict = raw_data

            package_name = os.getenv("DESIGN_SYSTEM_PACKAGE", "@wbg/nexus")
            clean_catalog: Dict[str, Dict[str, Any]] = {}
            for k, v in components_dict.items():
                if isinstance(v, dict):
                    norm_name = normalize_component_name(k)
                    clean_catalog[norm_name] = normalize_component_spec(norm_name, v, package_name)
            return clean_catalog if clean_catalog else None
        except Exception as exc:
            logger.warning("[catalog] Error reading components.json: %s", exc)
            return None

    def harvest_catalog(self) -> Dict[str, Dict[str, Any]]:
        """
        Dynamically harvests component definitions according to enterprise priority:
        1. Live Storybook endpoint (/design-system/index.json or /index.json)
        2. Static components.json fallback (reflecting @wbg/nexus)
        3. Local disk cache (.cache/storybook_catalog.json, filtered for @wbg/nexus)
        4. Offline Nexus fallback catalog (OFFLINE_NEXUS_CATALOG)
        """
        if self._memory_cache is not None:
            return self._memory_cache

        start_time = time.time()
        logger.info("[catalog] Harvesting component catalog (Priority: Storybook -> components.json -> Cache -> Offline Nexus)...")

        # 1. Tier-1: Live Storybook Harvesting
        from config import IS_LIVE_STORYBOOK_CONFIGURED
        if IS_LIVE_STORYBOOK_CONFIGURED and self.endpoint_url and self.endpoint_url.startswith("http"):
            from config import STORYBOOK_MANIFEST_PATH
            endpoints_to_try = [
                self.endpoint_url.rstrip("/") + STORYBOOK_MANIFEST_PATH,
                self.endpoint_url.rstrip("/") + "/index.json",
                self.endpoint_url.rstrip("/") + "/stories.json",
            ]
            for url in endpoints_to_try:
                try:
                    logger.debug("[catalog] Probing Storybook endpoint: %s (timeout=2.0s)", url)
                    with httpx.Client(timeout=2.0) as client:
                        resp = client.get(url)
                        if resp.status_code == 200:
                            stories_data = resp.json()
                            harvested = self._parse_storybook_index(stories_data)
                            if harvested:
                                logger.info("[catalog] Tier-1 SUCCESS: Harvested %d components from live Storybook in %.2fs", len(harvested), time.time() - start_time)
                                self._save_disk_cache(harvested)
                                self._memory_cache = harvested
                                return self._memory_cache
                except Exception as exc:
                    logger.debug("[catalog] Storybook endpoint %s unreachable: %s", url, exc)
                    continue

        # 2. Tier-2: Static components.json Fallback
        components_fallback = self._load_components_json()
        if components_fallback:
            logger.info("[catalog] Tier-2 SUCCESS: Loaded %d components from components.json in %.2fs", len(components_fallback), time.time() - start_time)
            self._save_disk_cache(components_fallback)
            self._memory_cache = components_fallback
            return self._memory_cache

        # 3. Tier-3: Local Disk Cache Fallback (.cache/storybook_catalog.json)
        disk_data = self._load_disk_cache()
        if disk_data and isinstance(disk_data, dict):
            logger.info("[catalog] Tier-3 SUCCESS: Loaded %d components from validated disk cache in %.2fs", len(disk_data), time.time() - start_time)
            self._memory_cache = disk_data
            return self._memory_cache

        # 4. Final resilient baseline: Official Nexus components
        logger.info("[catalog] Tier-4 FALLBACK: Using embedded OFFLINE_NEXUS_CATALOG (%d components)", len(OFFLINE_NEXUS_CATALOG))
        self._memory_cache = OFFLINE_NEXUS_CATALOG
        return self._memory_cache

    def _parse_storybook_index(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Parses Storybook v7+ index.json into structured component specifications."""
        result: Dict[str, Dict[str, Any]] = dict(self._load_components_json() or {})
        entries = data.get("entries", {}) or data.get("stories", {})
        package_name = os.getenv("DESIGN_SYSTEM_PACKAGE", "@wbg/nexus")
        for key, entry in entries.items():
            title = entry.get("title", "")
            title_parts = [p.strip() for p in title.split("/") if p.strip()]
            if len(title_parts) >= 2 and title_parts[0].lower() in ("components", "patterns", "elements", "primitives", "forms"):
                comp_raw = title_parts[1]
            elif title_parts:
                comp_raw = title_parts[-1]
            else:
                comp_raw = entry.get("name", "")

            comp_name = normalize_component_name(comp_raw)
            if not comp_name or comp_name in result:
                continue

            result[comp_name] = normalize_component_spec(
                comp_name=comp_name,
                raw_entry={
                    "description": f"Nexus design system {comp_name} component from {title or 'catalog'}.",
                    "props": {},
                    "example": f"<{comp_name} />",
                },
                package_name=package_name,
            )
        return result

    def get_catalog_summary(self, source: str = "nexus") -> Dict[str, str]:
        """Returns map of component names to brief descriptions, guarding against non-dict entries."""
        catalog = self.harvest_catalog()
        summary: Dict[str, str] = {}
        for name, data in catalog.items():
            if isinstance(data, dict):
                summary[name] = data.get("description", "")
        return summary

    def get_component_spec(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Returns detailed spec for a given component, matching case-insensitively and through normalization."""
        catalog = self.harvest_catalog()
        # Direct lookup
        if component_name in catalog and isinstance(catalog[component_name], dict):
            return catalog[component_name]

        # Normalized lookup e.g. 'components-button' -> 'Button'
        norm = normalize_component_name(component_name)
        if norm in catalog and isinstance(catalog[norm], dict):
            return catalog[norm]

        # Case-insensitive lookup
        lower_map = {k.lower(): v for k, v in catalog.items() if isinstance(v, dict)}
        if component_name.lower() in lower_map:
            return lower_map[component_name.lower()]
        if norm.lower() in lower_map:
            return lower_map[norm.lower()]

        return None
