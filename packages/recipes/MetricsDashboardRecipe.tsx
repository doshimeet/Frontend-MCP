"use client";

import React, { useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
  Button,
  Tag,
} from "@wbg/nexus";

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
    action: "Security Role Escalated",
    target: "iam.roles.admin",
    severity: "warning",
  },
  {
    id: "act-03",
    timestamp: "2026-09-22 11:20",
    actor: "data.pipeline@enterprise.com",
    action: "ETL Ingestion Completed",
    target: "dw.analytics.gold",
    severity: "info",
  },
  {
    id: "act-04",
    timestamp: "2026-09-22 09:05",
    actor: "audit.sentinel@enterprise.com",
    action: "Anomalous Login Pattern Detected",
    target: "auth.sso.external",
    severity: "critical",
  },
];

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
    <div className="metrics-dashboard-view">
      {/* 1. Header Slot */}
      <header className="nexus-page-header">
        <div className="nexus-page-header__meta">
          <span className="nexus-breadcrumb">Global Operations / Institutional Telemetry</span>
          <h1 className="nexus-page-title">{dashboardTitle}</h1>
          <p className="nexus-page-subtitle">{subtitle}</p>
        </div>

        <div className="nexus-page-header__actions">
          <div role="group" aria-label="Select dashboard date range" className="nexus-btn-group">
            {["7d", "30d", "90d"].map((range) => (
              <button
                key={range}
                type="button"
                className={`nexus-btn-segment ${selectedRange === range ? "active" : ""}`}
                onClick={() => handleRangeSelect(range)}
              >
                {range.toUpperCase()}
              </button>
            ))}
          </div>

          <Button variant="outline" size="sm" onClick={onExportReport || (() => alert("Exporting report..."))}>
            Export Audit Log
          </Button>
        </div>
      </header>

      {/* 2. Error State */}
      {errorMessage && (
        <div className="nexus-alert nexus-alert--danger" role="alert">
          <strong>Telemetry Synchronization Error:</strong> {errorMessage}
        </div>
      )}

      {/* 3. Composable KPI Grid Slot */}
      <section className="nexus-kpi-grid" aria-label="Key Performance Indicators">
        {kpis.map((kpi) => (
          <div key={kpi.id} className="nexus-kpi-card">
            <div className="nexus-kpi-header">
              <span className="nexus-kpi-label">{kpi.label}</span>
              {kpi.status !== "normal" && (
                <span className={`nexus-badge nexus-badge--${kpi.status === "critical" ? "danger" : "warning"}`}>
                  {kpi.status}
                </span>
              )}
            </div>
            <div className="nexus-kpi-value">{isLoading ? "..." : kpi.value}</div>
            <div className="nexus-kpi-subtext">
              <span className={kpi.isPositive ? "nexus-trend-up" : "nexus-trend-down"}>
                {kpi.isPositive ? "↑ " : "↓ "}
                {kpi.changePercent}
              </span>
              <span>{kpi.trendPeriod}</span>
            </div>
          </div>
        ))}
      </section>

      {/* 4. Data View Slot (Activity Log) */}
      <section className="nexus-data-section">
        <Card className="nexus-card">
          <CardHeader>
            <div className="nexus-section-header">
              <div>
                <CardTitle>Recent Institutional Events</CardTitle>
                <p className="nexus-section-subtitle">Real-time audit telemetry across core enterprise services</p>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            {recentActivities.length === 0 ? (
              <div className="nexus-empty-state">
                <h3 className="nexus-empty-state__title">No events recorded</h3>
                <p className="nexus-empty-state__description">
                  There are no recent audit activities recorded for the selected time range.
                </p>
              </div>
            ) : (
              <div className="nexus-table-container">
                <Table className="nexus-table">
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>Actor</TableHead>
                      <TableHead>Action</TableHead>
                      <TableHead>Target Resource</TableHead>
                      <TableHead className="nexus-col-number">Severity</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {recentActivities.map((act) => (
                      <TableRow key={act.id}>
                        <TableCell className="nexus-font-mono">{act.timestamp}</TableCell>
                        <TableCell className="nexus-font-medium">{act.actor}</TableCell>
                        <TableCell>{act.action}</TableCell>
                        <TableCell className="nexus-font-mono">{act.target}</TableCell>
                        <TableCell className="nexus-col-number">
                          <Tag
                            type={
                              act.severity === "critical"
                                ? "red"
                                : act.severity === "warning"
                                ? "magenta"
                                : "blue"
                            }
                          >
                            {act.severity.toUpperCase()}
                          </Tag>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </section>
    </div>
  );
};

export default MetricsDashboardRecipe;
