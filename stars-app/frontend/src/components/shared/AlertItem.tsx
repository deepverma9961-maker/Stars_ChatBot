import { useNavigate } from "react-router-dom";
import type { AlertItem as AlertItemType } from "../../types/alert";

const ICON: Record<string, string> = { critical: "🔴", warning: "🟡", info: "🔵" };

export default function AlertItem({ item }: { item: AlertItemType }) {
  const navigate = useNavigate();
  return (
    <div className={`alert-item ${item.severity}`}>
      <span className="text-lg mt-0.5">{ICON[item.severity]}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="font-medium text-white text-sm">{item.title}</div>
          {item.meta && <span className="text-xs text-muted whitespace-nowrap">{item.meta}</span>}
        </div>
        <div className="text-xs text-muted mt-0.5">{item.body}</div>
        {item.cta_label && item.cta_page && (
          <button
            onClick={() => navigate(`/${item.cta_page}`)}
            className="mt-2 text-xs px-2 py-1 rounded border border-white/20 text-white hover:bg-white/10 transition"
          >
            {item.cta_label}
          </button>
        )}
      </div>
    </div>
  );
}
