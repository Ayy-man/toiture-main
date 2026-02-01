"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
import { Calculator, History, LayoutDashboard, Users, PanelLeftClose, PanelLeft } from "lucide-react";
import { fr } from "@/lib/i18n/fr";

const navItems = [
  { title: fr.nav.estimateur, href: "/estimateur", icon: Calculator },
  { title: fr.nav.historique, href: "/historique", icon: History },
  { title: fr.nav.apercu, href: "/apercu", icon: LayoutDashboard },
  { title: fr.nav.clients, href: "/clients", icon: Users },
];

function SidebarToggleButton() {
  const { state, toggleSidebar } = useSidebar();
  return (
    <button
      onClick={toggleSidebar}
      className="flex items-center justify-center w-full p-2 rounded-md hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
    >
      {state === "expanded" ? (
        <PanelLeftClose className="h-5 w-5" />
      ) : (
        <PanelLeft className="h-5 w-5" />
      )}
    </button>
  );
}

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar
      variant="sidebar"
      collapsible="offcanvas"
      className="bg-[#1A1A1A] text-white border-r border-[#2A2A2A]"
    >
      <SidebarHeader className="p-4 border-b border-[#2A2A2A]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#8B2323] flex items-center justify-center">
            <span className="text-white font-bold text-sm">T</span>
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-bold text-white">Cortex</span>
            <span className="text-xs text-gray-500">Toiture LV</span>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent className="px-2 py-4">
        <SidebarGroup>
          <p className="px-3 mb-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
            Navigation
          </p>
          <SidebarMenu>
            {navItems.map((item) => (
              <SidebarMenuItem key={item.href}>
                <SidebarMenuButton
                  asChild
                  isActive={pathname.startsWith(item.href)}
                  className="h-10 px-3 data-[active=true]:bg-[#8B2323] data-[active=true]:text-white hover:bg-white/10 text-gray-300 hover:text-white"
                >
                  <Link href={item.href}>
                    <item.icon className="h-5 w-5" />
                    <span className="font-medium">{item.title}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="border-t border-[#2A2A2A] p-2">
        <SidebarToggleButton />
      </SidebarFooter>
    </Sidebar>
  );
}
