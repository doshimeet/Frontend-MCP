"use client";

import React, { useState } from "react";
import {
  Button,
  Input,
  Tag,
  Card,
  Tabs,
} from "@wbg/nexus";

export interface SettingsTabsRecipeProps {
  title?: string;
  description?: string;
  onSave?: (settings: any) => void;
}

export function SettingsTabsRecipe({
  title = "Enterprise Application & Governance Settings",
  description = "Manage portal configurations, security policies, API integrations, and notification channels.",
  onSave,
}: SettingsTabsRecipeProps) {
  const [activeTab, setActiveTab] = useState<"general" | "security" | "api" | "notifications">("general");
  const [isSaved, setIsSaved] = useState(false);

  // Form states
  const [appName, setAppName] = useState("World Bank Group Operations Portal");
  const [orgDomain, setOrgDomain] = useState("wbg-ops.worldbank.org");
  const [enforceMfa, setEnforceMfa] = useState(true);
  const [sessionTimeout, setSessionTimeout] = useState("30");
  const [apiKey, setApiKey] = useState("wbg_live_sec_994819a8f27b9");
  const [showKey, setShowKey] = useState(false);
  const [emailAlerts, setEmailAlerts] = useState(true);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaved(true);
    onSave?.({ appName, orgDomain, enforceMfa, sessionTimeout, emailAlerts });
    setTimeout(() => setIsSaved(false), 3000);
  };

  return (
    <div className="w-full max-w-5xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="border-b border-border pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">{title}</h1>
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>

      {/* Tabs Bar */}
      <div className="flex items-center gap-6 border-b border-border text-sm" role="tablist" aria-label="Settings categories">
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === "general"}
          aria-controls="panel-general"
          onClick={() => setActiveTab("general")}
          className={`pb-3 font-medium border-b-2 transition-colors ${
            activeTab === "general"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          General & Domain
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === "security"}
          aria-controls="panel-security"
          onClick={() => setActiveTab("security")}
          className={`pb-3 font-medium border-b-2 transition-colors ${
            activeTab === "security"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Security & Auth
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === "api"}
          aria-controls="panel-api"
          onClick={() => setActiveTab("api")}
          className={`pb-3 font-medium border-b-2 transition-colors ${
            activeTab === "api"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          API & Credentials
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === "notifications"}
          aria-controls="panel-notifications"
          onClick={() => setActiveTab("notifications")}
          className={`pb-3 font-medium border-b-2 transition-colors ${
            activeTab === "notifications"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Notifications
        </button>
      </div>

      {/* Feedback Alert */}
      {isSaved && (
        <div className="p-3.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-sm flex items-center justify-between">
          <span>Settings saved successfully. All operational nodes updated.</span>
          <Tag type="success">Active</Tag>
        </div>
      )}

      {/* Form Container */}
      <form onSubmit={handleSave} className="space-y-6">
        {/* Tab 1: General */}
        {activeTab === "general" && (
          <div id="panel-general" role="tabpanel" className="space-y-5">
            <div className="space-y-1.5">
              <label htmlFor="app-name" className="text-sm font-semibold text-foreground">
                Portal Application Name
              </label>
              <Input
                id="app-name"
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
                className="w-full text-sm"
              />
              <p className="text-xs text-muted-foreground">Displayed across headers and official email receipts.</p>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="domain" className="text-sm font-semibold text-foreground">
                Primary Host Domain
              </label>
              <Input
                id="domain"
                value={orgDomain}
                onChange={(e) => setOrgDomain(e.target.value)}
                className="w-full text-sm"
              />
            </div>
          </div>
        )}

        {/* Tab 2: Security */}
        {activeTab === "security" && (
          <div id="panel-security" role="tabpanel" className="space-y-5">
            <div className="flex items-center justify-between p-4 rounded-md border border-border bg-card">
              <div>
                <div className="text-sm font-semibold text-foreground">Enforce Microsoft Entra ID MFA</div>
                <div className="text-xs text-muted-foreground">Mandate multi-factor authentication for all portal accounts.</div>
              </div>
              <Button
                type="button"
                variant={enforceMfa ? "primary" : "outline"}
                size="sm"
                onClick={() => setEnforceMfa(!enforceMfa)}
              >
                {enforceMfa ? "Enabled" : "Disabled"}
              </Button>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="timeout" className="text-sm font-semibold text-foreground">
                Session Inactivity Timeout (Minutes)
              </label>
              <Input
                id="timeout"
                type="number"
                value={sessionTimeout}
                onChange={(e) => setSessionTimeout(e.target.value)}
                className="w-32 text-sm"
              />
            </div>
          </div>
        )}

        {/* Tab 3: API & Credentials */}
        {activeTab === "api" && (
          <div id="panel-api" role="tabpanel" className="space-y-5">
            <div className="space-y-1.5">
              <label htmlFor="api-key" className="text-sm font-semibold text-foreground">
                Live Environment API Secret
              </label>
              <div className="flex items-center gap-3">
                <Input
                  id="api-key"
                  type={showKey ? "text" : "password"}
                  value={apiKey}
                  readOnly
                  className="font-mono text-sm flex-1 bg-muted/30"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowKey(!showKey)}
                >
                  {showKey ? "Hide" : "Reveal"}
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setApiKey(`wbg_live_sec_${Math.random().toString(36).substring(2, 15)}`)}
                >
                  Regenerate
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">Use this key in Authorization headers for server-to-server sync.</p>
            </div>
          </div>
        )}

        {/* Tab 4: Notifications */}
        {activeTab === "notifications" && (
          <div id="panel-notifications" role="tabpanel" className="space-y-5">
            <div className="flex items-center justify-between p-4 rounded-md border border-border bg-card">
              <div>
                <div className="text-sm font-semibold text-foreground">Immediate Audit & Compliance Alerts</div>
                <div className="text-xs text-muted-foreground">Dispatch instant notifications on high-value grant approvals.</div>
              </div>
              <Button
                type="button"
                variant={emailAlerts ? "primary" : "outline"}
                size="sm"
                onClick={() => setEmailAlerts(!emailAlerts)}
              >
                {emailAlerts ? "Active" : "Muted"}
              </Button>
            </div>
          </div>
        )}

        {/* Action Bar */}
        <div className="flex items-center justify-end gap-3 pt-6 border-t border-border">
          <Button type="button" variant="outline" size="sm">
            Cancel
          </Button>
          <Button type="submit" variant="primary" size="sm">
            Save Preferences
          </Button>
        </div>
      </form>
    </div>
  );
}

export default SettingsTabsRecipe;
