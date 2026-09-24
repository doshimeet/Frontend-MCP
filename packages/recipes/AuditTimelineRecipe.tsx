"use client";

import React, { useState, useMemo } from "react";
import {
  Table,
  Button,
  Tag,
  Input,
  Card,
} from "@wbg/nexus";

export interface TimelineEvent {
  id: string;
  timestamp: string;
  actor: string;
  actorRole: string;
  action: string;
  category: "Approval" | "Security" | "Disbursement" | "System";
  statusBefore?: string;
  statusAfter?: string;
  details: string;
}

export interface AuditTimelineRecipeProps {
  title?: string;
  description?: string;
  events?: TimelineEvent[];
  onExport?: () => void;
}

const DEFAULT_EVENTS: TimelineEvent[] = [
  {
    id: "EVT-8819",
    timestamp: "2026-09-24 14:15 UTC",
    actor: "Marcus Vance",
    actorRole: "Finance Controller",
    action: "Approved Tranche 2 Disbursement",
    category: "Approval",
    statusBefore: "In Review",
    statusAfter: "Approved",
    details: "Authorized release of $4.8M funds following milestone confirmation and environmental sign-off.",
  },
  {
    id: "EVT-8818",
    timestamp: "2026-09-24 11:30 UTC",
    actor: "System Sentinel",
    actorRole: "Automated Policy Engine",
    action: "Sanctions & Compliance Verification",
    category: "Security",
    statusBefore: "Pending",
    statusAfter: "Passed",
    details: "Automated check passed against global procurement sanctions database with 0 matches.",
  },
  {
    id: "EVT-8817",
    timestamp: "2026-09-23 16:45 UTC",
    actor: "Elena Rostova",
    actorRole: "Project Manager",
    action: "Submitted Supplemental Documentation",
    category: "Disbursement",
    statusBefore: "Draft",
    statusAfter: "In Review",
    details: "Attached revised contractor bill of materials and independent engineering verification.",
  },
  {
    id: "EVT-8816",
    timestamp: "2026-09-22 09:20 UTC",
    actor: "DevSecOps Pipeline",
    actorRole: "Azure DevOps Runner",
    action: "Secret Rotation & Key Vault Refresh",
    category: "System",
    details: "Automated monthly rotation of API keys across production and QA application slots.",
  },
];

export function AuditTimelineRecipe({
  title = "Institutional Audit & Governance Timeline",
  description = "Immutable chronological audit trail capturing security authorizations, disbursements, and policy state transitions.",
  events = DEFAULT_EVENTS,
  onExport,
}: AuditTimelineRecipeProps) {
  const [filterCategory, setFilterCategory] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const categories = ["All", "Approval", "Security", "Disbursement", "System"];

  const filteredEvents = useMemo(() => {
    return events.filter((evt) => {
      const matchesCat = filterCategory === "All" || evt.category === filterCategory;
      const matchesSearch =
        evt.action.toLowerCase().includes(searchQuery.toLowerCase()) ||
        evt.actor.toLowerCase().includes(searchQuery.toLowerCase()) ||
        evt.details.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCat && matchesSearch;
    });
  }, [events, filterCategory, searchQuery]);

  const getCategoryTag = (cat: TimelineEvent["category"]) => {
    switch (cat) {
      case "Approval":
        return <Tag type="success">Approval</Tag>;
      case "Security":
        return <Tag type="primary">Security</Tag>;
      case "Disbursement":
        return <Tag type="secondary">Disbursement</Tag>;
      case "System":
        return <Tag type="outline">System</Tag>;
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">{title}</h1>
          <p className="text-sm text-muted-foreground mt-1">{description}</p>
        </div>
        <Button variant="outline" size="sm" onClick={onExport}>
          Export Audit Log (CSV)
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Category Filter Pills */}
        <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-1" role="tablist">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setFilterCategory(cat)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                filterCategory === cat
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "bg-muted text-muted-foreground hover:text-foreground"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="w-full md:w-64">
          <Input
            role="searchbox"
            placeholder="Search audit actions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="text-sm"
          />
        </div>
      </div>

      {/* Timeline Stream */}
      <div className="relative border-l-2 border-border/80 ml-4 md:ml-6 pl-6 md:pl-8 space-y-8 py-2">
        {filteredEvents.length === 0 ? (
          <div className="py-12 text-center text-muted-foreground text-sm">
            No matching audit events recorded.
          </div>
        ) : (
          filteredEvents.map((evt) => {
            const isExpanded = expandedId === evt.id;
            return (
              <div key={evt.id} className="relative group">
                {/* Timeline Dot */}
                <div className="absolute -left-[31px] md:-left-[39px] top-1.5 h-3.5 w-3.5 rounded-full border-2 border-background bg-primary ring-4 ring-muted/50" />

                {/* Event Card */}
                <div className="p-4 rounded-lg border border-border bg-card shadow-sm space-y-2.5 transition-all hover:border-primary/50">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2.5">
                      <span className="font-semibold text-sm text-foreground">{evt.action}</span>
                      {getCategoryTag(evt.category)}
                    </div>
                    <span className="font-mono text-xs text-muted-foreground">{evt.timestamp}</span>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>Initiated by: <strong className="text-foreground">{evt.actor}</strong> ({evt.actorRole})</span>
                    {evt.statusBefore && evt.statusAfter && (
                      <span className="ml-auto flex items-center gap-1.5">
                        <span className="line-through opacity-70">{evt.statusBefore}</span>
                        <span>&rarr;</span>
                        <strong className="text-foreground font-semibold">{evt.statusAfter}</strong>
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-muted-foreground leading-relaxed pt-1">
                    {evt.details}
                  </p>

                  <div className="pt-2 flex items-center justify-between border-t border-border/40 text-xs">
                    <span className="font-mono text-[10px] text-muted-foreground">ID: {evt.id}</span>
                    <button
                      type="button"
                      onClick={() => setExpandedId(isExpanded ? null : evt.id)}
                      className="text-primary hover:underline font-medium"
                    >
                      {isExpanded ? "Hide Telemetry" : "View Telemetry & Diff"}
                    </button>
                  </div>

                  {isExpanded && (
                    <div className="mt-2 p-3 rounded bg-muted/30 border border-border font-mono text-xs text-muted-foreground overflow-x-auto">
                      <pre className="text-[11px] leading-tight">
{`{
  "event_id": "${evt.id}",
  "category": "${evt.category}",
  "actor": "${evt.actor}",
  "role": "${evt.actorRole}",
  "state_change": "${evt.statusBefore || 'N/A'} -> ${evt.statusAfter || 'N/A'}",
  "integrity_hash": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"
}`}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default AuditTimelineRecipe;
