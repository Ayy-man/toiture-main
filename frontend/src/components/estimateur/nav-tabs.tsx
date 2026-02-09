"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { cn } from "@/lib/utils";

export function EstimateurTabs() {
  const pathname = usePathname();
  const { t } = useLanguage();

  const tabs = [
    { href: "/estimateur", label: t.estimateur.prix },
    { href: "/estimateur/materiaux", label: t.estimateur.materiaux },
    { href: "/estimateur/complet", label: t.estimateur.soumissionComplete },
    { href: "/estimateur/soumissions", label: t.submission?.submissions || "Soumissions" },
  ];

  return (
    <nav className="border-b">
      <div className="flex space-x-8">
        {tabs.map((tab) => {
          // For /estimateur, exact match only
          // For sub-routes, use startsWith
          const isActive =
            tab.href === "/estimateur"
              ? pathname === "/estimateur"
              : pathname.startsWith(tab.href);

          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                "py-4 px-1 text-sm font-medium transition-colors",
                isActive
                  ? "border-b-2 border-[#8B2323] text-[#8B2323]"
                  : "text-muted-foreground hover:text-[#8B2323]"
              )}
            >
              {tab.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
