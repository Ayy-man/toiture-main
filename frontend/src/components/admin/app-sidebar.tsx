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
} from "@/components/ui/sidebar";
import { Calculator, History, LayoutDashboard, Users } from "lucide-react";
import { fr } from "@/lib/i18n/fr";

const navItems = [
  { title: fr.nav.estimateur, href: "/estimateur", icon: Calculator },
  { title: fr.nav.historique, href: "/historique", icon: History },
  { title: fr.nav.apercu, href: "/apercu", icon: LayoutDashboard },
  { title: fr.nav.clients, href: "/clients", icon: Users },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar
      variant="sidebar"
      collapsible="icon"
      className="bg-[#1A1A1A] text-white border-r-0"
    >
      <SidebarHeader className="p-4">
        <span className="text-xl font-bold text-[#8B2323]">Cortex</span>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-gray-400">
            Navigation
          </SidebarGroupLabel>
          <SidebarMenu>
            {navItems.map((item) => (
              <SidebarMenuItem key={item.href}>
                <SidebarMenuButton
                  asChild
                  isActive={pathname.startsWith(item.href)}
                  className="data-[active=true]:bg-[#8B2323]/20 data-[active=true]:text-[#8B2323] hover:bg-[#8B2323]/10 hover:text-[#8B2323]/80"
                >
                  <Link href={item.href}>
                    <item.icon className="h-4 w-4" />
                    <span>{item.title}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
