"use client";

import React from "react";
import { AppShell } from "./AppShell";
import { MsalAuthentication } from "./MsalAuthentication";
import { AdobeAnalytics } from "./AdobeAnalytics";
import { AppInsights } from "./AppInsights";

export interface BaseProps {
  children: React.ReactNode;
}

/**
 * Base Component
 * Standard corporate wrapper combining MSAL session, App Insights,
 * Adobe Analytics, and the institutional AppShell layout.
 */
export function Base({ children }: BaseProps) {
  return (
    <MsalAuthentication>
      <AppInsights>
        <AdobeAnalytics />
        <AppShell>{children}</AppShell>
      </AppInsights>
    </MsalAuthentication>
  );
}
