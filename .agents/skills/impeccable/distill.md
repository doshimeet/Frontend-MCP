# Impeccable Critique Pass: /distill

The `/distill` pass focuses on **structural hierarchy, cognitive load reduction, and information density**. It strips away visual fluff and redundant wrappers to let data breathe and be scanned effortlessly.

---

## The 4 Distillation Directives

### 1. Eliminate Nested Cards ("Cardception")
* **Anti-Pattern**: Placing cards inside cards, inside sections, with multiple overlapping border lines and drop-shadows.
* **Refinement**: Flatten the layout. Use clean horizontal dividers (`--cds-border-subtle`) or subtle background alternations instead of multi-tiered container boxes.
* **Rule**: Maximum **1 level of elevation** across the entire page.

### 2. Eradicate "Status-Chip Soup"
* **Anti-Pattern**: Wrapping every data value (user roles, categories, departments, timestamps) inside colored pill badges.
* **Refinement**: Plain text for plain data. Badges (`Tag`) are strictly reserved for **critical lifecycle states** that change over time (e.g. `Active`, `Pending`, `Failed`, `Archived`).

### 3. Establish Clear Typographic Hierarchy
* **Anti-Pattern**: Every element competing for attention with bold weights and similar font sizes.
* **Refinement**: 
  - **Level 1**: Primary Page Title (`font_size_2xl`, 32px, bold).
  - **Level 2**: Top Metric Number (`font_size_3xl`, 40px, bold) or Section Title (`font_size_lg`, 20px, semibold).
  - **Level 3**: Data table rows / body copy (`font_size_base`, 16px, regular).
  - **Level 4**: Supporting metadata, timestamps, column headers (`font_size_sm`, 14px, muted slate).

### 4. Optimize Information Density for Enterprise Scanning
* **Anti-Pattern**: Mobile-first oversized 48px padding on desktop B2B data tables, forcing the user to scroll endlessly.
* **Refinement**: Use standard Carbon `lg` or `md` density table rows. Users should view at least 8–10 records above the fold without scrolling.

---

## Before & After Code Example

### ❌ Before /distill (Cluttered AI Output):
```tsx
// Status-chip soup + nested cards
<Card className="shadow-lg border p-6">
  <Card className="border p-4">
    <div className="flex gap-2">
      <Badge color="blue">ID: 001</Badge>
      <Badge color="purple">Owner: Sarah</Badge>
      <Badge color="green">Active</Badge>
      <Badge color="yellow">2026-09-22</Badge>
    </div>
  </Card>
</Card>
```

### ✅ After /distill (Clean Enterprise Standard):
```tsx
// Clean single-layer hierarchy with high-contrast text and a single semantic tag
<div className="enterprise-record-row" style={{ borderBottom: "1px solid var(--cds-border-subtle)" }}>
  <span style={{ fontFamily: "var(--cds-code-01)", fontSize: "0.8125rem" }}>001</span>
  <span style={{ fontWeight: 600, color: "var(--cds-text-primary)" }}>Sarah Connor</span>
  <span style={{ color: "var(--cds-text-secondary)", fontSize: "0.875rem" }}>2026-09-22</span>
  <Tag type="green" size="sm">ACTIVE</Tag>
</div>
```
