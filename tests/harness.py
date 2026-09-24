#!/usr/bin/env python3
"""
CLI Diagnostic Harness for Enterprise Design System MCP
Allows running and inspecting any MCP tool directly from the terminal.

Usage examples:
  python tests/harness.py health
  python tests/harness.py tokens --theme default
  python tests/harness.py components
  python tests/harness.py props --name Button
  python tests/harness.py plan --text "Build an invoice audit screen with filterable status"
  python tests/harness.py recipes
"""

import argparse
import json
import sys
from pathlib import Path

# Add repository root to sys.path
SERVER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVER_DIR))

from services.health_service import HealthService
from services.token_service import TokenService
from services.requirements_service import RequirementsService
from connectors.storybook_connector import OFFLINE_CARBON_CATALOG
from config import RECIPES_DIR

health_svc = HealthService()
token_svc = TokenService()
req_svc = RequirementsService()


def main():
    parser = argparse.ArgumentParser(description="Enterprise Design System MCP CLI Test Harness")
    subparsers = parser.add_subparsers(dest="command", help="Diagnostic command to run")

    # Command: health
    subparsers.add_parser("health", help="Run pre-flight environment health check")

    # Command: tokens
    tokens_parser = subparsers.add_parser("tokens", help="Fetch design tokens")
    tokens_parser.add_argument("--category", default="all", help="Token category (all, color, spacing)")
    tokens_parser.add_argument("--theme", default="default", help="Theme name")

    # Command: components
    subparsers.add_parser("components", help="List all catalog components")

    # Command: props
    props_parser = subparsers.add_parser("props", help="Get props for a component")
    props_parser.add_argument("--name", required=True, help="Component name (e.g. Button, DataTable)")

    # Command: plan
    plan_parser = subparsers.add_parser("plan", help="Parse requirements into architecture plan")
    plan_parser.add_argument("--text", required=True, help="Requirements / PRD text")
    plan_parser.add_argument("--theme", default="default", help="Theme name")

    # Command: recipes
    recipes_parser = subparsers.add_parser("recipes", help="List or inspect page recipes")
    recipes_parser.add_argument("--name", help="Specific recipe name to view code (e.g. CrudTableRecipe)")

    args = parser.parse_args()

    if not args.command or args.command == "health":
        print("\n=== ENVIRONMENT HEALTH DIAGNOSTICS ===")
        health = health_svc.run_diagnostics()
        print(health.model_dump_json(indent=2))
        return

    if args.command == "tokens":
        print(f"\n=== DESIGN TOKENS (theme={args.theme}, category={args.category}) ===")
        resp = token_svc.get_category_tokens(category=args.category, theme=args.theme)
        print(resp.model_dump_json(indent=2))
        return

    if args.command == "components":
        print("\n=== COMPONENT CATALOG ===")
        summary = {k: v["description"] for k, v in OFFLINE_CARBON_CATALOG.items()}
        print(json.dumps(summary, indent=2))
        return

    if args.command == "props":
        print(f"\n=== COMPONENT SPECS ({args.name}) ===")
        if args.name in OFFLINE_CARBON_CATALOG:
            print(json.dumps(OFFLINE_CARBON_CATALOG[args.name], indent=2))
        else:
            print(f"Component '{args.name}' not found. Available: {list(OFFLINE_CARBON_CATALOG.keys())}")
        return

    if args.command == "plan":
        print("\n=== ARCHITECTURAL BLUEPRINT FROM REQUIREMENTS ===")
        plan = req_svc.plan_architecture(args.text, args.theme)
        print(plan.model_dump_json(indent=2))
        return

    if args.command == "recipes":
        if args.name:
            clean_name = args.name.removesuffix(".tsx")
            target_file = RECIPES_DIR / f"{clean_name}.tsx"
            print(f"\n=== PAGE RECIPE CODE ({clean_name}) ===")
            if target_file.exists():
                print(target_file.read_text(encoding="utf-8"))
            else:
                print(f"Recipe file '{target_file}' not found.")
            return

        print("\n=== AVAILABLE PAGE RECIPES CATALOG ===")
        catalog_file = RECIPES_DIR / "recipes.json"
        if catalog_file.exists():
            with open(catalog_file, "r", encoding="utf-8") as f:
                recipes = json.load(f)
            for idx, r in enumerate(recipes, 1):
                print(f"{idx}. {r['name']} ({r['title']})")
                print(f"   Description: {r['description']}")
                print(f"   Best For:    {r['best_for']}")
                print(f"   Components:  {', '.join(r.get('required_components', []))}\n")
        else:
            print("1. CrudTableRecipe - Enterprise data table with search, badges, pagination.")
            print("2. MetricsDashboardRecipe - KPI cards with trends and data grid.")
            print("3. FormWizardRecipe - Multi-step intake form with validation.")
        return


if __name__ == "__main__":
    main()
