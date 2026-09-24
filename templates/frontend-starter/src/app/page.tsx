"use client";

import React, { useState } from "react";
import Link from "next/link";

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

  const handleCreateService = (e: React.FormEvent) => {
    e.preventDefault();
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
    <div className="welcome-dashboard max-w-7xl mx-auto space-y-8">
      {/* 1. Hero Section */}
      <section id="welcome-hero" className="border-b border-slate-200 pb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <h1 className="text-2xl md:text-3xl font-bold text-[#002244] tracking-tight">
                World Bank Group Operations Portal
              </h1>
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-800 border border-slate-200">
                Next.js 14 App Router
              </span>
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                Tailwind CSS & Nexus Tokens
              </span>
            </div>
            <p className="text-sm md:text-base text-slate-600 max-w-3xl">
              AI-Native enterprise platform pre-wired with strict DTCG design tokens, Taste Skill & Impeccable
              quality gates, and autonomous multi-environment detection.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              id="new-record-btn"
              type="button"
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2 text-xs font-semibold text-white bg-[#0071bc] hover:bg-[#005a96] rounded transition-colors shadow-sm"
            >
              + Register Service
            </button>
            <Link
              href="/projects"
              className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-50 transition-colors shadow-sm"
            >
              Projects Directory →
            </Link>
          </div>
        </div>
      </section>

      {/* 2. Notification Banner */}
      {notification && (
        <div
          role="alert"
          className="flex items-center justify-between p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-sm"
        >
          <div className="flex items-center gap-2">
            <span aria-hidden="true">✓</span>
            <span className="font-semibold">Success:</span>
            <span>{notification.message}</span>
          </div>
          <button
            type="button"
            onClick={() => setNotification(null)}
            className="text-emerald-700 hover:text-emerald-900 font-bold text-xs"
            aria-label="Dismiss notification"
          >
            ✕
          </button>
        </div>
      )}

      {/* 3. KPI Telemetry Grid */}
      <section id="metrics-grid" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            MCP Server Engine
          </div>
          <div className="text-2xl font-bold text-[#002244] mt-2">Online</div>
          <div className="text-xs text-emerald-700 font-semibold mt-1 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
            stdio & SSE Dual-Transport
          </div>
        </div>

        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            Design Tokens (DTCG)
          </div>
          <div className="text-2xl font-bold text-[#002244] mt-2">DTCG Tokens</div>
          <div className="text-xs text-slate-500 mt-1">wbg-enterprise & tokens.json</div>
        </div>

        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            Canonical Page Recipes
          </div>
          <div className="text-2xl font-bold text-[#002244] mt-2">6 Recipes</div>
          <div className="text-xs text-slate-500 mt-1">Table, Dashboard, Wizard, Inspector</div>
        </div>

        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            Accessibility Standard
          </div>
          <div className="text-2xl font-bold text-emerald-600 mt-2">WCAG 2.1 AA</div>
          <div className="text-xs text-emerald-700 font-semibold mt-1">
            100% Contrast & Focus Verified
          </div>
        </div>
      </section>

      {/* 4. Live Architecture Services Table */}
      <section id="crud-datatable" className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-[#002244]">Registered Architecture Services</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              High-density service registry with zero ghost dependencies, styled cleanly with Tailwind CSS.
            </p>
          </div>

          <div className="w-full sm:w-72">
            <input
              id="service-search-input"
              type="text"
              placeholder="Filter services by name or tier..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-1.5 text-xs border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-[#0071bc]"
              aria-label="Filter architecture services"
            />
          </div>
        </div>

        <div className="nexus-table-container bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="nexus-table w-full text-left text-sm" aria-label="Enterprise Services Table">
              <thead className="bg-slate-50 border-b border-slate-200 text-xs uppercase font-semibold text-slate-600 tracking-wider">
                <tr>
                  <th className="px-4 py-3">Service ID</th>
                  <th className="px-4 py-3">Service Name</th>
                  <th className="px-4 py-3">Architecture Tier</th>
                  <th className="px-4 py-3">Operational State</th>
                  <th className="px-4 py-3 text-right">p95 Latency</th>
                  <th className="px-4 py-3 text-right">30-Day SLA</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {filteredRecords.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-slate-500">
                      No matching services found for &quot;{searchQuery}&quot;.
                    </td>
                  </tr>
                ) : (
                  filteredRecords.map((item) => (
                    <tr key={item.id} className="hover:bg-blue-50/30 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs font-semibold text-[#0071bc]">
                        {item.id}
                      </td>
                      <td className="px-4 py-3 font-medium text-slate-900">{item.name}</td>
                      <td className="px-4 py-3 text-slate-600 text-xs">{item.category}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                            item.status === "healthy"
                              ? "bg-emerald-100 text-emerald-800"
                              : item.status === "warning"
                              ? "bg-amber-100 text-amber-900"
                              : item.status === "deploying"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {item.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-xs text-slate-700 tabular-nums">
                        {item.latency}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-xs font-medium text-slate-900 tabular-nums">
                        {item.uptime}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="px-4 py-3 bg-slate-50 border-t border-slate-200 text-xs text-slate-500 flex items-center justify-between">
            <span>Showing {filteredRecords.length} of {records.length} services</span>
            <span>WBG Enterprise Quality Gate</span>
          </div>
        </div>
      </section>

      {/* 5. Modal: Register New Service */}
      {isModalOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-headline"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
        >
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <h3 id="modal-headline" className="text-base font-bold text-[#002244]">
                Register New Architectural Service
              </h3>
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 font-bold text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateService} className="space-y-4">
              <div>
                <label htmlFor="modal-service-name" className="block text-xs font-semibold text-slate-700 mb-1">
                  Service Name
                </label>
                <input
                  id="modal-service-name"
                  type="text"
                  required
                  placeholder="e.g. Identity Authorization Broker"
                  value={newServiceName}
                  onChange={(e) => setNewServiceName(e.target.value)}
                  className="w-full px-3 py-2 text-xs border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-[#0071bc]"
                />
              </div>

              <div>
                <label htmlFor="modal-service-category" className="block text-xs font-semibold text-slate-700 mb-1">
                  Architectural Category
                </label>
                <select
                  id="modal-service-category"
                  value={newServiceCategory}
                  onChange={(e) => setNewServiceCategory(e.target.value)}
                  className="w-full px-3 py-2 text-xs border border-slate-300 rounded bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-[#0071bc]"
                >
                  <option value="Core Services">Core Services</option>
                  <option value="AI Runtime">AI Runtime</option>
                  <option value="Design System">Design System</option>
                  <option value="Data & Analytics">Data & Analytics</option>
                  <option value="Security & Compliance">Security & Compliance</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-3.5 py-1.5 text-xs font-semibold text-white bg-[#0071bc] hover:bg-[#005a96] rounded shadow-sm"
                >
                  Confirm Registration
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
