import React from "react";

export default function AboutPage() {
  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto", fontFamily: "sans-serif" }}>
      <h1>About the Enterprise Operations Portal</h1>
      <p style={{ lineHeight: "1.6", color: "#525252" }}>
        This institutional application was scaffolded using the World Bank Group Enterprise Design System Engine.
        It enforces strict WCAG 2.1 AA accessibility guidelines, Azure Active Directory MSAL authentication,
        and unified telemetry tracking.
      </p>

      <div style={{ marginTop: "2rem", padding: "1.5rem", background: "#f4f6f8", borderRadius: "4px" }}>
        <h3>Architecture Specifications</h3>
        <ul style={{ lineHeight: "1.8", color: "#161616" }}>
          <li><strong>Design System:</strong> @wbg/nexus (v2.0.0)</li>
          <li><strong>Runtime:</strong> Next.js 14 App Router</li>
          <li><strong>Hosting:</strong> Azure App Service Linux Slot</li>
          <li><strong>Authentication:</strong> MSAL / Azure Entra ID</li>
          <li><strong>Telemetry:</strong> Azure Application Insights & Adobe Analytics</li>
        </ul>
      </div>
    </div>
  );
}
