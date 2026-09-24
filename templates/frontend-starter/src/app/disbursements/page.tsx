"use client";

import React, { useState } from "react";
import Link from "next/link";

interface TrancheRecord {
  trancheId: string;
  projectId: string;
  recipient: string;
  facility: string;
  authorizedUSD: string;
  disbursedUSD: string;
  executionDate: string;
  status: "Released" | "Pending Clearance" | "Under Audit" | "Scheduled";
}

const DISBURSEMENT_DATA: TrancheRecord[] = [
  {
    trancheId: "TR-2026-081",
    projectId: "P174201",
    recipient: "Ministry of Public Works, Indonesia",
    facility: "IBRD Sovereign Loan",
    authorizedUSD: "$120,000,000",
    disbursedUSD: "$120,000,000",
    executionDate: "2026-03-15",
    status: "Released",
  },
  {
    trancheId: "TR-2026-082",
    projectId: "P168432",
    recipient: "National Treasury of Kenya",
    facility: "IDA Concessional Credit",
    authorizedUSD: "$75,000,000",
    disbursedUSD: "$50,000,000",
    executionDate: "2026-06-01",
    status: "Pending Clearance",
  },
  {
    trancheId: "TR-2026-083",
    projectId: "P179510",
    recipient: "Ministerio de Economía y Finanzas, Peru",
    facility: "IBRD Green Climate Tranche",
    authorizedUSD: "$45,000,000",
    disbursedUSD: "$15,000,000",
    executionDate: "2026-07-20",
    status: "Under Audit",
  },
  {
    trancheId: "TR-2026-084",
    projectId: "P171120",
    recipient: "Ministry of Transport, Vietnam",
    facility: "IBRD Infrastructure Bond Facility",
    authorizedUSD: "$90,000,000",
    disbursedUSD: "$90,000,000",
    executionDate: "2026-02-10",
    status: "Released",
  },
  {
    trancheId: "TR-2026-085",
    projectId: "P180240",
    recipient: "Ministère de la Santé, Morocco",
    facility: "IDA Emergency Health Envelope",
    authorizedUSD: "$40,000,000",
    disbursedUSD: "$0",
    executionDate: "2026-10-15",
    status: "Scheduled",
  },
];

export default function DisbursementsPage() {
  const [filterStatus, setFilterStatus] = useState("All");

  const filteredTranches = DISBURSEMENT_DATA.filter((tranche) => {
    return filterStatus === "All" || tranche.status === filterStatus;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="text-xs uppercase tracking-wider font-semibold text-slate-500 mb-1">
            Financial Operations & Treasury
          </div>
          <h1 className="text-2xl font-bold text-[#002244] tracking-tight">
            Financial Tranches & Disbursement Inspector
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Fiduciary monitoring, liquidity drawdowns, and automated tranche compliance tracking.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/"
            className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-50 transition-colors shadow-sm"
          >
            ← Back to Overview
          </Link>
          <Link
            href="/projects"
            className="px-3.5 py-2 text-xs font-semibold text-white bg-[#0071bc] hover:bg-[#005a96] rounded transition-colors shadow-sm"
          >
            View Projects Directory →
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            Total Authorized Tranches
          </div>
          <div className="text-2xl font-bold text-[#002244] mt-2 font-mono tabular-nums">
            $370,000,000
          </div>
          <div className="text-xs text-slate-500 mt-1">5 multi-year facility envelopes</div>
        </div>

        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            Cumulative Disbursed
          </div>
          <div className="text-2xl font-bold text-emerald-600 mt-2 font-mono tabular-nums">
            $275,000,000
          </div>
          <div className="text-xs text-emerald-700 font-semibold mt-1">
            74.3% liquidation efficiency
          </div>
        </div>

        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            Undisbursed Balance
          </div>
          <div className="text-2xl font-bold text-[#0071bc] mt-2 font-mono tabular-nums">
            $95,000,000
          </div>
          <div className="text-xs text-slate-500 mt-1">Committed to active work packages</div>
        </div>

        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            Compliance Review
          </div>
          <div className="text-2xl font-bold text-slate-800 mt-2">
            100% Pass
          </div>
          <div className="text-xs text-slate-500 mt-1">Fiduciary AML & KYC cleared</div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex items-center justify-between bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-600">Filter by Status:</span>
          {["All", "Released", "Pending Clearance", "Under Audit", "Scheduled"].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                filterStatus === st
                  ? "bg-[#002244] text-white font-semibold"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
        <div className="text-xs text-slate-500">
          Showing {filteredTranches.length} tranches
        </div>
      </div>

      {/* Tranches Table */}
      <div className="nexus-table-container bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="nexus-table w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs uppercase font-semibold text-slate-600 tracking-wider">
              <tr>
                <th className="px-4 py-3">Tranche ID</th>
                <th className="px-4 py-3">Project Link</th>
                <th className="px-4 py-3">Recipient Sovereign Entity</th>
                <th className="px-4 py-3">Financing Facility</th>
                <th className="px-4 py-3 text-right">Authorized (USD)</th>
                <th className="px-4 py-3 text-right">Disbursed (USD)</th>
                <th className="px-4 py-3">Execution Date</th>
                <th className="px-4 py-3">Tranche Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {filteredTranches.map((tranche) => (
                <tr key={tranche.trancheId} className="hover:bg-blue-50/30 transition-colors">
                  <td className="px-4 py-3 font-mono font-medium text-[#002244]">
                    {tranche.trancheId}
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      href="/projects"
                      className="font-mono text-xs font-semibold text-[#0071bc] hover:underline"
                    >
                      {tranche.projectId}
                    </Link>
                  </td>
                  <td className="px-4 py-3 font-medium text-slate-800">
                    {tranche.recipient}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-600">
                    {tranche.facility}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-slate-700 tabular-nums">
                    {tranche.authorizedUSD}
                  </td>
                  <td className="px-4 py-3 text-right font-mono font-semibold text-slate-900 tabular-nums">
                    {tranche.disbursedUSD}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">
                    {tranche.executionDate}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
                        tranche.status === "Released"
                          ? "bg-emerald-100 text-emerald-800"
                          : tranche.status === "Pending Clearance"
                          ? "bg-blue-100 text-blue-800"
                          : tranche.status === "Under Audit"
                          ? "bg-amber-100 text-amber-900"
                          : "bg-slate-100 text-slate-700"
                      }`}
                    >
                      {tranche.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 bg-slate-50 border-t border-slate-200 text-xs text-slate-500 flex items-center justify-between">
          <span>Official Sovereign Fiduciary Register</span>
          <span>Security Classification: OFFICIAL USE ONLY</span>
        </div>
      </div>
    </div>
  );
}
