# Impeccable Critique Pass: /clarify

The `/clarify` pass focuses on **UX micro-copy, contextual clarity, and intuitive user action labels**. It eliminates ambiguous buttons, robotic error codes, and confusing instructional copy.

---

## The 4 Clarify Directives

### 1. Action-Oriented Verbs for Primary Actions
* **Anti-Pattern**: Generic, passive, or ambiguous labels like "Submit", "Send", "Click Here", "OK", "Go".
* **Refinement**: Explicit, task-oriented verbs describing the exact outcome of the user's action:
  - ❌ `Submit` $\rightarrow$ ✅ `Register Service`
  - ❌ `Save` $\rightarrow$ ✅ `Apply Security Policy`
  - ❌ `Done` $\rightarrow$ ✅ `Complete Onboarding`
  - ❌ `Click here to export` $\rightarrow$ ✅ `Export Audit Log (CSV)`

### 2. High-Clarity Destructive Action Confirmations
* **Anti-Pattern**: Vague modal dialogs: *"Are you sure you want to proceed?"*
* **Refinement**: Explicitly name the resource being affected and the irreversibility:
  - ❌ *"Are you sure?"*
  - ✅ *"Permanently delete gateway cluster 'api-prod-east'? This action cannot be undone and will revoke 14 active API keys."*
  - Button: `Delete Cluster (Irreversible)` with `danger` variant.

### 3. Human Error Messaging with Recovery Paths
* **Anti-Pattern**: Cryptic stack traces or unhelpful error alerts:
  - *"An unexpected error occurred: code 500."*
* **Refinement**: Three-part structure: **What happened**, **Why it happened**, and **How to recover**:
  - *"Unable to connect to the telemetry pipeline. The broker is temporarily unreachable. Verify VPN connection or retry in 60 seconds."*
  - Always provide an inline `Retry` button.

### 4. Semantic Field Association & Accessible Descriptions
* **Anti-Pattern**: Inputs without associated `<label>` or using placeholder text as a replacement for labels.
* **Refinement**:
  - Every form input must have a permanent visible label linked via `id` / `labelText`.
  - Placeholder text is exclusively for formatting hints (e.g. `e.g. 198.51.100.0/24`), never for instructions.

---

## Before & After Code Example

### ❌ Before /clarify (Vague & Robotic):
```tsx
<Modal open={isOpen} modalHeading="Confirm" primaryButtonText="Submit">
  <p>Are you sure?</p>
  <input placeholder="Enter name" />
</Modal>
```

### ✅ After /clarify (Explicit, Human & Accessible):
```tsx
<Modal
  open={isOpen}
  modalHeading="Decommission Healthcare Gateway"
  primaryButtonText="Decommission Gateway"
  secondaryButtonText="Cancel"
  danger
  onRequestSubmit={handleDecommission}
>
  <p style={{ color: "var(--cds-text-secondary)", marginBottom: "1rem" }}>
    You are about to decommission gateway <strong>gw-hlth-east-01</strong>. 
    Traffic will automatically reroute to the secondary cluster.
  </p>
  <TextInput
    id="decommission-reason"
    labelText="Reason for Decommissioning"
    placeholder="e.g. Scheduled migration to v2 cluster"
    helperText="Recorded in the permanent compliance audit log."
  />
</Modal>
```
