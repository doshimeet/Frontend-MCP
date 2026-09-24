"use client";

import React, { useState, useMemo } from "react";
import {
  Table,
  Table as DataTable,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
  Button,
  Tag,
  Input,
} from "@wbg/nexus";

export interface TableItem {
  id: string;
  name: string;
  code: string;
  category: string;
  status: "active" | "pending" | "suspended" | "archived";
  updatedAt: string;
  owner: string;
}

export interface CrudTableRecipeProps {
  title?: string;
  description?: string;
  apiEndpoint?: string;
  initialItems?: TableItem[];
  isLoading?: boolean;
  errorMessage?: string | null;
  onRefresh?: () => void;
  onCreateNew?: () => void;
}

const DEFAULT_ITEMS: TableItem[] = [
  {
    id: "REC-001",
    name: "Enterprise Data Hub Lakehouse",
    code: "ARC-LAKE-0912",
    category: "Infrastructure",
    status: "active",
    updatedAt: "2026-09-21",
    owner: "Alex Vance",
  },
  {
    id: "REC-002",
    name: "Global Payments Settlement Engine",
    code: "FIN-SETTLE-8831",
    category: "Finance",
    status: "active",
    updatedAt: "2026-09-20",
    owner: "Elena Rostova",
  },
  {
    id: "REC-003",
    name: "Customer Onboarding Microservice",
    code: "SVC-ONBOARD-2019",
    category: "Customer Experience",
    status: "pending",
    updatedAt: "2026-09-18",
    owner: "Kenji Sato",
  },
  {
    id: "REC-004",
    name: "Legacy Auth Token Bridge",
    code: "LEG-SEC-1102",
    category: "Security",
    status: "suspended",
    updatedAt: "2026-08-30",
    owner: "Marcus Brody",
  },
  {
    id: "REC-005",
    name: "Q3 Marketing Vendor Contract",
    code: "CTR-VND-4410",
    category: "Procurement",
    status: "archived",
    updatedAt: "2026-07-12",
    owner: "David Miller",
  },
];

export const CrudTableRecipe: React.FC<CrudTableRecipeProps> = ({
  title = "Enterprise Operations Registry",
  description = "Authoritative directory of operational resources, workflows, and infrastructure assets.",
  initialItems = DEFAULT_ITEMS,
  isLoading = false,
  errorMessage = null,
  onRefresh,
  onCreateNew,
}) => {
  const [items] = useState<TableItem[]>(initialItems);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      const matchesSearch =
        !searchQuery.trim() ||
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.owner.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory =
        selectedCategory === "all" || item.category.toLowerCase() === selectedCategory.toLowerCase();
      return matchesSearch && matchesCategory;
    });
  }, [items, searchQuery, selectedCategory]);

  return (
    <div className="crud-table-view">
      {/* 1. Header Slot */}
      <header className="nexus-page-header">
        <div className="nexus-page-header__meta">
          <span className="nexus-breadcrumb">Institutional Registry / Resources</span>
          <h1 className="nexus-page-title">{title}</h1>
          <p className="nexus-page-subtitle">{description}</p>
        </div>

        <div className="nexus-page-header__actions">
          {onRefresh && (
            <Button variant="outline" size="sm" onClick={onRefresh} aria-label="Refresh table data">
              Refresh
            </Button>
          )}
          <Button
            variant="default"
            size="sm"
            onClick={onCreateNew || (() => alert("Create Record modal invoked"))}
            aria-label="Create new record"
          >
            Create Record
          </Button>
        </div>
      </header>

      {/* 2. Error Notification */}
      {errorMessage && (
        <div className="nexus-alert nexus-alert--danger" role="alert">
          <strong>Data retrieval failed:</strong> {errorMessage}
        </div>
      )}

      {/* 3. Composable Toolbar Slot */}
      <div className="nexus-toolbar" role="toolbar" aria-label="Table filters and search">
        <div className="nexus-toolbar__filters">
          <Input
            type="search"
            placeholder="Search records by name, code, owner..."
            value={searchQuery}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
            aria-label="Search records"
            className="nexus-search-input"
          />

          <select
            className="nexus-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            aria-label="Filter by category"
          >
            <option value="all">All Categories</option>
            <option value="Infrastructure">Infrastructure</option>
            <option value="Finance">Finance</option>
            <option value="Customer Experience">Customer Experience</option>
            <option value="Security">Security</option>
            <option value="Procurement">Procurement</option>
          </select>
        </div>

        <div className="nexus-toolbar__actions">
          <span className="nexus-record-count">
            {filteredItems.length} record{filteredItems.length === 1 ? "" : "s"}
          </span>
        </div>
      </div>

      {/* 4. Data View Slot */}
      <div className="nexus-table-container">
        {isLoading ? (
          <div className="nexus-empty-state">
            <p className="nexus-empty-state__description">Loading registry records...</p>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="nexus-empty-state">
            <h3 className="nexus-empty-state__title">No matching records found</h3>
            <p className="nexus-empty-state__description">
              Try adjusting your search query or category filter to locate records.
            </p>
          </div>
        ) : (
          <Table className="nexus-table">
            <TableHeader>
              <TableRow>
                <TableHead>Entity Name</TableHead>
                <TableHead>Resource Code</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Updated</TableHead>
                <TableHead>Owner</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredItems.map((item) => (
                <TableRow key={item.id}>
                  <TableCell className="nexus-font-medium">{item.name}</TableCell>
                  <TableCell className="nexus-font-mono">{item.code}</TableCell>
                  <TableCell>{item.category}</TableCell>
                  <TableCell>
                    <Tag
                      type={
                        item.status === "active"
                          ? "green"
                          : item.status === "pending"
                          ? "blue"
                          : item.status === "suspended"
                          ? "red"
                          : "gray"
                      }
                    >
                      {item.status.toUpperCase()}
                    </Tag>
                  </TableCell>
                  <TableCell className="nexus-font-mono">{item.updatedAt}</TableCell>
                  <TableCell>{item.owner}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
};

export default CrudTableRecipe;
