import { useState } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../store/auth";

interface NavItem {
  label: string;
  path?: string;
  icon: string;
  children?: { label: string; path: string }[];
}

const navItems: NavItem[] = [
  { label: "Home", path: "/dashboard", icon: "🏠" },
  { label: "Students", path: "/students", icon: "👥" },
  { label: "Courses", path: "/courses", icon: "📚" },
  { label: "Schedule", path: "/schedule", icon: "📅" },
  { label: "Payments", path: "/payments", icon: "💳" },
];

export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState<string[]>([]);
  const navigate = useNavigate();
  const location = useLocation();
  const logout = useAuthStore((s) => s.logout);
  const user = useAuthStore((s) => s.user);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const toggleSection = (label: string) => {
    setExpandedSections((prev) =>
      prev.includes(label) ? prev.filter((s) => s !== label) : [...prev, label]
    );
  };

  const isActive = (path?: string) => path && location.pathname === path;

  return (
    <div className="min-h-screen bg-surface-background">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}>
        {/* Brand */}
        <div className="sidebar-brand">
          <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
            <span className="text-2xl">🎓</span>
          </div>
          <span className="text-white font-bold text-lg hidden sm:block">Academy</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 overflow-y-auto">
          {navItems.map((item) => (
            <div key={item.label}>
              {item.children ? (
                <>
                  <button
                    onClick={() => toggleSection(item.label)}
                    className={`sidebar-section-header w-full ${expandedSections.includes(item.label) ? "text-brand-700" : ""}`}
                  >
                    <span className="flex items-center gap-3">
                      <span className="text-lg">{item.icon}</span>
                      <span className="hidden sm:block">{item.label}</span>
                    </span>
                    <svg
                      className={`w-4 h-4 transition-transform ${expandedSections.includes(item.label) ? "rotate-180" : ""}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {expandedSections.includes(item.label) && (
                    <div>
                      {item.children.map((child) => (
                        <button
                          key={child.path}
                          onClick={() => {
                            navigate(child.path);
                            setSidebarOpen(false);
                          }}
                          className={`sidebar-sub-item w-full ${isActive(child.path) ? "text-brand-700 font-medium" : ""}`}
                        >
                          {child.label}
                        </button>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <button
                  onClick={() => {
                    navigate(item.path || "/");
                    setSidebarOpen(false);
                  }}
                  className={`sidebar-nav-item w-full ${isActive(item.path) ? "active" : ""}`}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span className="hidden sm:block">{item.label}</span>
                </button>
              )}
            </div>
          ))}
        </nav>

        {/* User profile */}
        <div className="sidebar-user">
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center text-white font-medium">
            {user?.name?.charAt(0) || "U"}
          </div>
          <div className="flex-1 hidden sm:block">
            <p className="text-white font-medium text-sm truncate">{user?.name || "User"}</p>
            <p className="text-white/70 text-xs truncate">{user?.email || "user@email.com"}</p>
          </div>
          <button
            onClick={handleLogout}
            className="text-white/70 hover:text-white transition-colors"
            title="Logout"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:ml-[260px] min-h-screen">
        {/* Top bar */}
        <header className="sticky top-0 z-20 bg-white border-b border-surface-border">
          <div className="flex items-center justify-between px-4 sm:px-6 py-4">
            {/* Mobile menu button */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 hover:bg-brand-50 rounded-lg transition-colors"
            >
              <svg className="w-6 h-6 text-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            {/* Search */}
            <div className="search-bar hidden sm:flex">
              <svg className="w-5 h-5 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input type="text" placeholder="Search anything here..." />
            </div>

            {/* Right side */}
            <div className="flex items-center gap-4">
              <button className="p-2 hover:bg-brand-50 rounded-lg transition-colors relative">
                <svg className="w-5 h-5 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span className="absolute top-1 right-1 w-2 h-2 bg-brand-500 rounded-full"></span>
              </button>
              <div className="w-9 h-9 rounded-full gradient-brand flex items-center justify-center text-white font-medium text-sm">
                {user?.name?.charAt(0) || "U"}
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
