"use client";

import React, { useState } from "react";
import {
  Theme,
  Header,
  HeaderName,
  HeaderNavigation,
  HeaderMenuItem,
  HeaderGlobalBar,
  HeaderGlobalAction,
  SkipToContent,
  Content,
} from "@carbon/react";
import QueryProvider from "../providers/QueryProvider";
import AuthProvider, { useAuth } from "./auth/AuthProvider";
import { useTranslation, SupportedLocale } from "../hooks/useTranslation";

export interface AppShellProps {
  children: React.ReactNode;
}

const AppShellInner: React.FC<AppShellProps> = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState<"white" | "g100">("white");
  const { appMode, user } = useAuth();
  const { t, locale, setLocale, supportedLocales } = useTranslation("en");

  const toggleTheme = () => {
    setCurrentTheme((prev) => (prev === "white" ? "g100" : "white"));
  };

  const cycleLocale = () => {
    const nextIdx = (supportedLocales.indexOf(locale) + 1) % supportedLocales.length;
    setLocale(supportedLocales[nextIdx]);
  };

  return (
    <Theme theme={currentTheme}>
      <div className="enterprise-app-wrapper">
        <SkipToContent href="#main-content">Skip to main content</SkipToContent>

        {/* Security Classification Banner for Internal World Bank Group Applications */}
        {appMode === "internal" && (
          <div
            role="region"
            aria-label="Security Classification Banner"
            style={{
              backgroundColor: "var(--cds-support-warning, #ffcc00)",
              color: "#1a1a1a",
              padding: "0.35rem 1.5rem",
              fontSize: "0.75rem",
              fontWeight: 700,
              letterSpacing: "0.06em",
              borderBottom: "1px solid #d4a700",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              zIndex: 9999,
              position: "relative",
            }}
          >
            <span style={{ margin: "0 auto", textAlign: "center" }}>
              🔒 {t("common.officialUseOnly")}
            </span>
            {user && (
              <span style={{ fontSize: "0.6875rem", opacity: 0.9, fontWeight: 500, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span>{user.name}</span>
                <span style={{ opacity: 0.6 }}>|</span>
                <span>{user.email}</span>
              </span>
            )}
          </div>
        )}

        <Header aria-label="Enterprise Design System Application Shell" className="enterprise-shell-header">
          <HeaderName href="/" prefix="WBG">
            {t("common.appName")}
          </HeaderName>
          <HeaderNavigation aria-label="Primary Platform Navigation">
            <HeaderMenuItem href="/" isCurrentPage>
              {t("common.dashboard")}
            </HeaderMenuItem>
            <HeaderMenuItem href="/projects">{t("nav.projects")}</HeaderMenuItem>
            <HeaderMenuItem href="/disbursements">{t("nav.disbursements")}</HeaderMenuItem>
            <HeaderMenuItem href="#catalog">Component Catalog</HeaderMenuItem>
            <HeaderMenuItem href="#tokens">Design Tokens</HeaderMenuItem>
          </HeaderNavigation>
          <HeaderGlobalBar>
            {/* Locale Language Switcher */}
            <HeaderGlobalAction
              aria-label={`Language: ${locale.toUpperCase()}. Click to cycle.`}
              onClick={cycleLocale}
              tooltipAlignment="end"
            >
              <span style={{ fontSize: "0.75rem", padding: "0 0.5rem", fontWeight: 700 }}>
                🌐 {locale.toUpperCase()}
              </span>
            </HeaderGlobalAction>

            {/* Dark / Light Mode Switcher */}
            <HeaderGlobalAction
              aria-label={`Switch to ${currentTheme === "white" ? "Dark" : "Light"} Theme`}
              onClick={toggleTheme}
              tooltipAlignment="end"
            >
              <span style={{ fontSize: "0.8125rem", padding: "0 0.5rem", fontWeight: 600 }}>
                {currentTheme === "white" ? "🌙 Dark" : "☀️ Light"}
              </span>
            </HeaderGlobalAction>
          </HeaderGlobalBar>
        </Header>

        <Content id="main-content" className="enterprise-main-content">
          {children}
        </Content>

        <footer
          style={{
            padding: "1.5rem 2rem",
            borderTop: "1px solid var(--cds-border-subtle, #e0e0e0)",
            backgroundColor: "var(--cds-layer, #f4f4f4)",
            fontSize: "0.8125rem",
            color: "var(--cds-text-secondary, #525252)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "1rem",
          }}
        >
          <div>
            © 2026 World Bank Group Digital Architecture. Built with Next.js & Enterprise Design System.
          </div>
          <div style={{ display: "flex", gap: "1.5rem" }}>
            <span>WCAG 2.1 AA Compliant</span>
            <span>FastMCP Server Connected</span>
            <span>App Mode: <strong>{appMode.toUpperCase()}</strong></span>
          </div>
        </footer>
      </div>
    </Theme>
  );
};

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  return (
    <QueryProvider>
      <AuthProvider>
        <AppShellInner>{children}</AppShellInner>
      </AuthProvider>
    </QueryProvider>
  );
};

export default AppShell;
