import { ReactNode } from "react";
import { Outlet } from "react-router-dom";

interface DashboardLayoutProps {
  sidebar: ReactNode;
  topbar: ReactNode;
}

export function DashboardLayout({ sidebar, topbar }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-surface-background">
      {/* Sidebar */}
      {sidebar}

      {/* Main content */}
      <div className="lg:ml-[260px] min-h-screen">
        {/* Top bar */}
        {topbar}

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
