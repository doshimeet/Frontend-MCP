"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import QueryProvider from "../providers/QueryProvider";
import AuthProvider, { useAuth } from "./auth/AuthProvider";
import { useTranslation } from "../hooks/useTranslation";

export interface AppShellProps {
  children: React.ReactNode;
}

const AppShellInner: React.FC<AppShellProps> = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState<"light" | "dark">("light");
  const { appMode, user } = useAuth();
  const { t, locale, setLocale, supportedLocales } = useTranslation("en");
  const pathname = usePathname();

  const toggleTheme = () => {
    setCurrentTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const cycleLocale = () => {
    const nextIdx = (supportedLocales.indexOf(locale) + 1) % supportedLocales.length;
    setLocale(supportedLocales[nextIdx]);
  };

  const navLinks = [
    { href: "/", label: t("common.dashboard") },
    { href: "/projects", label: t("nav.projects") },
    { href: "/disbursements", label: t("nav.disbursements") },
    { href: "#catalog", label: "Component Catalog" },
    { href: "#tokens", label: "Design Tokens" },
  ];

  return (
    <div className={`nexus-app-container ${currentTheme === "dark" ? "theme-dark" : "theme-light"}`}>
      {/* Accessible Skip Navigation */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-[#002244] focus:font-semibold focus:shadow-md focus:rounded"
      >
        Skip to main content
      </a>

      {/* Institutional 56px Header with Integrated Security Classification Pill */}
      <header
        aria-label="Enterprise Institutional Application Shell"
        className="nexus-institutional-header flex items-center justify-between px-6 h-14 bg-[#002244] text-white border-b border-white/10"
        role="banner"
      >
        {/* Brand Group */}
        <div className="nexus-header-brand-group flex items-center gap-4">
          <Link href="/" className="flex items-center gap-2 text-white no-underline hover:opacity-90 transition-opacity">
            <span className="px-2 py-0.5 rounded bg-[#0071bc] text-[11px] font-bold text-white tracking-wider">
              WBG
            </span>
            <span className="font-semibold text-sm tracking-tight text-white">
              {t("common.appName")}
            </span>
          </Link>
          {appMode === "internal" && (
            <span className="nexus-classification-pill" aria-label="Security Classification: Official Use Only">
              OFFICIAL USE ONLY
            </span>
          )}
        </div>

        {/* Primary Platform Navigation */}
        <nav className="hidden md:flex items-center gap-1" aria-label="Primary Platform Navigation">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                  isActive
                    ? "bg-white/15 text-white font-semibold shadow-inner"
                    : "text-slate-300 hover:text-white hover:bg-white/10"
                }`}
                aria-current={isActive ? "page" : undefined}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Global Action Bar */}
        <div className="flex items-center gap-3">
          {/* User Metadata */}
          {user && (
            <div className="nexus-user-meta hidden sm:flex items-center gap-2 px-2 text-white" aria-label={`Current User: ${user.name}`}>
              <span className="nexus-user-name text-xs font-semibold">{user.name}</span>
              <span className="nexus-user-badge text-[10px] px-1.5 py-0.5 rounded bg-white/20 uppercase tracking-wide">
                {user.role}
              </span>
            </div>
          )}

          {/* Locale Switcher */}
          <button
            type="button"
            aria-label={`Language: ${locale.toUpperCase()}. Click to cycle.`}
            onClick={cycleLocale}
            className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold text-white bg-white/10 hover:bg-white/20 rounded transition-colors"
          >
            <span aria-hidden="true">🌐</span>
            <span>{locale.toUpperCase()}</span>
          </button>

          {/* Theme Toggle */}
          <button
            type="button"
            aria-label={`Switch to ${currentTheme === "light" ? "Dark" : "Light"} Theme`}
            onClick={toggleTheme}
            className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold text-white bg-white/10 hover:bg-white/20 rounded transition-colors"
          >
            <span>{currentTheme === "light" ? "🌙 Dark" : "☀️ Light"}</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main id="main-content" className="nexus-main-content">
        {children}
      </main>

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
