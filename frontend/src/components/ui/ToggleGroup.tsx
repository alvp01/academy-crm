interface ToggleGroupProps {
  value: string;
  onChange: (value: string) => void;
  options: { label: string; value: string }[];
  className?: string;
}

export function ToggleGroup({ value, onChange, options, className = "" }: ToggleGroupProps) {
  return (
    <div className={`inline-flex rounded-xl border border-surface-border overflow-hidden ${className}`}>
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            value === option.value
              ? "bg-brand-700 text-white"
              : "bg-white text-text-light hover:bg-brand-50"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
