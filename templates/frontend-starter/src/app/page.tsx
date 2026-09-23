"use client";

import React, { useState } from "react";
import {
  Grid,
  Column,
  Tile,
  Button,
  Tag,
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  TableToolbar,
  TableToolbarContent,
  TableToolbarSearch,
  Pagination,
  Modal,
  TextInput,
  Select,
  SelectItem,
  InlineNotification,
} from "@carbon/react";

interface ServiceRecord {
  id: string;
  name: string;
  category: string;
  status: "healthy" | "warning" | "deploying" | "offline";
  latency: string;
  uptime: string;
}

const SAMPLE_RECORDS: ServiceRecord[] = [
  {
    id: "SRV-01",
    name: "Enterprise FastMCP Gateway",
    category: "AI Runtime",
    status: "healthy",
    latency: "18ms",
    uptime: "99.98%",
  },
  {
    id: "SRV-02",
    name: "Design Tokens Streamer (DTCG)",
    category: "Design System",
    status: "healthy",
    latency: "12ms",
    uptime: "99.99%",
  },
  {
    id: "SRV-03",
    name: "Azure DevOps Scaffolding Agent",
    category: "CI/CD & DevOps",
    status: "deploying",
    latency: "145ms",
    uptime: "99.85%",
  },
  {
    id: "SRV-04",
    name: "Storybook Catalog Validator",
    category: "UI Verification",
    status: "healthy",
    latency: "34ms",
    uptime: "99.92%",
  },
  {
    id: "SRV-05",
    name: "Playwright Headless Edge Verifier",
    category: "Quality Assurance",
    status: "warning",
    latency: "320ms",
    uptime: "98.90%",
  },
];

const TABLE_HEADERS = [
  { key: "name", header: "Service Name" },
  { key: "category", header: "Architecture Tier" },
  { key: "status", header: "Operational State" },
  { key: "latency", header: "p95 Latency" },
  { key: "uptime", header: "30-Day SLA" },
];

const STATUS_TAGS: Record<ServiceRecord["status"], "green" | "blue" | "magenta" | "red"> = {
  healthy: "green",
  deploying: "blue",
  warning: "magenta",
  offline: "red",
};

