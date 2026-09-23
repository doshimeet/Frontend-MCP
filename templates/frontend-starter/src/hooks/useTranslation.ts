"use client";

import { useState, useCallback } from "react";
import en from "../../messages/en.json";
import fr from "../../messages/fr.json";
import es from "../../messages/es.json";

export type SupportedLocale = "en" | "fr" | "es";

const dictionaries: Record<SupportedLocale, any> = {
  en,
  fr,
  es,
};

export function useTranslation(initialLocale: SupportedLocale = "en") {
  const [locale, setLocale] = useState<SupportedLocale>(initialLocale);

  const t = useCallback(
    (keyPath: string): string => {
      const keys = keyPath.split(".");
      let current = dictionaries[locale] || dictionaries.en;
      for (const k of keys) {
        if (current && typeof current === "object" && k in current) {
          current = current[k];
        } else {
          // Fallback to English
          let fallback = dictionaries.en;
          for (const fk of keys) {
            if (fallback && typeof fallback === "object" && fk in fallback) {
              fallback = fallback[fk];
            } else {
              return keyPath;
            }
          }
          return typeof fallback === "string" ? fallback : keyPath;
        }
      }
      return typeof current === "string" ? current : keyPath;
    },
    [locale]
  );

  return { t, locale, setLocale, supportedLocales: ["en", "fr", "es"] as const };
}

export default useTranslation;
