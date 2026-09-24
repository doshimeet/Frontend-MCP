"use client";

import React, { useState, useMemo } from "react";
import {
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Button,
  Tag,
  Input,
  Card,
  Tabs,
  Sheet,
} from "@wbg/design-system";

export interface MasterDetailItem {
  id: string;
  referenceNumber: string;
  title: string;
  category: string;
  status: "submitted" | "in_review" | "approved" | "rejected";
  amount: string;
  submittedBy: string;
  submissionDate: string;
  description: string;
  riskRating: "Low" | "Medium" | "High";
  approvers: string[];
}

export interface MasterDetailRecipeProps {
  title?: string;
  description?: string;
  items?: MasterDetailItem[];
  isLoading?: boolean;
  onApprove?: (id: string) => void;
  onReject?: (id: string) => void;
}

const DEFAULT_ITEMS: MasterDetailItem[] = [
  {
    id: "REC-2026-001",
    referenceNumber: "WBG-PROC-4819",
    title: "Regional Solar Grid Infrastructure Tender",
    category: "Procurement",
    status: "in_review",
    amount: "$12,450,000",
    submittedBy: "Elena Rostova (Energy Division)",
    submissionDate: "2026-09-18",
    description: "Multi-jurisdiction solar PV deployment across 14 municipal substations.",
    riskRating: "Medium",
    approvers: ["Director General", "Regional Compliance Lead"],
  },
  {
    id: "REC-2026-002",
    referenceNumber: "WBG-DISB-9902",
    title: "Clean Water Sanitation Tranche 2",
    category: "Disbursement",
    status: "approved",
    amount: "$4,800,000",
    submittedBy: "Marcus Chen (Sanitation Taskforce)",
    submissionDate: "2026-09-12",
    description: "Sub-grant disbursement following Phase 1 audit sign-off and milestone verification.",
    riskRating: "Low",
    approvers: ["Finance Officer", "Country Director"],
  },
  {
    id: "REC-2026-003",
    referenceNumber: "WBG-PROC-5104",
    title: "Rural Healthcare Telemetry Expansion",
    category: "Procurement",
    status: "submitted",
    amount: "$1,750,000",
    submittedBy: "Amina Diallo (Health Operations)",
    submissionDate: "2026-09-22",
    description: "Satellite connectivity and diagnostics hardware rollout for remote clinics.",
    riskRating: "Low",
    approvers: ["Health Lead"],
  },
  {
    id: "REC-2026-004",
    referenceNumber: "WBG-DISB-7721",
    title: "Coastal Barrier Reinforcement Grant",
    category: "Disbursement",
    status: "rejected",
    amount: "$6,100,000",
    submittedBy: "David Okafor (Climate Adaptation)",
    submissionDate: "2026-08-30",
    description: "Reimbursement claim flagged during environmental compliance cross-check.",
    riskRating: "High",
    approvers: ["Environmental Audit Board"],
  },
];

