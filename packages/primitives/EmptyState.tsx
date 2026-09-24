import React from "react";

export interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  action,
  className = "",
}) => {
  return (
    <div className={`nexus-empty-state ${className}`} role="status">
      {icon && <div className="nexus-empty-state__icon">{icon}</div>}
      <h3 className="nexus-empty-state__title">{title}</h3>
      <p className="nexus-empty-state__description">{description}</p>
      {action && <div className="nexus-empty-state__action">{action}</div>}
    </div>
  );
};
