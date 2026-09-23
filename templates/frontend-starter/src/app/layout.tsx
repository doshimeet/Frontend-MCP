import React from "react";
import type { Metadata } from "next";
import "./globals.scss";
import { AppShell } from "@/components/AppShell";

export const metadata: Metadata = {
  title: "Enterprise Digital Platform | Design System & Generation Engine",
  description:
    "AI-Native Enterprise Design System Starter Kit powered by Next.js and IBM Carbon Design System.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
