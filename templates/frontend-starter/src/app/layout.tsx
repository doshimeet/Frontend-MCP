import React from "react";
import type { Metadata } from "next";
import "./globals.css";
import { Base } from "@/components/Base";

export const metadata: Metadata = {
  title: "World Bank Group Operations Portal | Enterprise Platform",
  description:
    "AI-Native Enterprise Design System Starter Kit powered by Next.js and WBG Design System.",
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
        <Base>{children}</Base>
      </body>
    </html>
  );
}
