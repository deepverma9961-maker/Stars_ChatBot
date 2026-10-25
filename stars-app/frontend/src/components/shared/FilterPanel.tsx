interface Option { value: string; label: string }

interface FilterPanelProps {
  label: string;
  options: Option[];
  selected: string[];
  onChange: (selected: string[]) => void;
  multi?: boolean;
}

export default function FilterPanel({ label, options, selected, onChange, multi = true }: FilterPanelProps) {
  const toggle = (val: string) => {
    if (!multi) {
      onChange(selected[0] === val ? [] : [val]);
      return;
    }
    onChange(selected.includes(val) ? selected.filter(v => v !== val) : [...selected, val]);
  };
  return (
    <div className="mb-4">
      <div className="text-xs text-muted mb-2">{label}</div>
      <div className="flex flex-wrap gap-1.5">
        {options.map(opt => (
          <button
            key={opt.value}
            onClick={() => toggle(opt.value)}
            className={`fchip ${selected.includes(opt.value) ? "on" : ""}`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}
