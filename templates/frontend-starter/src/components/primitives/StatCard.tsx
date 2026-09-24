import React from "react";

export interface StatCardProps {
  label: string;
  value: string | number;
  change?: string;
  trend?: "up" | "down" | "neutral";
  subtext?: string;
  icon?: React.ReactNode;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  change,
  trend,
  subtext,
  icon,
  className = "",
}) => {
  return (
    <div className={`nexus-kpi-card ${className}`}>
      <div className="nexus-kpi-header">
        <span className="nexus-kpi-label">{label}</span>
        {icon && <span className="nexus-kpi-icon" aria-hidden="true">{icon}</span>}
      </div>
      <div className="nexus-kpi-value">{value}</div>
      {(change || subtext) && (
        <div className="nexus-kpi-subtext">
          {change && (
            <span
              className={
                trend === "up"
                  ? "nexus-trend-up"
                  : trend === "down"
                  ? "nexus-trend-down"
                  : ""
              }
            >
              {trend === "up" ? "↑ " : trend === "down" ? "↓ " : ""}
              {change}
            </span>
          )}
          {subtext && <span>{subtext}</span>}
        </div>
      )}
    </div>
  );
};
