"use client";

import React, { useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Tag,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Button,
} from "@wbg/design-system";

export interface KpiMetric {
  id: string;
  label: string;
  value: string;
  changePercent: string;
  isPositive: boolean;
  trendPeriod: string;
  status: "normal" | "warning" | "critical";
}

export interface ActivityLogItem {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  target: string;
  severity: "info" | "warning" | "critical";
}

export interface MetricsDashboardRecipeProps {
  dashboardTitle?: string;
  subtitle?: string;
  kpis?: KpiMetric[];
  recentActivities?: ActivityLogItem[];
  isLoading?: boolean;
  errorMessage?: string | null;
  onDateRangeChange?: (range: string) => void;
  onExportReport?: () => void;
}

const DEFAULT_KPIS: KpiMetric[] = [
  {
    id: "kpi-rev",
    label: "Total Operational Throughput",
    value: "$4,821,450",
    changePercent: "+14.2%",
    isPositive: true,
    trendPeriod: "vs previous 30 days",
    status: "normal",
  },
  {
    id: "kpi-users",
    label: "Active Enterprise Users",
    value: "18,420",
    changePercent: "+6.8%",
    isPositive: true,
    trendPeriod: "vs previous 30 days",
    status: "normal",
  },
  {
    id: "kpi-sla",
    label: "System SLA Compliance",
    value: "99.94%",
    changePercent: "+0.12%",
    isPositive: true,
    trendPeriod: "target: 99.90%",
    status: "normal",
  },
  {
    id: "kpi-sec",
    label: "Pending Compliance Reviews",
    value: "7",
    changePercent: "-2",
    isPositive: false,
    trendPeriod: "3 require immediate action",
    status: "warning",
  },
];

const DEFAULT_ACTIVITIES: ActivityLogItem[] = [
  {
    id: "act-01",
    timestamp: "2026-09-22 14:15",
    actor: "security.bot@enterprise.com",
    action: "SSL Certificate Rotated",
    target: "api.gateway.internal",
    severity: "info",
  },
  {
    id: "act-02",
    timestamp: "2026-09-22 13:42",
    actor: "sarah.connor@corp.internal",
    action: "Firewall Rule Altered",
    target: "db-cluster-primary",
    severity: "warning",
  },
  {
    id: "act-03",
    timestamp: "2026-09-22 11:20",
    actor: "david.miller@corp.internal",
    action: "User Role Escalation",
    target: "Group: Global Admins",
    severity: "critical",
  },
  {
    id: "act-04",
    timestamp: "2026-09-22 09:05",
    actor: "telemetry.worker@corp.internal",
    action: "Database Vacuum Completed",
    target: "analytics-warehouse-01",
    severity: "info",
  },
];

const ACTIVITY_HEADERS = [
  { key: "timestamp", header: "Timestamp" },
  { key: "actor", header: "Initiating Principal" },
  { key: "action", header: "Action Executed" },
  { key: "target", header: "Target Resource" },
  { key: "severity", header: "Severity" },
];

const SEVERITY_TAG_TYPES: Record<ActivityLogItem["severity"], "blue" | "magenta" | "red"> = {
  info: "blue",
  warning: "magenta",
  critical: "red",
};

