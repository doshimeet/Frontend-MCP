# Impeccable Critique Pass: /harden

The `/harden` pass ensures that the user interface is **resilient against network latency, empty data, unexpected API errors, and accessibility barriers (WCAG 2.1 AA)**.

---

## The 4 Hardening Directives

### 1. Skeleton Loading States Must Match Real Geometry
* **Anti-Pattern**: A generic spinner in the middle of a blank white screen that causes jarring Layout Shift (CLS) when data loads.
* **Refinement**: 
  - Use `SkeletonText` matching the exact count of columns, table rows, or card headers.
  - Geometry preserves space so content slides in seamlessly without layout jumps.

### 2. Meaningful Empty States with Primary Call to Action
* **Anti-Pattern**: An empty white box or blank table that leaves the user wondering if the system is broken or empty.
* **Refinement**:
  - Two distinct scenarios handled:
    1. **Initial Empty State** (Zero records created yet): Friendly header, 1-sentence value explanation, and primary `Create First Item` action button.
    2. **Zero Search Results** (Filters return no items): Message explaining that no matches were found, accompanied by a `Clear Filters` button.

### 3. Error Boundaries & Inline Notifications
* **Anti-Pattern**: The entire screen crashing into a React error boundary screen (`Minified React error #...`).
* **Refinement**:
  - Component-level containment.
  - Display Carbon `InlineNotification` (`kind="error"`) directly above the affected component.
  - Keep the rest of the navigation and page operational.

### 4. WCAG 2.1 AA Compliance Verification
* **Anti-Pattern**: Missing `aria-label` on icon buttons, low-contrast text on colored badges, broken keyboard tab loops.
* **Refinement**:
  - Contrast Ratio: Minimum **4.5:1** for normal text, **3:1** for large text / UI borders.
  - Visible Focus Ring: All interactive elements must exhibit a high-contrast focus ring (`--cds-focus`).
  - Screen Reader Announcements: Dynamic status changes must be wrapped in `aria-live="polite"`.

---

## Before & After Code Example

### ❌ Before /harden (Fragile & Unhandled):
```tsx
// Crashes if items is empty or loading
<div>
  {isLoading && <p>Loading...</p>}
  <table>
    {items.map((it) => <tr><td>{it.name}</td></tr>)}
  </table>
</div>
```

### ✅ After /harden (Resilient Enterprise Implementation):
```tsx
<div>
  {errorMessage && (
    <InlineNotification
      kind="error"
      title="Failed to retrieve records"
      subtitle={errorMessage}
      actions={<Button kind="ghost" size="sm" onClick={retry}>Retry</Button>}
    />
  )}

  <Table>
    <TableBody>
      {isLoading ? (
        Array.from({ length: 5 }).map((_, i) => (
          <TableRow key={i}>
            <TableCell><SkeletonText paragraph={false} /></TableCell>
            <TableCell><SkeletonText paragraph={false} /></TableCell>
          </TableRow>
        ))
      ) : items.length === 0 ? (
        <TableRow>
          <TableCell colSpan={2} style={{ textAlign: "center", padding: "3rem" }}>
            <h3>No records available</h3>
            <p>Get started by creating your first entity.</p>
            <Button kind="primary" size="sm" onClick={handleCreate}>+ Create Record</Button>
          </TableCell>
        </TableRow>
      ) : (
        items.map((it) => (
          <TableRow key={it.id}>
            <TableCell>{it.name}</TableCell>
          </TableRow>
        ))
      )}
    </TableBody>
  </Table>
</div>
```
