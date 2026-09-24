"use client";

import React, { useEffect } from "react";
import { loggerService } from "../services/LoggerService";

export interface AppInsightsProps {
  connectionString?: string;
  children?: React.ReactNode;
}

export function AppInsights({ connectionString, children }: AppInsightsProps) {
  useEffect(() => {
    loggerService.info("Azure Application Insights initialized", {
      status: "connected",
      hasConnectionString: Boolean(connectionString),
    });
  }, [connectionString]);

  return <>{children}</>;
}
