"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
  SidebarRail,
  useSidebar,
} from "@/components/ui/sidebar";
import { Calculator, History, LayoutDashboard, Users, Home } from "lucide-react";
import { useLanguage, type Locale } from "@/lib/i18n";

function useNavItems() {
  const { t } = useLanguage();
  return [
    { title: t.nav.estimateur, href: "/estimateur", icon: Calculator },
    { title: t.nav.historique, href: "/historique", icon: History },
    { title: t.nav.apercu, href: "/apercu", icon: LayoutDashboard },
    { title: t.nav.clients, href: "/clients", icon: Users },
  ];
}

function SidebarBranding() {
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";

  return (
    <SidebarMenuButton size="lg" asChild>
      <Link href="/estimateur" className="gap-3">
        <div className="flex aspect-square size-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Home className="size-5" />
        </div>
        {!isCollapsed && (
          <div className="flex flex-col gap-0.5 leading-none">
            <span className="font-bold text-base">Cortex</span>
            <span className="text-xs text-sidebar-foreground/60">Toiture LV</span>
          </div>
        )}
      </Link>
    </SidebarMenuButton>
  );
}

type NavItemType = { title: string; href: string; icon: React.ComponentType<{ className?: string }> };

function NavItem({ item, isActive }: { item: NavItemType; isActive: boolean }) {
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";

  return (
    <SidebarMenuButton
      asChild
      isActive={isActive}
      tooltip={item.title}
    >
      <Link href={item.href} className="gap-3">
        <item.icon className="size-5 shrink-0" />
        {!isCollapsed && <span>{item.title}</span>}
      </Link>
    </SidebarMenuButton>
  );
}

function LanguageToggle() {
  const { locale, setLocale } = useLanguage();
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";

  const handleToggle = (newLocale: Locale) => {
    setLocale(newLocale);
  };

  if (isCollapsed) {
    return (
      <SidebarMenuButton
        tooltip={locale === "fr" ? "Langue" : "Language"}
        onClick={() => handleToggle(locale === "fr" ? "en" : "fr")}
      >
        <span className="text-xs font-bold">{locale.toUpperCase()}</span>
      </SidebarMenuButton>
    );
  }

  return (
    <div className="flex items-center gap-1 p-1 rounded-lg bg-sidebar-accent">
      <button
        type="button"
        className={`h-8 px-3 text-xs font-semibold flex-1 rounded-md transition-colors ${
          locale === "en"
            ? "bg-sidebar-primary text-sidebar-primary-foreground"
            : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent"
        }`}
        onClick={() => handleToggle("en")}
      >
        EN
      </button>
      <button
        type="button"
        className={`h-8 px-3 text-xs font-semibold flex-1 rounded-md transition-colors ${
          locale === "fr"
            ? "bg-sidebar-primary text-sidebar-primary-foreground"
            : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent"
        }`}
        onClick={() => handleToggle("fr")}
      >
        FR
      </button>
    </div>
  );
}

function SidebarUserInfo() {
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";

  return (
    <SidebarMenuButton size="lg" className="gap-3">
      <div className="flex aspect-square size-9 shrink-0 items-center justify-center rounded-lg bg-sidebar-accent text-sidebar-accent-foreground">
        <span className="text-sm font-bold">LV</span>
      </div>
      {!isCollapsed && (
        <div className="flex flex-col gap-0.5 leading-none">
          <span className="font-medium text-sm">Toiture LV</span>
          <span className="text-xs text-sidebar-foreground/60">Admin</span>
        </div>
      )}
    </SidebarMenuButton>
  );
}

export function AppSidebar() {
  const pathname = usePathname();
  const navItems = useNavItems();

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="border-b border-sidebar-border">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarBranding />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarMenu>
            {navItems.map((item) => (
              <SidebarMenuItem key={item.href}>
                <NavItem
                  item={item}
                  isActive={pathname === item.href || pathname.startsWith(item.href + "/")}
                />
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="border-t border-sidebar-border">
        <SidebarMenu>
          <SidebarMenuItem>
            <LanguageToggle />
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarUserInfo />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
