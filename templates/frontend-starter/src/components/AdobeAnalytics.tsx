"use client";

import React, { useEffect } from "react";
import { usePathname } from "next/navigation";
import { omnitureService } from "../services/omnitureService";

export interface AdobeAnalyticsProps {
  reportSuiteId?: string;
}

export function AdobeAnalytics({ reportSuiteId = "wbg-global-operations" }: AdobeAnalyticsProps) {
  const pathname = usePathname();

  useEffect(() => {
    // Record page view on client route change
    omnitureService.trackPageView({
      pageName: pathname || "/",
      channel: "Enterprise Operations Portal",
      reportSuiteId,
    });
  }, [pathname, reportSuiteId]);

  return null; // Telemetry hook renders no DOM
}
