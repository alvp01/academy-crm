import { ReactNode } from "react";

interface AlertProps {
  variant?: "error" | "success" | "warning" | "info";
  children: ReactNode;
  className?: string;
}

const variantClasses = {
  error: "bg-red-50 border-red-200 text-red-700",
  success: "bg-green-50 border-green-200 text-green-700",
  warning: "bg-amber-50 border-amber-200 text-amber-700",
  info: "bg-blue-50 border-blue-200 text-blue-700",
};

export function Alert({ variant = "error", children, className = "" }: AlertProps) {
  return (
    <div
      className={`p-4 border rounded-xl text-sm ${variantClasses[variant]} ${className}`}
    >
      {children}
    </div>
  );
}
