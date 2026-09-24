"use client";

import React, { useState } from "react";
import {
  Progress,
  Input,
  Button,
  Alert,
  Card,
} from "@wbg/nexus";

export interface WizardFormData {
  orgName: string;
  adminEmail: string;
  department: string;
  envTier: string;
  cloudRegion: string;
  highAvailability: boolean;
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
      setCurrentStep((prev) => prev + 1 - 2);
    }
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;
    setIsSubmitting(true);
    setSubmissionError(null);

    try {
      await new Promise((res) => setTimeout(res, 800));
      onComplete?.(formData);
      alert("Tenant configuration successfully provisioned!");
    } catch (err: any) {
      setSubmissionError(err.message || "Failed to provision tenant resources. Please retry.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const progressPercentage = Math.round(((currentStep + 1) / steps.length) * 100);

  return (
    <div className="form-wizard-view">
      {/* 1. Header Slot */}
      <header className="nexus-page-header">
        <div className="nexus-page-header__meta">
          <span className="nexus-breadcrumb">Provisioning / Guided Setup</span>
          <h1 className="nexus-page-title">{wizardTitle}</h1>
          <p className="nexus-page-subtitle">{wizardSubtitle}</p>
        </div>
      </header>

      {/* 2. Visual Progress Indicator */}
      <div className="nexus-wizard-progress" role="progressbar" aria-valuenow={progressPercentage} aria-valuemin={0} aria-valuemax={100}>
        <div className="nexus-wizard-steps">
          {steps.map((step, idx) => (
            <div
              key={step.label}
              className={`nexus-wizard-step ${idx === currentStep ? "active" : idx < currentStep ? "completed" : ""}`}
            >
              <span className="nexus-wizard-step-number">{idx + 1}</span>
              <span className="nexus-wizard-step-label">{step.label}</span>
            </div>
          ))}
        </div>
        <Progress value={progressPercentage} className="nexus-progress-bar" />
      </div>

      {/* 3. Error Banner */}
      {submissionError && (
        <Alert variant="destructive" className="nexus-alert nexus-alert--danger">
          <strong>Provisioning Error:</strong> {submissionError}
        </Alert>
      )}

      {/* 4. Form Content Pane */}
      <Card className="nexus-card nexus-wizard-card">
        {currentStep === 0 && (
          <div className="nexus-form-pane">
            <h2 className="nexus-section-title">Organization Profile & Identity</h2>
            <div className="nexus-form-group">
              <label htmlFor="orgName" className="nexus-label">Organization Legal Name</label>
              <Input
                id="orgName"
                placeholder="e.g. Acme Health Corp"
                value={formData.orgName}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, orgName: e.target.value })}
              />
              {errors.orgName && <span className="nexus-field-error">{errors.orgName}</span>}
            </div>

            <div className="nexus-form-group">
              <label htmlFor="adminEmail" className="nexus-label">Primary Administrative Email</label>
              <Input
                id="adminEmail"
                type="email"
                placeholder="admin@enterprise.com"
                value={formData.adminEmail}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, adminEmail: e.target.value })}
              />
              {errors.adminEmail && <span className="nexus-field-error">{errors.adminEmail}</span>}
            </div>

            <div className="nexus-form-group">
              <label htmlFor="department" className="nexus-label">Primary Operational Unit</label>
              <select
                id="department"
                className="nexus-select"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              >
                <option value="engineering">Engineering & Infrastructure</option>
                <option value="finance">Finance & Accounting</option>
                <option value="clinical">Clinical & Healthcare Operations</option>
                <option value="legal">Legal & Corporate Compliance</option>
              </select>
            </div>
          </div>
        )}

        {currentStep === 1 && (
          <div className="nexus-form-pane">
            <h2 className="nexus-section-title">Cloud Infrastructure</h2>
            <div className="nexus-form-group">
              <label htmlFor="envTier" className="nexus-label">Deployment Tier</label>
              <select
                id="envTier"
                className="nexus-select"
                value={formData.envTier}
                onChange={(e) => setFormData({ ...formData, envTier: e.target.value })}
              >
                <option value="production">Production (Multi-AZ with Automated Failover)</option>
                <option value="staging">Staging / Pre-Release</option>
                <option value="development">Development Sandbox</option>
              </select>
            </div>

            <div className="nexus-form-group">
              <label htmlFor="cloudRegion" className="nexus-label">Primary Cloud Region</label>
              <select
                id="cloudRegion"
                className="nexus-select"
                value={formData.cloudRegion}
                onChange={(e) => setFormData({ ...formData, cloudRegion: e.target.value })}
              >
                <option value="eastus">US East (Virginia - Azure Primary)</option>
                <option value="westus">US West (Washington)</option>
                <option value="westeurope">West Europe (Amsterdam)</option>
              </select>
              {errors.cloudRegion && <span className="nexus-field-error">{errors.cloudRegion}</span>}
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="nexus-form-pane">
            <h2 className="nexus-section-title">Security & Access Governance</h2>
            <div className="nexus-form-group">
              <label htmlFor="auditRetentionDays" className="nexus-label">Audit Retention Schedule</label>
              <select
                id="auditRetentionDays"
                className="nexus-select"
                value={formData.auditRetentionDays}
                onChange={(e) => setFormData({ ...formData, auditRetentionDays: e.target.value })}
              >
                <option value="90">90 Days (Standard Development)</option>
                <option value="365">1 Year (SOX / HIPAA Baseline)</option>
                <option value="2555">7 Years (Financial / Institutional Grade)</option>
              </select>
            </div>

            <div className="nexus-form-group">
              <label htmlFor="ipWhitelist" className="nexus-label">Restricted Corporate IP CIDR Blocks</label>
              <Input
                id="ipWhitelist"
                placeholder="e.g. 198.51.100.0/24, 203.0.113.0/24"
                value={formData.ipWhitelist}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, ipWhitelist: e.target.value })}
              />
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="nexus-form-pane">
            <h2 className="nexus-section-title">Configuration Summary</h2>
            <p className="nexus-section-subtitle">
              Verify all operational parameters before initiating provisioning.
            </p>

            <div className="nexus-summary-grid">
              <div className="nexus-summary-item">
                <span className="nexus-summary-label">Organization:</span>
                <span className="nexus-summary-value">{formData.orgName || "Not specified"}</span>
              </div>
              <div className="nexus-summary-item">
                <span className="nexus-summary-label">Admin Email:</span>
                <span className="nexus-summary-value">{formData.adminEmail || "Not specified"}</span>
              </div>
              <div className="nexus-summary-item">
                <span className="nexus-summary-label">Deployment Tier:</span>
                <span className="nexus-summary-value">{formData.envTier.toUpperCase()}</span>
              </div>
              <div className="nexus-summary-item">
                <span className="nexus-summary-label">Cloud Region:</span>
                <span className="nexus-summary-value">{formData.cloudRegion}</span>
              </div>
              <div className="nexus-summary-item">
                <span className="nexus-summary-label">Log Retention:</span>
                <span className="nexus-summary-value">{formData.auditRetentionDays} Days</span>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* 5. Navigation Controls */}
      <footer className="nexus-wizard-footer">
        <Button variant="ghost" size="sm" onClick={onCancel || (() => alert("Cancelled"))}>
          Cancel
        </Button>

        <div className="nexus-wizard-actions">
          {currentStep > 0 && (
            <Button variant="outline" size="sm" onClick={handleBack} disabled={isSubmitting}>
              Back
            </Button>
          )}

          {currentStep < steps.length - 1 ? (
            <Button variant="default" size="sm" onClick={handleNext}>
              Next Step
            </Button>
          ) : (
            <Button variant="default" size="sm" onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting ? "Provisioning..." : "Confirm & Provision"}
            </Button>
          )}
        </div>
      </footer>
    </div>
  );
};

export default FormWizardRecipe;
