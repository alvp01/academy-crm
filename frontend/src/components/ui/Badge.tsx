import { ReactNode } from "react";

interface BadgeProps {
  variant?: "success" | "error" | "warning" | "info" | "default";
  children: ReactNode;
  className?: string;
}

const variantClasses = {
  success: "bg-green-100 text-green-700",
  error: "bg-red-100 text-red-700",
  warning: "bg-amber-100 text-amber-700",
  info: "bg-blue-100 text-blue-700",
  default: "bg-surface-background text-text-light",
};

export function Badge({ variant = "default", children, className = "" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${variantClasses[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
