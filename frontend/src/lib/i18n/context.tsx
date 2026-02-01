"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { fr } from "./fr";
import { en } from "./en";

export type Locale = "en" | "fr";

// Define a structural type that allows any string values for each key
type DeepStringify<T> = {
  [K in keyof T]: T[K] extends object ? DeepStringify<T[K]> : string;
};

type Translations = DeepStringify<typeof fr>;

interface LanguageContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

const STORAGE_KEY = "cortex-locale";

const translations: Record<Locale, Translations> = {
  fr,
  en,
};

interface LanguageProviderProps {
  children: ReactNode;
}

export function LanguageProvider({ children }: LanguageProviderProps) {
  const [locale, setLocaleState] = useState<Locale>("fr");
  const [mounted, setMounted] = useState(false);

  // Load locale from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY) as Locale | null;
    if (stored && (stored === "en" || stored === "fr")) {
      setLocaleState(stored);
    }
    setMounted(true);
  }, []);

  // Persist locale changes to localStorage
  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    localStorage.setItem(STORAGE_KEY, newLocale);
  };

  const value: LanguageContextValue = {
    locale,
    setLocale,
    t: translations[locale],
  };

  // Prevent hydration mismatch by rendering with default locale until mounted
  if (!mounted) {
    return (
      <LanguageContext.Provider value={{ ...value, t: translations.fr }}>
        {children}
      </LanguageContext.Provider>
    );
  }

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}
