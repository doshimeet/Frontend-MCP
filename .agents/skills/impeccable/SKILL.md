---
name: impeccable
description: >-
  Enterprise design critique and anti-slop refinement skill. Enforces strict design tokens,
  eliminates generic AI design tells, polishes typography hierarchy, and hardens resilient UI states.
---

# Impeccable Design Critique Skill

This skill governs the visual quality, semantic density, and user experience standards for all frontend code generated in this workspace. It acts as an automated design partner that audits and refines candidate TSX/JSX code through 4 specialized passes:

1. **`/distill`** ([distill.md](./distill.md)): Structural simplification, cognitive load reduction, and information hierarchy.
2. **`/polish`** ([polish.md](./polish.md)): Removal of AI visual tells (AI beige, random italics, arbitrary radii), micro-interaction refinement.
3. **`/clarify`** ([clarify.md](./clarify.md)): Micro-copy optimization, actionable button verbs, and intuitive error messaging.
4. **`/harden`** ([harden.md](./harden.md)): Resilient states (loading skeletons, empty states, error boundaries, WCAG 2.1 AA keyboard/contrast compliance).

---

## When to Activate This Skill

Activate this skill:
- Immediately after generating or modifying any UI component, page, or dashboard.
- Before committing any frontend code or presenting it to the user.
- When invoked by the MCP prompt `impeccable_design_critique`.
- During step 4 of the master UI generation workflow (`.agents/workflows/build-ui.md`).

---

## Core Anti-Slop Principles

| AI Anti-Pattern ("Slop") | Enterprise Standard ("Impeccable") |
| :--- | :--- |
| **Status-Chip Soup**: Wrapping every label, column, and table value in colored pill badges. | Badges are reserved exclusively for actionable, critical lifecycle states (e.g., `Active`, `Suspended`, `Failed`). |
| **Nested Cards Inside Cards**: Deeply stacked border boxes creating visual noise. | Flat surface hierarchy with subtle dividers (`--cds-border-subtle`) and single-level elevation. |
| **Oversized Hero Banners**: 400px empty gradients pushing data below the fold. | Compact headers with high information density; data visible immediately upon load. |
| **Arbitrary Hex & Inline CSS**: `color: #4a5568; margin-top: 17px;`. | Strict token mapping (`var(--cds-text-secondary)`, `var(--cds-spacing-md)`). |
| **Missing States**: Blank white screen during data fetching or zero-result searches. | Explicit Loading Skeletons matching table/card geometry + Empty states with a clear primary CTA. |

---

## Execution Protocol

When reviewing candidate code:
1. Run **`/distill`** first to eliminate structural clutter.
2. Run **`/polish`** to clean styling, spacing, and typography.
3. Run **`/clarify`** to tighten all user-facing labels and verbs.
4. Run **`/harden`** to verify resilience, keyboard accessibility, and contrast.
5. Provide the final refined TSX file with inline comments highlighting key architectural upgrades.