export function MasterDetailRecipe({
  title = "Operations & Case Review Inspector",
  description = "Split-pane master-detail workflow with real-time detail inspection and decision actions.",
  items = DEFAULT_ITEMS,
  isLoading = false,
  onApprove,
  onReject,
}: MasterDetailRecipeProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedId, setSelectedId] = useState<string>(items[0]?.id || "");
  const [activeTab, setActiveTab] = useState<"overview" | "approvals" | "audit">("overview");

  const filteredItems = useMemo(() => {
    return items.filter((item) =>
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.referenceNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.category.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [items, searchQuery]);

  const selectedItem = useMemo(() => {
    return items.find((i) => i.id === selectedId) || items[0] || null;
  }, [items, selectedId]);

  const getStatusTag = (status: MasterDetailItem["status"]) => {
    switch (status) {
      case "approved":
        return <Tag type="success">Approved</Tag>;
      case "in_review":
        return <Tag type="primary">In Review</Tag>;
      case "submitted":
        return <Tag type="secondary">Submitted</Tag>;
      case "rejected":
        return <Tag type="danger">Rejected</Tag>;
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">{title}</h1>
          <p className="text-sm text-muted-foreground mt-1">{description}</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" size="sm" onClick={() => setSelectedId(items[0]?.id || "")}>
            Reset Selection
          </Button>
          <Button variant="primary" size="sm">
            Export Records
          </Button>
        </div>
      </div>

      {/* Split Pane Container */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[640px]">
        {/* Left Master List (5 cols on lg) */}
        <div className="lg:col-span-5 flex flex-col space-y-4 border border-border rounded-lg p-4 bg-card shadow-sm">
          <div className="flex items-center justify-between gap-2">
            <Input
              role="searchbox"
              aria-label="Search cases"
              placeholder="Search reference, title..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full text-sm"
            />
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 pr-1" role="list" aria-label="Cases list">
            {isLoading ? (
              <div className="space-y-3 p-4">
                {[1, 2, 3, 4].map((n) => (
                  <div key={n} className="h-16 bg-muted/60 animate-pulse rounded-md" />
                ))}
              </div>
            ) : filteredItems.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground text-sm">
                No matching records found.
              </div>
            ) : (
              filteredItems.map((item) => {
                const isSelected = item.id === selectedId;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSelectedId(item.id)}
                    className={`w-full text-left p-3.5 rounded-md transition-all border ${
                      isSelected
                        ? "bg-accent text-accent-foreground border-primary shadow-sm"
                        : "hover:bg-muted/50 border-transparent text-foreground"
                    }`}
                    aria-selected={isSelected}
                  >
                    <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                      <span className="font-mono font-medium">{item.referenceNumber}</span>
                      {getStatusTag(item.status)}
                    </div>
                    <div className="font-medium text-sm line-clamp-1 mb-1">{item.title}</div>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{item.category}</span>
                      <span className="font-semibold text-foreground">{item.amount}</span>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Right Detail Inspector (7 cols on lg) */}
        <div className="lg:col-span-7 flex flex-col border border-border rounded-lg p-6 bg-card shadow-sm">
          {selectedItem ? (
            <div className="space-y-6">
              {/* Detail Header */}
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 border-b border-border pb-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-muted text-muted-foreground">
                      {selectedItem.referenceNumber}
                    </span>
                    {getStatusTag(selectedItem.status)}
                    <span className="text-xs px-2 py-0.5 rounded bg-secondary text-secondary-foreground font-medium">
                      Risk: {selectedItem.riskRating}
                    </span>
                  </div>
                  <h2 className="text-xl font-bold text-foreground">{selectedItem.title}</h2>
                  <p className="text-xs text-muted-foreground mt-1">
                    Submitted by {selectedItem.submittedBy} on {selectedItem.submissionDate}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onReject?.(selectedItem.id)}
                  >
                    Reject
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => onApprove?.(selectedItem.id)}
                  >
                    Approve Case
                  </Button>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="flex items-center gap-4 border-b border-border text-sm" role="tablist">
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTab === "overview"}
                  onClick={() => setActiveTab("overview")}
                  className={`pb-2.5 font-medium border-b-2 transition-colors ${
                    activeTab === "overview"
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Overview & Scope
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTab === "approvals"}
                  onClick={() => setActiveTab("approvals")}
                  className={`pb-2.5 font-medium border-b-2 transition-colors ${
                    activeTab === "approvals"
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Approval Chain ({selectedItem.approvers.length})
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTab === "audit"}
                  onClick={() => setActiveTab("audit")}
                  className={`pb-2.5 font-medium border-b-2 transition-colors ${
                    activeTab === "audit"
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Audit History
                </button>
              </div>

              {/* Tab Contents */}
              {activeTab === "overview" && (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-xs uppercase tracking-wider text-muted-foreground font-semibold mb-1.5">
                      Case Summary
                    </h3>
                    <p className="text-sm text-foreground leading-relaxed bg-muted/30 p-3.5 rounded-md border border-border/50">
                      {selectedItem.description}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-2">
                    <div className="p-3 bg-muted/20 border border-border rounded-md">
                      <div className="text-xs text-muted-foreground">Authorized Amount</div>
                      <div className="text-lg font-bold text-foreground mt-0.5">{selectedItem.amount}</div>
                    </div>
                    <div className="p-3 bg-muted/20 border border-border rounded-md">
                      <div className="text-xs text-muted-foreground">Category Domain</div>
                      <div className="text-lg font-bold text-foreground mt-0.5">{selectedItem.category}</div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "approvals" && (
                <div className="space-y-3">
                  <h3 className="text-xs uppercase tracking-wider text-muted-foreground font-semibold mb-2">
                    Designated Signatories
                  </h3>
                  <div className="space-y-2">
                    {selectedItem.approvers.map((approver, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 rounded-md bg-muted/20 border border-border text-sm"
                      >
                        <span className="font-medium text-foreground">{approver}</span>
                        <Tag type="primary">Pending Review</Tag>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === "audit" && (
                <div className="space-y-3 text-xs text-muted-foreground">
                  <div className="border-l-2 border-border pl-3 space-y-2">
                    <div>
                      <span className="font-semibold text-foreground">Record Created</span>
                      <p className="text-muted-foreground">{selectedItem.submissionDate} by {selectedItem.submittedBy}</p>
                    </div>
                    <div>
                      <span className="font-semibold text-foreground">Initial Validation</span>
                      <p className="text-muted-foreground">Passed automated policy checks and risk classification.</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
              Select a case record to inspect details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MasterDetailRecipe;
