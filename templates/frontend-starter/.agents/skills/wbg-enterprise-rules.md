# WBG Nexus Enterprise Design Rules & Quality Standards

This document bridges the general aesthetic guidance of **Taste Skill** (`design-taste-frontend`) and **Impeccable** (`impeccable`) with the mission-critical institutional requirements of the **World Bank Group (WBG)** and multilateral development banks.

---

## 1. Core Institutional Directives

### 1.1 Contrast & Accessibility (Non-Negotiable)
- **WCAG 2.1 AA Compliance**: All text and interactive components must strictly achieve a minimum contrast ratio of **4.5:1** for standard body text and **3:1** for headers/graphical UI boundaries.
- **Never Sacrificing Readability for "Aesthetic Subtlety"**:
  - Do NOT use low-contrast grey text (e.g. `#9ca3af` or `#888888`) on white or light grey backgrounds.
  - Body text must use `--nexus-color-text-primary` (`#222222` or `#111827`).
  - Secondary/metadata text must use `--nexus-color-text-secondary` (`#4b5563` or `#595959`), guaranteed $\ge 4.5:1$ against `#ffffff`.
  - All interactive elements must maintain distinct focus indicators (`outline: 2px solid var(--nexus-color-interactive-primary)` with `outline-offset: 2px`).

### 1.2 Institutional Color Palette & Brand Consistency
- **Primary Navy**: `var(--nexus-color-primary)` (`#002244`) — anchors the header, branding, navigation, and executive accents.
- **Interactive Blue**: `var(--nexus-color-interactive-primary)` (`#0071bc`) — primary buttons, active links, selected tabs.
- **Surface & Canvas**:
  - Background Canvas: `var(--nexus-color-background-canvas)` (`#f8f9fa` or `#f3f4f6`).
  - Card/Container Surface: `var(--nexus-color-background-surface)` (`#ffffff`).
  - Subtle Muted Surface: `var(--nexus-color-background-subtle)` (`#f1f5f9`).
- **Semantic Status Tones**:
  - Success / Active: `#0d6832` (text/border), `#e6f4ea` (fill) — contrast $\ge 4.5:1$.
  - Warning / Under Review: `#8c5800` (text/border), `#fef7e0` (fill) — contrast $\ge 4.5:1$.
  - Danger / High Risk: `#b31b1b` (text/border), `#fce8e6` (fill) — contrast $\ge 4.5:1$.
  - Informational / Pipeline: `#004085` (text/border), `#cce5ff` (fill) — contrast $\ge 4.5:1$.

### 1.3 Token Indirection & Bespoke Theme Inversion Protocol
- **Absolute Rule**: NEVER hardcode raw color hex values (`#002244`, `#0071bc`, `#e0e0e0`) in component JSX or inline styles. Always reference `var(--nexus-color-*)` and `var(--nexus-elevation-*)`.
- **Theme Inversion Protocol**: When custom branding or bespoke palettes are requested, do NOT rewrite component markup. Taste Skill curates the palette and overrides root CSS variables (`:root { --nexus-color-interactive-primary: #...; }`), leaving component architecture untouched.
- **Contrast Assurance**: Taste Skill (Button Contrast Check) and Impeccable (`colorize.md`) natively verify WCAG AA ($\ge 4.5:1$) contrast on custom themes.

---

## 2. Anti-Slop Architectural Rules

### 2.1 Eliminate Raw Inline Style Spaghetti
- **Rule**: Never generate components with deep nested inline style blocks (`style={{ display: 'flex', border: '1px solid #ccc', ... }}`).
- **Enforcement**: Components must compose predefined Nexus utility classes (`.nexus-card`, `.nexus-kpi-card`, `.nexus-table`, `.nexus-badge`, `.nexus-toolbar`) or dedicated scoped CSS modules.
- **Why**: Inline styles prevent theme inheritance, break responsive overrides, bloat bundle size, and fail programmatic style audits.

