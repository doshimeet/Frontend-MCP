"use client";

import React from "react";
import { useMsalAuth } from "../../components/MsalAuthentication";

export default function VerifyMsalPage() {
  const { user, login, logout, switchRole } = useMsalAuth();

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto", fontFamily: "sans-serif" }}>
      <h1>MSAL Verification Dashboard</h1>
      <p style={{ color: "#525252" }}>
        Validates institutional Microsoft Authentication Library (MSAL) session state and claims.
      </p>

      <div style={{ marginTop: "1.5rem", padding: "1.5rem", border: "1px solid #e0e0e0", borderRadius: "4px" }}>
        <h3>Session Details</h3>
        <p><strong>Authenticated:</strong> {user.isAuthenticated ? "Yes (Active Session)" : "No"}</p>
        <p><strong>User:</strong> {user.name}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Active Role:</strong> {user.role}</p>

        <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
          <button
            onClick={() => switchRole("Procurement Lead")}
            style={{ padding: "0.5rem 1rem", background: "#002244", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
          >
            Role: Procurement Lead
          </button>
          <button
            onClick={() => switchRole("Financial Auditor")}
            style={{ padding: "0.5rem 1rem", background: "#0071bc", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
          >
            Role: Financial Auditor
          </button>
          {user.isAuthenticated ? (
            <button
              onClick={logout}
              style={{ padding: "0.5rem 1rem", background: "#da1e28", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
            >
              Sign Out
            </button>
          ) : (
            <button
              onClick={login}
              style={{ padding: "0.5rem 1rem", background: "#198038", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
            >
              Sign In
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
