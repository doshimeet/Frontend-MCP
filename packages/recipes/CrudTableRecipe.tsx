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
} from "@wbg/design-system";

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

/**
 * Data hook for fetching tabular records via TanStack Query or REST endpoint.
 */
export function useTableRecords(apiEndpoint?: string, fallbackData?: TableItem[]) {
  // If TanStack Query is mounted in the app, this hook cleanly resolves data
  const [data, setData] = useState<TableItem[]>(fallbackData || []);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    if (!apiEndpoint) {
      if (fallbackData) setData(fallbackData);
      return;
    }
    let isMounted = true;
    setLoading(true);
    fetch(apiEndpoint)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch`);
        return res.json();
      })
      .then((json) => {
        if (isMounted) {
          setData(json);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [apiEndpoint]);

  return { data, loading, error };
}


const TABLE_HEADERS = [
  { key: "name", header: "Entity Name" },
  { key: "code", header: "Identifier" },
  { key: "category", header: "Category" },
  { key: "status", header: "Lifecycle Status" },
  { key: "updatedAt", header: "Last Modified" },
  { key: "owner", header: "Owner" },
];

const STATUS_TAG_TYPES: Record<TableItem["status"], "green" | "blue" | "red" | "gray"> = {
  active: "green",
  pending: "blue",
  suspended: "red",
  archived: "gray",
};

export const CrudTableRecipe: React.FC<CrudTableRecipeProps> = ({
  title = "Records Management",
  description = "View, search, and manage enterprise operational records across all departments.",
  initialItems = [
    {
      id: "REC-001",
      name: "Global Healthcare Policy",
      code: "POL-HLTH-2026",
      category: "Compliance",
      status: "active",
      updatedAt: "2026-09-18",
      owner: "Sarah Connor",
    },
    {
      id: "REC-002",
      name: "Enterprise Cloud Migration",
      code: "PRJ-CLD-8821",
      category: "Infrastructure",
      status: "pending",
      updatedAt: "2026-09-20",
      owner: "Alex Vance",
    },
    {
      id: "REC-003",
      name: "Financial Year Audit 2025",
      code: "AUD-FIN-2025",
      category: "Finance",
      status: "active",
      updatedAt: "2026-09-15",
      owner: "Elena Rostova",
    },
    {
      id: "REC-004",
      name: "Legacy VPN Gateway",
      code: "SYS-VPN-0012",
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
  ],
  isLoading = false,
  errorMessage = null,
  onRefresh,
  onCreateNew,
}) => {
  const [items, setItems] = useState<TableItem[]>(initialItems);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);

  // Filter items based on search query
  const filteredItems = useMemo(() => {
    if (!searchQuery.trim()) return items;
    const query = searchQuery.toLowerCase();
    return items.filter(
      (item) =>
        item.name.toLowerCase().includes(query) ||
        item.code.toLowerCase().includes(query) ||
        item.category.toLowerCase().includes(query) ||
        item.owner.toLowerCase().includes(query)
    );
  }, [items, searchQuery]);

  // Paginated window
  const paginatedItems = useMemo(() => {
    const startIndex = (page - 1) * pageSize;
    return filteredItems.slice(startIndex, startIndex + pageSize);
  }, [filteredItems, page, pageSize]);

  return (
    <div className="crud-table-recipe-container" style={{ width: "100%", padding: "1.5rem" }}>
      {/* 1. Header Section */}
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
            {title}
          </h1>
          <p style={{ margin: "0.25rem 0 0", color: "var(--cds-text-secondary, #525252)", fontSize: "0.875rem" }}>
            {description}
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {onRefresh && (
            <Button kind="secondary" size="md" onClick={onRefresh} aria-label="Refresh table data">
              Refresh
            </Button>
          )}
          <Button
            kind="primary"
            size="md"
            onClick={onCreateNew || (() => alert("Create Record modal invoked"))}
            aria-label="Create new record"
          >
            Create Record
          </Button>
        </div>
      </div>

      {/* 2. Resilient State: Error State */}
      {errorMessage && (
        <div style={{ marginBottom: "1.5rem" }}>
          <InlineNotification
            kind="error"
            title="Data retrieval failed"
            subtitle={errorMessage}
            aria-label="Table loading error notification"
          />
        </div>
      )}

      {/* 3. Data Table Layout */}
      <DataTable rows={paginatedItems} headers={TABLE_HEADERS} isSortable>
        {({ rows, headers, getHeaderProps, getRowProps, getTableProps }) => (
          <div style={{ background: "var(--cds-layer, #ffffff)", border: "1px solid var(--cds-border-subtle, #e0e0e0)" }}>
            <TableToolbar aria-label="Table operational toolbar">
              <TableToolbarContent>
                <TableToolbarSearch
                  persistent
                  placeholder="Search by name, ID, category, or owner..."
                  value={searchQuery}
                  onChange={(_evt: any, val?: string) => {
                    setSearchQuery(val ?? "");
                    setPage(1);
                  }}
                  id="crud-table-search"
                />
              </TableToolbarContent>
            </TableToolbar>

            <Table {...getTableProps()} aria-label={title}>
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
                {/* 4. Resilient State: Loading State */}
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, idx) => (
                    <TableRow key={`skeleton-row-${idx}`}>
                      {headers.map((header) => (
                        <TableCell key={`skeleton-cell-${header.key}`}>
                          <SkeletonText paragraph={false} lineCount={1} />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                ) : rows.length === 0 ? (
                  /* 5. Resilient State: Empty State */
                  <TableRow>
                    <TableCell colSpan={headers.length} style={{ textAlign: "center", padding: "3rem 1rem" }}>
                      <div style={{ maxWidth: "420px", margin: "0 auto" }}>
                        <h3 style={{ fontSize: "1.125rem", fontWeight: 600, margin: "0 0 0.5rem" }}>
                          No matching records found
                        </h3>
                        <p style={{ color: "var(--cds-text-secondary, #525252)", fontSize: "0.875rem", margin: "0 0 1rem" }}>
                          {searchQuery
                            ? `No records match your search criteria "${searchQuery}". Try clearing your search term.`
                            : "There are currently no records in this view. Create your first record to begin."}
                        </p>
                        {searchQuery ? (
                          <Button kind="tertiary" size="sm" onClick={() => setSearchQuery("")}>
                            Clear Search
                          </Button>
                        ) : (
                          <Button kind="primary" size="sm" onClick={onCreateNew}>
                            Create New Record
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  /* 6. Normal Data Rows */
                  rows.map((row) => {
                    const originalItem = items.find((it) => it.id === row.id);
                    return (
                      <TableRow {...getRowProps({ row })}>
                        {row.cells.map((cell) => {
                          if (cell.info.header === "status" && originalItem) {
                            return (
                              <TableCell key={cell.id}>
                                <Tag type={STATUS_TAG_TYPES[originalItem.status]} size="sm">
                                  {originalItem.status.toUpperCase()}
                                </Tag>
                              </TableCell>
                            );
                          }
                          if (cell.info.header === "code") {
                            return (
                              <TableCell key={cell.id}>
                                <code style={{ fontFamily: "var(--cds-code-01, monospace)", fontSize: "0.8125rem" }}>
                                  {cell.value}
                                </code>
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

            {/* 7. Pagination Controls */}
            {!isLoading && filteredItems.length > 0 && (
              <Pagination
                backwardText="Previous page"
                forwardText="Next page"
                itemsPerPageText="Records per page:"
                page={page}
                pageNumberText="Page Number"
                pageSize={pageSize}
                pageSizes={[10, 25, 50]}
                totalItems={filteredItems.length}
                onChange={({ page: newPage, pageSize: newPageSize }) => {
                  setPage(newPage);
                  setPageSize(newPageSize);
                }}
              />
            )}
          </div>
        )}
      </DataTable>
    </div>
  );
};

export default CrudTableRecipe;
