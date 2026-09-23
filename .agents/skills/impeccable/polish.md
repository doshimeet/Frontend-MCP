# Impeccable Critique Pass: /polish

The `/polish` pass eliminates **AI visual tells, styling inconsistencies, and generic slop**, replacing them with crisp, intentional enterprise craft.

---

## The 4 Polish Directives

### 1. Eradicate Random Italicized Words in Headings
* **Anti-Pattern**: Generative AI models love styling a random word in an `<h1>` with italics and purple gradients:
  `<h1>Experience <i>seamless</i> automated intelligence</h1>`
* **Refinement**: Pure, confident typographic weight. Enterprise B2B software is clear and direct:
  `<h1>Operations & Security Intelligence</h1>`

### 2. Kill "AI Beige" & Muddy Background Washes
* **Anti-Pattern**: Pale yellow/beige backgrounds (`#fdfbf7`, `#faf8f5`) randomly inserted into B2B SaaS views, making the UI look dirty or low-contrast.
* **Refinement**: 
  - For Corporate B2B: Crisp white canvas (`#ffffff`) with subtle cool-gray surfaces (`#f4f4f4`) or dark slate (`#161616` / `#262626`).
  - For Agency Clients: Only use warm tones when explicitly activating `client-warm-sage` where linen and sage are harmonized across all tokens.

### 3. Enforce Strict Border Radius Consistency
* **Anti-Pattern**: Mixing arbitrary border radii (e.g. `border-radius: 18px` on cards, `0px` on inputs, `30px` on buttons).
* **Refinement**:
  - `radius.none` (`0px`): Tables, global header, tabs.
  - `radius.sm` (`2px`): Status tags, tooltips.
  - `radius.md` (`4px`): Buttons, inputs, modal containers.
  - `radius.full` (`9999px`): Exclusively for circular avatar icons and status dot indicators.

### 4. Professional Micro-Interactions & Keyboard Focus Rings
* **Anti-Pattern**: Zero hover feedback, or excessive bouncy animations that delay user actions.
* **Refinement**:
  - Smooth 150ms ease transitions on interactive controls (`transition: background-color 0.15s ease`).
  - High-visibility focus indicators (WCAG 2.4.7): `outline: 2px solid var(--cds-focus); outline-offset: 2px;`.

---

## Before & After Code Example

### ❌ Before /polish (AI Tells):
```tsx
// Random italics, AI beige background, arbitrary radius, no focus indicator
<div style={{ backgroundColor: "#fbf9f4", borderRadius: "22px", padding: "30px" }}>
  <h1 style={{ color: "#333" }}>
    Monitor your <span style={{ fontStyle: "italic", color: "#6366f1" }}>effortless</span> workflows
  </h1>
  <button style={{ borderRadius: "50px", backgroundColor: "#6366f1", color: "white" }}>
    Click Here
  </button>
</div>
```

### ✅ After /polish (Crisp Enterprise Craft):
```tsx
// Strict design tokens, confident typography, precision border radius, accessible focus
<div style={{ backgroundColor: "var(--cds-layer)", borderRadius: "4px", padding: "1.5rem" }}>
  <h1 style={{ fontSize: "1.75rem", fontWeight: 700, margin: 0, color: "var(--cds-text-primary)" }}>
    Workflow Telemetry & Operations
  </h1>
  <Button kind="primary" size="md">
    Export Audit Report
  </Button>
</div>
```
