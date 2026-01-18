import { Metadata } from "next";
import { DashboardContent } from "@/components/dashboard/dashboard-content";

export const metadata: Metadata = {
  title: "Analytics - TOITURELV Cortex",
  description: "View AI estimate accuracy metrics and analytics",
};

export default function DashboardPage() {
  return (
    <main className="container mx-auto max-w-7xl px-4 py-8">
      <DashboardContent />
    </main>
  );
}