export const MetricsDashboardRecipe: React.FC<MetricsDashboardRecipeProps> = ({
  dashboardTitle = "Operations & Security Intelligence",
  subtitle = "Real-time telemetry, capacity utilization, and high-priority audit events.",
  kpis = DEFAULT_KPIS,
  recentActivities = DEFAULT_ACTIVITIES,
  isLoading = false,
  errorMessage = null,
  onDateRangeChange,
  onExportReport,
}) => {
  const [selectedRange, setSelectedRange] = useState<string>("30d");

  const handleRangeSelect = (range: string) => {
    setSelectedRange(range);
    onDateRangeChange?.(range);
  };

  return (
    <div className="metrics-dashboard-container" style={{ width: "100%", padding: "1.5rem" }}>
      {/* 1. Header & Controls */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "1.5rem",
          flexWrap: "wrap",
          gap: "1rem",
        }}
      >
        <div>
          <h1 style={{ fontSize: "1.75rem", fontWeight: 600, margin: 0, color: "var(--cds-text-primary, #161616)" }}>
            {dashboardTitle}
          </h1>
          <p style={{ margin: "0.25rem 0 0", color: "var(--cds-text-secondary, #525252)", fontSize: "0.875rem" }}>
            {subtitle}
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <div
            role="group"
            aria-label="Select dashboard date range"
            style={{
              display: "flex",
              border: "1px solid var(--cds-border-subtle, #e0e0e0)",
              borderRadius: "4px",
              overflow: "hidden",
            }}
          >
            {["7d", "30d", "90d"].map((range) => (
              <button
                key={range}
                type="button"
                onClick={() => handleRangeSelect(range)}
                style={{
                  padding: "0.5rem 0.875rem",
                  fontSize: "0.8125rem",
                  border: "none",
                  cursor: "pointer",
                  background: selectedRange === range ? "var(--cds-interactive, #0f62fe)" : "var(--cds-layer, #ffffff)",
                  color: selectedRange === range ? "#ffffff" : "var(--cds-text-primary, #161616)",
                  fontWeight: selectedRange === range ? 600 : 400,
                  transition: "background 0.15s ease",
                }}
              >
                {range.toUpperCase()}
              </button>
            ))}
          </div>

          <Button kind="secondary" size="md" onClick={onExportReport || (() => alert("Exporting report..."))}>
            Export Audit Log
          </Button>
        </div>
      </div>

      {/* 2. Resilient Error Notification */}
      {errorMessage && (
        <div style={{ marginBottom: "1.5rem" }}>
          <InlineNotification
            kind="error"
            title="Telemetry service synchronization error"
            subtitle={errorMessage}
            aria-label="Dashboard telemetry error"
          />
        </div>
      )}

      {/* 3. Top-Line KPI Cards */}
      <Grid fullWidth style={{ padding: 0, marginBottom: "1.5rem" }}>
        {kpis.map((kpi) => (
          <Column key={kpi.id} lg={4} md={4} sm={4} style={{ marginBottom: "1rem" }}>
            <Tile
              style={{
                height: "100%",
                padding: "1.25rem",
                borderLeft:
                  kpi.status === "warning"
                    ? "4px solid var(--cds-support-warning, #f1c21b)"
                    : kpi.status === "critical"
                    ? "4px solid var(--cds-support-error, #da1e28)"
                    : "4px solid var(--cds-support-success, #24a148)",
                background: "var(--cds-layer, #ffffff)",
              }}
            >
              <div style={{ fontSize: "0.8125rem", color: "var(--cds-text-secondary, #525252)", marginBottom: "0.5rem" }}>
                {kpi.label}
              </div>
              {isLoading ? (
                <SkeletonText heading width="75%" />
              ) : (
                <div style={{ fontSize: "1.875rem", fontWeight: 700, lineHeight: 1.2, margin: "0.25rem 0" }}>
                  {kpi.value}
                </div>
              )}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  marginTop: "0.5rem",
                  fontSize: "0.75rem",
                  color: "var(--cds-text-secondary, #525252)",
                }}
              >
                <span
                  style={{
                    fontWeight: 600,
                    color: kpi.isPositive
                      ? "var(--cds-support-success, #24a148)"
                      : "var(--cds-support-error, #da1e28)",
                  }}
                >
                  {kpi.changePercent}
                </span>
                <span>{kpi.trendPeriod}</span>
              </div>
            </Tile>
          </Column>
        ))}
      </Grid>

      {/* 4. Telemetry & Recent Activity Table */}
      <div
        style={{
          background: "var(--cds-layer, #ffffff)",
          border: "1px solid var(--cds-border-subtle, #e0e0e0)",
          padding: "1.25rem",
        }}
      >
        <div style={{ marginBottom: "1rem" }}>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 600, margin: 0 }}>Recent Security & System Events</h2>
          <p style={{ margin: "0.25rem 0 0", color: "var(--cds-text-secondary, #525252)", fontSize: "0.8125rem" }}>
            Immutable audit record of all administrative operations performed in the last 24 hours.
          </p>
        </div>

        <DataTable rows={recentActivities} headers={ACTIVITY_HEADERS}>
          {({ rows, headers, getHeaderProps, getRowProps, getTableProps }) => (
            <Table {...getTableProps()} aria-label="Recent System Activities">
              <TableHead>
                <TableRow>
                  {headers.map((header) => (
                    <TableHeader {...getHeaderProps({ header })}>
                      {header.header}
                    </TableHeader>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  Array.from({ length: 4 }).map((_, idx) => (
                    <TableRow key={`skeleton-act-${idx}`}>
                      {headers.map((header) => (
                        <TableCell key={`skeleton-act-cell-${header.key}`}>
                          <SkeletonText paragraph={false} lineCount={1} />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                ) : rows.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={headers.length} style={{ textAlign: "center", padding: "2rem" }}>
                      No events recorded in this time range.
                    </TableCell>
                  </TableRow>
                ) : (
                  rows.map((row) => {
                    const original = recentActivities.find((a) => a.id === row.id);
                    return (
                      <TableRow {...getRowProps({ row })}>
                        {row.cells.map((cell) => {
                          if (cell.info.header === "severity" && original) {
                            return (
                              <TableCell key={cell.id}>
                                <Tag type={SEVERITY_TAG_TYPES[original.severity]} size="sm">
                                  {original.severity.toUpperCase()}
                                </Tag>
                              </TableCell>
                            );
                          }
                          if (cell.info.header === "target") {
                            return (
                              <TableCell key={cell.id}>
                                <code style={{ fontFamily: "monospace", fontSize: "0.8125rem" }}>{cell.value}</code>
                              </TableCell>
                            );
                          }
                          return <TableCell key={cell.id}>{cell.value}</TableCell>;
                        })}
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          )}
        </DataTable>
      </div>
    </div>
  );
};

export default MetricsDashboardRecipe;
