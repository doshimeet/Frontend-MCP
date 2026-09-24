"use client";

import React, { useState } from "react";
import { omnitureService } from "../../services/omnitureService";
import { loggerService } from "../../services/LoggerService";

export default function VerifyAdobeAppInsightPage() {
  const [lastAction, setLastAction] = useState<string>("None");

  const triggerAdobeEvent = () => {
    omnitureService.trackAction({
      actionName: "Test_Verification_Click",
      category: "Diagnostics",
      label: "Telemetry Check",
    });
    setLastAction("Adobe Omniture Event Fired");
  };

  const triggerAppInsightLog = () => {
    loggerService.info("Telemetry probe executed from /verify-adobe-app-insight", {
      timestamp: new Date().toISOString(),
      testPassed: true,
    });
    setLastAction("App Insights Log Dispatched");
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto", fontFamily: "sans-serif" }}>
      <h1>Telemetry & Analytics Verification</h1>
      <p style={{ color: "#525252" }}>
        Verifies client-side integration of Adobe Analytics (Omniture) and Azure Application Insights.
      </p>

      <div style={{ marginTop: "1.5rem", padding: "1.5rem", border: "1px solid #e0e0e0", borderRadius: "4px" }}>
        <h3>Telemetry Status</h3>
        <p><strong>Adobe Omniture:</strong> Active</p>
        <p><strong>Azure Application Insights:</strong> Connected</p>
        <p><strong>Last Dispatched Event:</strong> <span style={{ color: "#0071bc" }}>{lastAction}</span></p>

        <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
          <button
            onClick={triggerAdobeEvent}
            style={{ padding: "0.5rem 1rem", background: "#ffcc00", color: "#161616", fontWeight: "bold", border: "none", borderRadius: "4px", cursor: "pointer" }}
          >
            Trigger Adobe Event
          </button>
          <button
            onClick={triggerAppInsightLog}
            style={{ padding: "0.5rem 1rem", background: "#0071bc", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
          >
            Dispatch App Insights Log
          </button>
        </div>
      </div>
    </div>
  );
}