### 2.2 Heading & Hierarchy Hygiene
- **Rule**: Exactly **one** `<h1>` per page or screen context.
- **Forbidden**: Do not stack repetitive, redundant headers like:
  ```html
  <!-- FORBIDDEN AI SLOP -->
  <h1>Operations 360</h1>
  <h2>Operations 360 Overview</h2>
  <h3>Operations 360 Dashboard Portfolio</h3>
  ```
- **Approved Institutional Pattern**:
  ```html
  <!-- APPROVED HIERARCHY -->
  <header class="nexus-page-header">
    <div class="nexus-page-header__meta">
      <span class="nexus-breadcrumb">Global Practices / East Asia & Pacific</span>
      <h1 class="nexus-page-title">Operations 360</h1>
    </div>
    <div class="nexus-page-header__actions">
      <!-- primary contextual actions -->
    </div>
  </header>
  ```

### 2.3 Status-Chip & Badge Hygiene
- **Forbidden**: Do not plaster status badges onto every metric card, table header, or label ("status-chip soup").
- **Approved Rule**:
  - Use badges **only** for operational state transitions (`Active`, `Disbursing`, `Under Audit`, `Closed`).
  - For statistical metrics (e.g. `$4.2B Committed`, `98.4% On Schedule`), use a dedicated **StatCard** typography hierarchy with clear labels and tabular figures, NOT colored pill badges.

### 2.4 Surface Depth Over Harsh 1px Grid Lines
- **Forbidden**: Enclosing every widget, stat box, and row in a harsh `1px solid #e0e0e0` or `1px solid #d1d5db` line border.
- **Approved Pattern**:
  - Use subtle layered elevation shadows with soft border blending:
    - Subtle Surface: `box-shadow: 0 1px 3px rgba(0, 34, 68, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04); border: 1px solid rgba(0, 34, 68, 0.08);`
    - Raised Interactive: `box-shadow: 0 4px 12px rgba(0, 34, 68, 0.08), 0 2px 4px rgba(0, 0, 0, 0.04);`
    - Modal / Floating: `box-shadow: 0 12px 32px rgba(0, 34, 68, 0.12), 0 4px 8px rgba(0, 0, 0, 0.06);`

---

## 3. Financial & Operational Data Density

1. **Tabular Numerics**: Always apply `font-variant-numeric: tabular-nums` or `font-feature-settings: "tnum"` to monetary figures, percentages, dates, and project IDs so columns align cleanly.
2. **Alignment Standards**:
   - Numbers, monetary amounts, and dates $\rightarrow$ **Right-aligned**.
   - Text, titles, descriptions, and statuses $\rightarrow$ **Left-aligned**.
   - Action icon buttons $\rightarrow$ **Right-aligned** or centered in explicit action columns.
3. **Empty States & Loading States**:
   - Every data table and chart container MUST handle empty, loading, and error states gracefully.
   - Never display a blank white rectangle. Use `<EmptyState title="..." description="..." action="..." />`.

---

## 4. Header & Security Banner Design
- **Forbidden**: Neon yellow or high-saturation caution-tape banners stretching across the entire screen (`background: #ffcc00; height: 40px;`).
- **Approved Pattern**:
  - Compact institutional top bar (48–56px height).
  - Subtle, dignified classification pill integrated directly into the header or navigation bar:
    `<span class="nexus-classification-pill">OFFICIAL USE ONLY</span>`
  - Crisp typography, dark navy background (`#002244`), clear user profile avatar and institutional emblem.

---

## 5. Summary Checklist Before Emitting Code
1. [ ] Did I eliminate raw inline CSS styles in favor of Nexus tokens/classes?
2. [ ] Is there exactly one clean `<h1>` without repetitive subtitle headers?
3. [ ] Are status badges used judiciously instead of on every element?
4. [ ] Do all colors meet WCAG AA contrast ($\ge 4.5:1$ text)?
5. [ ] Are tables using tabular numbers and right-aligned metrics?
6. [ ] Is the security banner cleanly integrated rather than a jarring yellow strip?
