"use client";

import React, { useState } from "react";
import Link from "next/link";

interface ProjectRecord {
  id: string;
  name: string;
  country: string;
  region: string;
  sector: string;
  commitmentUSD: string;
  status: "Active" | "Pipeline" | "Under Review" | "Closed";
  rating: "Satisfactory" | "Moderately Satisfactory" | "Needs Attention";
}

const INITIAL_PROJECTS: ProjectRecord[] = [
  {
    id: "P174201",
    name: "Sustainable Rural Resilient Water & Sanitation Program",
    country: "Indonesia",
    region: "East Asia & Pacific",
    sector: "Water & Sanitation",
    commitmentUSD: "$400,000,000",
    status: "Active",
    rating: "Satisfactory",
  },
  {
    id: "P168432",
    name: "Sub-Saharan Clean Grid Integration & Solar Scaling",
    country: "Kenya",
    region: "Eastern & Southern Africa",
    sector: "Energy & Extractives",
    commitmentUSD: "$280,000,000",
    status: "Active",
    rating: "Satisfactory",
  },
  {
    id: "P179510",
    name: "Andean Climate-Resilient Agricultural Logistics",
    country: "Peru",
    region: "Latin America & Caribbean",
    sector: "Agriculture & Food",
    commitmentUSD: "$165,000,000",
    status: "Under Review",
    rating: "Needs Attention",
  },
  {
    id: "P171120",
    name: "Coastal Metro Transit Decarbonization Facility",
    country: "Vietnam",
    region: "East Asia & Pacific",
    sector: "Transportation",
    commitmentUSD: "$320,000,000",
    status: "Active",
    rating: "Moderately Satisfactory",
  },
  {
    id: "P180240",
    name: "Digital Health Infrastructure & Tracing Platform",
    country: "Morocco",
    region: "Middle East & North Africa",
    sector: "Health & Nutrition",
    commitmentUSD: "$120,000,000",
    status: "Pipeline",
    rating: "Satisfactory",
  },
];

export default function ProjectsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSector, setSelectedSector] = useState("All");

  const filteredProjects = INITIAL_PROJECTS.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.country.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSector = selectedSector === "All" || p.sector === selectedSector;
    return matchesSearch && matchesSector;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="text-xs uppercase tracking-wider font-semibold text-slate-500 mb-1">
            Operations & Global Practices
          </div>
          <h1 className="text-2xl font-bold text-[#002244] tracking-tight">
            Institutional Projects & Operations Directory
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Global portfolio oversight covering sovereign development tranches and technical assistance facilities.
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
            href="/disbursements"
            className="px-3.5 py-2 text-xs font-semibold text-white bg-[#0071bc] hover:bg-[#005a96] rounded transition-colors shadow-sm"
          >
            View Disbursements →
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            Total Active Portfolio
          </div>
          <div className="text-2xl font-bold text-[#002244] mt-2 font-mono tabular-nums">
            $1,285,000,000
          </div>
          <div className="text-xs text-emerald-700 font-semibold mt-1">
            ↑ 4.2% committed YoY
          </div>
        </div>

        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            Active Operations
          </div>
          <div className="text-2xl font-bold text-[#002244] mt-2 font-mono tabular-nums">
            5 Projects
          </div>
          <div className="text-xs text-slate-500 mt-1">Across 5 Sovereign Partners</div>
        </div>

        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            Satisfactory Rating
          </div>
          <div className="text-2xl font-bold text-emerald-600 mt-2 font-mono tabular-nums">
            80.0%
          </div>
          <div className="text-xs text-slate-500 mt-1">Independent Evaluation Group benchmark</div>
        </div>

        <div className="nexus-kpi-card bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
            Environment Mode
          </div>
          <div className="text-2xl font-bold text-[#0071bc] mt-2">
            Standalone
          </div>
          <div className="text-xs text-slate-500 mt-1">Tailwind CSS + Nexus Tokens</div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
        <div className="w-full sm:w-80">
          <input
            type="text"
            placeholder="Search by ID, country, or title..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-[#0071bc]"
            aria-label="Filter project records"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <label htmlFor="sector-filter" className="text-xs font-semibold text-slate-600 whitespace-nowrap">
            Sector:
          </label>
          <select
            id="sector-filter"
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            className="px-3 py-2 text-sm border border-slate-300 rounded bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-[#0071bc]"
          >
            <option value="All">All Sectors</option>
            <option value="Water & Sanitation">Water & Sanitation</option>
            <option value="Energy & Extractives">Energy & Extractives</option>
            <option value="Agriculture & Food">Agriculture & Food</option>
            <option value="Transportation">Transportation</option>
            <option value="Health & Nutrition">Health & Nutrition</option>
          </select>
        </div>
      </div>

      {/* Table Container */}
      <div className="nexus-table-container bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="nexus-table w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs uppercase font-semibold text-slate-600 tracking-wider">
              <tr>
                <th className="px-4 py-3">Project ID</th>
                <th className="px-4 py-3">Operation Title</th>
                <th className="px-4 py-3">Country / Region</th>
                <th className="px-4 py-3">Sector</th>
                <th className="px-4 py-3 text-right">Commitment (USD)</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Performance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {filteredProjects.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-slate-500">
                    No matching operations found.
                  </td>
                </tr>
              ) : (
                filteredProjects.map((project) => (
                  <tr key={project.id} className="hover:bg-blue-50/30 transition-colors">
                    <td className="px-4 py-3 font-mono font-medium text-[#0071bc]">
                      {project.id}
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-900">
                      {project.name}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      <div className="font-medium text-slate-800">{project.country}</div>
                      <div className="text-xs text-slate-400">{project.region}</div>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{project.sector}</td>
                    <td className="px-4 py-3 text-right font-mono font-semibold text-slate-900 tabular-nums">
                      {project.commitmentUSD}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
                          project.status === "Active"
                            ? "bg-emerald-100 text-emerald-800"
                            : project.status === "Under Review"
                            ? "bg-amber-100 text-amber-900"
                            : project.status === "Pipeline"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {project.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`text-xs font-medium ${
                          project.rating === "Satisfactory"
                            ? "text-emerald-700"
                            : project.rating === "Needs Attention"
                            ? "text-red-700"
                            : "text-amber-700"
                        }`}
                      >
                        {project.rating}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 bg-slate-50 border-t border-slate-200 text-xs text-slate-500 flex items-center justify-between">
          <span>Showing {filteredProjects.length} of {INITIAL_PROJECTS.length} operations</span>
          <span>Source: World Bank Group Operations 360 Core</span>
        </div>
      </div>
    </div>
  );
}
