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
import { useTranslation } from "../hooks/useTranslation";

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
      <div className="nexus-app-container">
        <SkipToContent href="#main-content">Skip to main content</SkipToContent>

        {/* Institutional 56px Header with Integrated Classification Pill */}
        <Header aria-label="Enterprise Institutional Application Shell" className="nexus-institutional-header">
          <div className="nexus-header-brand-group">
            <HeaderName href="/" prefix="WBG">
              {t("common.appName")}
            </HeaderName>
            {appMode === "internal" && (
              <span className="nexus-classification-pill" aria-label="Security Classification: Official Use Only">
                OFFICIAL USE ONLY
              </span>
            )}
          </div>

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
            {/* User Metadata */}
            {user && (
              <div className="nexus-user-meta" aria-label={`Current User: ${user.name}`}>
                <span className="nexus-user-name">{user.name}</span>
                <span className="nexus-user-badge">{user.role}</span>
              </div>
            )}

            {/* Locale Language Switcher */}
            <HeaderGlobalAction
              aria-label={`Language: ${locale.toUpperCase()}. Click to cycle.`}
              onClick={cycleLocale}
              tooltipAlignment="end"
            >
              <span className="nexus-locale-switcher">
                🌐 {locale.toUpperCase()}
              </span>
            </HeaderGlobalAction>

            {/* Dark / Light Mode Switcher */}
            <HeaderGlobalAction
              aria-label={`Switch to ${currentTheme === "white" ? "Dark" : "Light"} Theme`}
              onClick={toggleTheme}
              tooltipAlignment="end"
            >
              <span className="nexus-theme-toggle">
                {currentTheme === "white" ? "🌙 Dark" : "☀️ Light"}
              </span>
            </HeaderGlobalAction>
          </HeaderGlobalBar>
        </Header>

        {/* Main Content Area */}
        <Content id="main-content" className="nexus-main-content">
          {children}
        </Content>

        {/* Institutional Dignified Footer */}
        <footer className="nexus-footer">
          <div className="nexus-footer-copyright">
            © 2026 World Bank Group Digital Architecture. Built with Next.js & Nexus Enterprise Platform.
          </div>
          <div className="nexus-footer-meta">
            <span className="nexus-footer-badge">WCAG 2.1 AA Compliant</span>
            <span className="nexus-footer-badge">FastMCP Server v2.0</span>
            <span className="nexus-footer-badge">Mode: {appMode.toUpperCase()}</span>
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
