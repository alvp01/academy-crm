import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../../store/auth";
import { Avatar } from "../ui/Avatar";

interface NavItem {
  label: string;
  path?: string;
  icon: ReactNode;
  children?: { label: string; path: string }[];
}

import { ReactNode } from "react";

const navItems: NavItem[] = [
  { 
    label: "Home", 
    path: "/dashboard", 
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
    ),
  },
  { 
    label: "Students", 
    path: "/students", 
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
  },
  { 
    label: "Courses", 
    path: "/courses", 
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
  },
  { 
    label: "Schedule", 
    path: "/schedule", 
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
  },
  { 
    label: "Payments", 
    path: "/payments", 
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
      </svg>
    ),
  },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

export function Sidebar({ open, onClose }: SidebarProps) {
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
    <aside
      className={`fixed left-0 top-0 h-full bg-white z-40 flex flex-col w-[260px] transition-transform duration-300 ${
        open ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      }`}
    >
      {/* Brand */}
      <div className="p-6 flex items-center gap-3 gradient-brand min-h-[120px]">
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
                  className={`flex items-center justify-between w-full px-6 py-3 text-text font-medium cursor-pointer hover:bg-brand-50 transition-colors ${
                    expandedSections.includes(item.label) ? "text-brand-700" : ""
                  }`}
                >
                  <span className="flex items-center gap-3">
                    {item.icon}
                    <span className="hidden sm:block">{item.label}</span>
                  </span>
                  <svg
                    className={`w-4 h-4 transition-transform ${
                      expandedSections.includes(item.label) ? "rotate-180" : ""
                    }`}
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
                          onClose();
                        }}
                        className={`w-full px-6 py-2 pl-12 text-text-light hover:text-brand-700 hover:bg-brand-50 transition-colors cursor-pointer ${
                          isActive(child.path) ? "text-brand-700 font-medium" : ""
                        }`}
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
                  onClose();
                }}
                className={`flex items-center gap-3 w-full px-6 py-3 text-text-light hover:bg-brand-50 hover:text-brand-700 transition-colors cursor-pointer ${
                  isActive(item.path)
                    ? "bg-gradient-to-r from-brand-700 to-brand-500 text-white rounded-r-[24px] mr-3"
                    : ""
                }`}
              >
                {item.icon}
                <span className="hidden sm:block">{item.label}</span>
              </button>
            )}
          </div>
        ))}
      </nav>

      {/* User profile */}
      <div className="mt-auto p-4 flex items-center gap-3 gradient-brand">
        <Avatar name={user?.name || "User"} size="md" className="bg-white/20" />
        <div className="flex-1 hidden sm:block min-w-0">
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
  );
}
