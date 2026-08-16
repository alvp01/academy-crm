import { InputHTMLAttributes } from "react";

interface SearchBarProps extends InputHTMLAttributes<HTMLInputElement> {
  placeholder?: string;
}

export function SearchBar({ placeholder = "Search anything here...", className = "", ...props }: SearchBarProps) {
  return (
    <div className={`flex items-center gap-2 px-4 py-2 bg-white border border-surface-border rounded-xl w-full max-w-md ${className}`}>
      <svg className="w-5 h-5 text-text-light flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        type="search"
        placeholder={placeholder}
        className="flex-1 outline-none text-text placeholder-text-light bg-transparent"
        {...props}
      />
    </div>
  );
}