export default function WelcomeDashboardPage() {
  const [records, setRecords] = useState<ServiceRecord[]>(SAMPLE_RECORDS);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [newServiceName, setNewServiceName] = useState<string>("");
  const [newServiceCategory, setNewServiceCategory] = useState<string>("Core Services");
  const [notification, setNotification] = useState<{ message: string; kind: "success" | "info" } | null>(null);

  const filteredRecords = records.filter(
    (r) =>
      r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateService = () => {
    if (!newServiceName.trim()) return;

    const newRecord: ServiceRecord = {
      id: `SRV-0${records.length + 1}`,
      name: newServiceName.trim(),
      category: newServiceCategory,
      status: "healthy",
      latency: "22ms",
      uptime: "100.0%",
    };

    setRecords([newRecord, ...records]);
    setNewServiceName("");
    setIsModalOpen(false);
    setNotification({
      message: `Service "${newRecord.name}" successfully registered into enterprise catalog.`,
      kind: "success",
    });
  };

  return (
    <div className="welcome-dashboard" style={{ maxWidth: "1280px", margin: "0 auto" }}>
      {/* 1. Hero Section */}
      <section id="welcome-hero" style={{ marginBottom: "2rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.5rem" }}>
              <h1 style={{ fontSize: "2rem", fontWeight: 700, margin: 0 }}>
                Enterprise Digital Platform
              </h1>
              <Tag type="cool-gray" size="md">Next.js 14 App Router</Tag>
              <Tag type="green" size="md">IBM Carbon v11</Tag>
            </div>
            <p style={{ fontSize: "1rem", color: "var(--cds-text-secondary, #525252)", margin: 0, maxWidth: "720px" }}>
              AI-Native frontend starter kit wired with strict DTCG design tokens, pre-composed page recipes,
              and bidirectional FastMCP orchestration.
            </p>
          </div>

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <Button
              id="new-record-btn"
              kind="primary"
              size="md"
              onClick={() => setIsModalOpen(true)}
            >
              + Register Service
            </Button>
            <Button
              kind="secondary"
              size="md"
              onClick={() => window.open("https://react.carbondesignsystem.com", "_blank")}
            >
              Carbon Storybook ↗
            </Button>
          </div>
        </div>
      </section>

      {/* 2. Notification Banner */}
      {notification && (
        <div style={{ marginBottom: "1.5rem" }}>
          <InlineNotification
            kind={notification.kind}
            title="System Alert"
            subtitle={notification.message}
            onCloseButtonClick={() => setNotification(null)}
          />
        </div>
      )}

      {/* 3. KPI Telemetry Grid */}
      <section id="metrics-grid" style={{ marginBottom: "2.5rem" }}>
        <Grid fullWidth style={{ padding: 0 }}>
          <Column lg={3} md={4} sm={4} style={{ marginBottom: "1rem" }}>
            <Tile style={{ padding: "1.25rem", height: "100%", background: "var(--cds-layer, #ffffff)" }}>
              <div style={{ fontSize: "0.8125rem", color: "var(--cds-text-secondary, #525252)" }}>MCP Server Engine</div>
              <div style={{ fontSize: "1.75rem", fontWeight: 700, margin: "0.5rem 0" }}>Online</div>
              <div style={{ fontSize: "0.75rem", color: "var(--cds-support-success, #24a148)", fontWeight: 600 }}>
                ● stdio & SSE Dual-Transport
              </div>
            </Tile>
          </Column>

          <Column lg={3} md={4} sm={4} style={{ marginBottom: "1rem" }}>
            <Tile style={{ padding: "1.25rem", height: "100%", background: "var(--cds-layer, #ffffff)" }}>
              <div style={{ fontSize: "0.8125rem", color: "var(--cds-text-secondary, #525252)" }}>Design Tokens (DTCG)</div>
              <div style={{ fontSize: "1.75rem", fontWeight: 700, margin: "0.5rem 0" }}>2 Themes</div>
              <div style={{ fontSize: "0.75rem", color: "var(--cds-text-secondary, #525252)" }}>
                enterprise-dark & warm-sage
              </div>
            </Tile>
          </Column>

          <Column lg={3} md={4} sm={4} style={{ marginBottom: "1rem" }}>
            <Tile style={{ padding: "1.25rem", height: "100%", background: "var(--cds-layer, #ffffff)" }}>
              <div style={{ fontSize: "0.8125rem", color: "var(--cds-text-secondary, #525252)" }}>Canonical Page Recipes</div>
              <div style={{ fontSize: "1.75rem", fontWeight: 700, margin: "0.5rem 0" }}>3 Patterns</div>
              <div style={{ fontSize: "0.75rem", color: "var(--cds-text-secondary, #525252)" }}>
                CRUD Table, Dashboard, Wizard
              </div>
            </Tile>
          </Column>

          <Column lg={3} md={4} sm={4} style={{ marginBottom: "1rem" }}>
            <Tile style={{ padding: "1.25rem", height: "100%", background: "var(--cds-layer, #ffffff)" }}>
              <div style={{ fontSize: "0.8125rem", color: "var(--cds-text-secondary, #525252)" }}>Accessibility Standard</div>
              <div style={{ fontSize: "1.75rem", fontWeight: 700, margin: "0.5rem 0" }}>WCAG 2.1 AA</div>
              <div style={{ fontSize: "0.75rem", color: "var(--cds-support-success, #24a148)", fontWeight: 600 }}>
                100% Contrast & Focus Verified
              </div>
            </Tile>
          </Column>
        </Grid>
      </section>

      {/* 4. Live Carbon DataTable Section */}
      <section id="crud-datatable" style={{ marginBottom: "2.5rem" }}>
        <div style={{ marginBottom: "1rem" }}>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 600, margin: 0 }}>Registered Architecture Services</h2>
          <p style={{ fontSize: "0.875rem", color: "var(--cds-text-secondary, #525252)", margin: "0.25rem 0 0" }}>
            Live Carbon DataTable demonstrating sorting, client-side filtering, accessible status badges, and zero magic CSS.
          </p>
        </div>

        <DataTable rows={filteredRecords} headers={TABLE_HEADERS} isSortable>
          {({ rows, headers, getHeaderProps, getRowProps, getTableProps }) => (
            <div style={{ background: "var(--cds-layer, #ffffff)", border: "1px solid var(--cds-border-subtle, #e0e0e0)" }}>
              <TableToolbar aria-label="Services table toolbar">
                <TableToolbarContent>
                  <TableToolbarSearch
                    persistent
                    placeholder="Filter services by name or tier..."
                    value={searchQuery}
                    onChange={(_evt: any, val?: string) => setSearchQuery(val ?? "")}
                    id="service-search-input"
                  />
                </TableToolbarContent>
              </TableToolbar>

              <Table {...getTableProps()} aria-label="Enterprise Services Table">
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
                  {rows.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={headers.length} style={{ textAlign: "center", padding: "2rem" }}>
                        No matching services found for "{searchQuery}".
                      </TableCell>
                    </TableRow>
                  ) : (
                    rows.map((row) => {
                      const item = records.find((r) => r.id === row.id);
                      return (
                        <TableRow {...getRowProps({ row })}>
                          {row.cells.map((cell) => {
                            if (cell.info.header === "status" && item) {
                              return (
                                <TableCell key={cell.id}>
                                  <Tag type={STATUS_TAGS[item.status]} size="sm">
                                    {item.status.toUpperCase()}
                                  </Tag>
                                </TableCell>
                              );
                            }
                            if (cell.info.header === "latency") {
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

              <Pagination
                backwardText="Previous page"
                forwardText="Next page"
                itemsPerPageText="Items per page:"
                page={1}
                pageNumberText="Page Number"
                pageSize={10}
                pageSizes={[10, 25, 50]}
                totalItems={filteredRecords.length}
                onChange={() => {}}
              />
            </div>
          )}
        </DataTable>
      </section>

      {/* 5. Modal: Register New Service */}
      <Modal
        open={isModalOpen}
        modalHeading="Register New Architectural Service"
        primaryButtonText="Confirm Registration"
        secondaryButtonText="Cancel"
        onRequestClose={() => setIsModalOpen(false)}
        onRequestSubmit={handleCreateService}
      >
        <div style={{ paddingTop: "1rem" }}>
          <p style={{ fontSize: "0.875rem", color: "var(--cds-text-secondary, #525252)", marginBottom: "1.5rem" }}>
            Provide the service details to register it with the enterprise catalog and generate corresponding routes.
          </p>

          <TextInput
            id="modal-service-name"
            labelText="Service Name"
            placeholder="e.g. Identity Authorization Broker"
            value={newServiceName}
            onChange={(e) => setNewServiceName(e.target.value)}
            style={{ marginBottom: "1.25rem" }}
          />

          <Select
            id="modal-service-category"
            labelText="Architectural Category"
            value={newServiceCategory}
            onChange={(e) => setNewServiceCategory(e.target.value)}
          >
            <SelectItem value="Core Services" text="Core Services" />
            <SelectItem value="AI Runtime" text="AI Runtime" />
            <SelectItem value="Design System" text="Design System" />
            <SelectItem value="Data & Analytics" text="Data & Analytics" />
            <SelectItem value="Security & Compliance" text="Security & Compliance" />
          </Select>
        </div>
      </Modal>
    </div>
  );
}
