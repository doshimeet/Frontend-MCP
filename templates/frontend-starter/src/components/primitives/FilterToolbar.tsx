import React from "react";

export interface FilterToolbarProps {
  searchPlaceholder?: string;
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  children?: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
}

export const FilterToolbar: React.FC<FilterToolbarProps> = ({
  searchPlaceholder = "Search records...",
  searchValue,
  onSearchChange,
  children,
  actions,
  className = "",
}) => {
  return (
    <div className={`nexus-toolbar ${className}`} role="toolbar" aria-label="Filters and actions">
      <div className="nexus-toolbar__filters">
        {onSearchChange !== undefined && (
          <div className="nexus-search-input-wrapper">
            <input
              type="search"
              className="nexus-input nexus-input--search"
              placeholder={searchPlaceholder}
              value={searchValue}
              onChange={(e) => onSearchChange(e.target.value)}
              aria-label={searchPlaceholder}
            />
          </div>
        )}
        {children}
      </div>
      {actions && <div className="nexus-toolbar__actions">{actions}</div>}
    </div>
  );
};
