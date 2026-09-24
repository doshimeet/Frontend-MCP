# GitHub Copilot Instructions: Nexus Design System (v2.0.0)

You are assisting with frontend development using the World Bank Group **Nexus Design System**.

## 1. Design Tokens & Styling Sovereignty
- **Never write raw hex colors** (`#002244`, `#0071bc`) or arbitrary Tailwind colors (`bg-blue-600`) in component JSX or inline styles.
- Always use Nexus CSS variables from `packages/tokens/nexus-tokens.css`:
  - Brand Navy: `var(--nexus-color-primary)`
  - Interactive Action: `var(--nexus-color-interactive-primary)`
  - Background Canvas: `var(--nexus-color-background-canvas)`
  - Card Surface: `var(--nexus-color-background-surface)`
  - Text Primary: `var(--nexus-color-text-primary)`
  - Text Secondary: `var(--nexus-color-text-secondary)`
- Always use layered elevation classes:
  - `.nexus-card`, `.nexus-kpi-card`, `.nexus-table`, `.nexus-badge`

## 2. Institutional Quality & Anti-Slop Rules
Read and adhere strictly to `.agents/skills/wbg-enterprise-rules.md`:
- **Heading Order**: Exactly one `<h1>` per page. Do not stack repetitive sub-headings.
- **Badge Hygiene**: Reserve badges strictly for operational lifecycle states (`Active`, `Disbursing`). Do not plaster badges on metric figures or every table header.
- **Data Density**: Financial amounts, percentages, and project IDs must use `tabular-nums` and right-align in tables.
- **Security Pill**: Use the integrated `.nexus-classification-pill` (`🔒 OFFICIAL USE ONLY`) inside navigation; never render full-width yellow caution tape.

## 3. Aesthetic Taste & Polish
- For visual direction, typography choices, and layout personality, reference `.agents/skills/design-taste-frontend/SKILL.md`.
- For micro-interactions, accessibility checks, and UX clarity, reference `.agents/skills/impeccable/`.
