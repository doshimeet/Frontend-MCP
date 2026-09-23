"use client";

import React, { useState } from "react";
import {
  ProgressIndicator,
  ProgressStep,
  Form,
  FormGroup,
  TextInput,
  Select,
  SelectItem,
  Checkbox,
  Button,
  InlineNotification,
  Tile,
} from "@carbon/react";

export interface WizardFormData {
  // Step 1: Enterprise Profile
  orgName: string;
  adminEmail: string;
  department: string;
  // Step 2: Infrastructure Configuration
  envTier: string;
  cloudRegion: string;
  highAvailability: boolean;
  // Step 3: Security & Governance
  mfaEnforced: boolean;
  auditRetentionDays: string;
  ipWhitelist: string;
}

export interface FormWizardRecipeProps {
  wizardTitle?: string;
  wizardSubtitle?: string;
  onComplete?: (data: WizardFormData) => void;
  onCancel?: () => void;
}

const INITIAL_DATA: WizardFormData = {
  orgName: "",
  adminEmail: "",
  department: "engineering",
  envTier: "production",
  cloudRegion: "eastus",
  highAvailability: true,
  mfaEnforced: true,
  auditRetentionDays: "365",
  ipWhitelist: "",
};

export const FormWizardRecipe: React.FC<FormWizardRecipeProps> = ({
  wizardTitle = "Enterprise Tenant Onboarding",
  wizardSubtitle = "Configure enterprise infrastructure boundaries, security policies, and administrative credentials.",
  onComplete,
  onCancel,
}) => {
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [formData, setFormData] = useState<WizardFormData>(INITIAL_DATA);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submissionError, setSubmissionError] = useState<string | null>(null);

  const steps = [
    { label: "Profile & Identity", secondaryLabel: "Organization credentials" },
    { label: "Infrastructure", secondaryLabel: "Cloud tier & region" },
    { label: "Governance & Security", secondaryLabel: "MFA & compliance" },
    { label: "Review & Deploy", secondaryLabel: "Final verification" },
  ];

  const validateStep = (stepIndex: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (stepIndex === 0) {
      if (!formData.orgName.trim()) {
        newErrors.orgName = "Organization name is required.";
      }
      if (!formData.adminEmail.trim() || !formData.adminEmail.includes("@")) {
        newErrors.adminEmail = "A valid corporate email address is required.";
      }
    } else if (stepIndex === 1) {
      if (!formData.cloudRegion) {
        newErrors.cloudRegion = "Please select a target cloud deployment region.";
      }
    } else if (stepIndex === 2) {
      if (!formData.auditRetentionDays) {
        newErrors.auditRetentionDays = "Retention duration must be defined.";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (!validateStep(currentStep)) return;
    if (currentStep < steps.length - 1) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setErrors({});
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;
    setIsSubmitting(true);
    setSubmissionError(null);

    try {
      // Simulated cloud provisioning execution
      await new Promise((res) => setTimeout(res, 1000));
      onComplete?.(formData);
      alert("Tenant configuration successfully provisioned!");
    } catch (err: any) {
      setSubmissionError(err.message || "Failed to provision tenant resources. Please retry.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="form-wizard-container" style={{ width: "100%", maxWidth: "800px", margin: "0 auto", padding: "1.5rem" }}>
      {/* 1. Header */}
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "1.75rem", fontWeight: 600, margin: 0, color: "var(--cds-text-primary, #161616)" }}>
          {wizardTitle}
        </h1>
        <p style={{ margin: "0.25rem 0 0", color: "var(--cds-text-secondary, #525252)", fontSize: "0.875rem" }}>
          {wizardSubtitle}
        </p>
      </div>

      {/* 2. Visual Progress Stepper */}
      <div style={{ marginBottom: "2.5rem" }}>
        <ProgressIndicator currentIndex={currentStep} aria-label="Tenant onboarding progression">
          {steps.map((step, idx) => (
            <ProgressStep
              key={step.label}
              label={step.label}
              description={step.secondaryLabel}
              complete={idx < currentStep}
              current={idx === currentStep}
              invalid={idx === currentStep && Object.keys(errors).length > 0}
            />
          ))}
        </ProgressIndicator>
      </div>

      {/* 3. Error Banner */}
      {submissionError && (
        <div style={{ marginBottom: "1.5rem" }}>
          <InlineNotification
            kind="error"
            title="Provisioning Error"
            subtitle={submissionError}
            aria-label="Submission error notification"
          />
        </div>
      )}

      {/* 4. Multi-Step Form Panes */}
      <div
        style={{
          background: "var(--cds-layer, #ffffff)",
          border: "1px solid var(--cds-border-subtle, #e0e0e0)",
          padding: "2rem",
          minHeight: "340px",
          borderRadius: "4px",
        }}
      >
        <Form>
          {/* STEP 0: Organization Profile */}
          {currentStep === 0 && (
            <div>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 600, margin: "0 0 1.5rem" }}>Organization Profile</h2>
              <FormGroup legendText="">
                <TextInput
                  id="orgName"
                  labelText="Organization Legal Name"
                  placeholder="e.g. Acme Health Corp"
                  value={formData.orgName}
                  invalid={!!errors.orgName}
                  invalidText={errors.orgName}
                  onChange={(e) => setFormData({ ...formData, orgName: e.target.value })}
                  style={{ marginBottom: "1.25rem" }}
                />

                <TextInput
                  id="adminEmail"
                  labelText="Primary Administrative Email"
                  placeholder="admin@enterprise.com"
                  type="email"
                  value={formData.adminEmail}
                  invalid={!!errors.adminEmail}
                  invalidText={errors.adminEmail}
                  onChange={(e) => setFormData({ ...formData, adminEmail: e.target.value })}
                  style={{ marginBottom: "1.25rem" }}
                />

                <Select
                  id="department"
                  labelText="Primary Operational Unit"
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                >
                  <SelectItem value="engineering" text="Engineering & Infrastructure" />
                  <SelectItem value="finance" text="Finance & Accounting" />
                  <SelectItem value="clinical" text="Clinical & Healthcare Operations" />
                  <SelectItem value="legal" text="Legal & Corporate Compliance" />
                </Select>
              </FormGroup>
            </div>
          )}

          {/* STEP 1: Infrastructure */}
          {currentStep === 1 && (
            <div>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 600, margin: "0 0 1.5rem" }}>Cloud Infrastructure</h2>
              <FormGroup legendText="">
                <Select
                  id="envTier"
                  labelText="Deployment Tier"
                  value={formData.envTier}
                  onChange={(e) => setFormData({ ...formData, envTier: e.target.value })}
                  style={{ marginBottom: "1.25rem" }}
                >
                  <SelectItem value="production" text="Production (Multi-AZ with Automated Failover)" />
                  <SelectItem value="staging" text="Staging / Pre-Release" />
                  <SelectItem value="development" text="Development Sandbox" />
                </Select>

                <Select
                  id="cloudRegion"
                  labelText="Primary Cloud Region"
                  value={formData.cloudRegion}
                  invalid={!!errors.cloudRegion}
                  invalidText={errors.cloudRegion}
                  onChange={(e) => setFormData({ ...formData, cloudRegion: e.target.value })}
                  style={{ marginBottom: "1.5rem" }}
                >
                  <SelectItem value="eastus" text="US East (Virginia - Azure Data Center)" />
                  <SelectItem value="westus" text="US West (Washington)" />
                  <SelectItem value="westeurope" text="West Europe (Amsterdam)" />
                </Select>

                <Checkbox
                  id="highAvailability"
                  labelText="Enable Automated Multi-Zone Geo-Replication"
                  checked={formData.highAvailability}
                  onChange={(_, { checked }) => setFormData({ ...formData, highAvailability: checked })}
                />
              </FormGroup>
            </div>
          )}

          {/* STEP 2: Governance & Security */}
          {currentStep === 2 && (
            <div>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 600, margin: "0 0 1.5rem" }}>Security & Access Governance</h2>
              <FormGroup legendText="">
                <div style={{ marginBottom: "1.25rem" }}>
                  <Checkbox
                    id="mfaEnforced"
                    labelText="Enforce Hardware / FIDO2 Multi-Factor Authentication for all users"
                    checked={formData.mfaEnforced}
                    onChange={(_, { checked }) => setFormData({ ...formData, mfaEnforced: checked })}
                  />
                </div>

                <Select
                  id="auditRetentionDays"
                  labelText="Security Audit Log Retention Schedule"
                  value={formData.auditRetentionDays}
                  onChange={(e) => setFormData({ ...formData, auditRetentionDays: e.target.value })}
                  style={{ marginBottom: "1.25rem" }}
                >
                  <SelectItem value="90" text="90 Days (Standard Development)" />
                  <SelectItem value="365" text="1 Year (SOX / HIPAA Baseline)" />
                  <SelectItem value="2555" text="7 Years (Financial / Institutional Grade)" />
                </Select>

                <TextInput
                  id="ipWhitelist"
                  labelText="Restricted Corporate IP CIDR Blocks (Optional)"
                  placeholder="e.g. 198.51.100.0/24, 203.0.113.0/24"
                  value={formData.ipWhitelist}
                  onChange={(e) => setFormData({ ...formData, ipWhitelist: e.target.value })}
                />
              </FormGroup>
            </div>
          )}

          {/* STEP 3: Review & Summary */}
          {currentStep === 3 && (
            <div>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 600, margin: "0 0 1rem" }}>Configuration Summary</h2>
              <p style={{ fontSize: "0.875rem", color: "var(--cds-text-secondary, #525252)", margin: "0 0 1.5rem" }}>
                Verify all operational settings before provisioning the tenant environment.
              </p>

              <Tile style={{ marginBottom: "1rem", background: "var(--cds-layer-accent, #f4f4f4)" }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", fontSize: "0.875rem" }}>
                  <div>
                    <strong>Organization:</strong> {formData.orgName || "Not specified"}
                  </div>
                  <div>
                    <strong>Admin Email:</strong> {formData.adminEmail || "Not specified"}
                  </div>
                  <div>
                    <strong>Tier:</strong> {formData.envTier.toUpperCase()}
                  </div>
                  <div>
                    <strong>Region:</strong> {formData.cloudRegion}
                  </div>
                  <div>
                    <strong>Geo-Replication:</strong> {formData.highAvailability ? "Enabled" : "Disabled"}
                  </div>
                  <div>
                    <strong>MFA Mandate:</strong> {formData.mfaEnforced ? "Enforced" : "Optional"}
                  </div>
                  <div>
                    <strong>Log Retention:</strong> {formData.auditRetentionDays} Days
                  </div>
                </div>
              </Tile>
            </div>
          )}
        </Form>
      </div>

      {/* 5. Sticky Bottom Action Controls */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: "1.5rem",
          padding: "1rem 0",
          borderTop: "1px solid var(--cds-border-subtle, #e0e0e0)",
        }}
      >
        <Button kind="ghost" size="md" onClick={onCancel || (() => alert("Cancelled"))}>
          Cancel
        </Button>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          {currentStep > 0 && (
            <Button kind="secondary" size="md" onClick={handleBack} disabled={isSubmitting}>
              Back
            </Button>
          )}

          {currentStep < steps.length - 1 ? (
            <Button kind="primary" size="md" onClick={handleNext}>
              Next Step
            </Button>
          ) : (
            <Button kind="primary" size="md" onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting ? "Provisioning..." : "Confirm & Provision"}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default FormWizardRecipe;
