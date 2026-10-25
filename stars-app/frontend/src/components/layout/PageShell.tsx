import type { ReactNode } from "react";

interface PageShellProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
}

export default function PageShell({ title, subtitle, actions, children }: PageShellProps) {
  return (
    <div className="min-h-full flex flex-col">
      {/* Page header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-brand-border bg-brand-navy/60 sticky top-0 z-10 backdrop-blur">
        <div>
          <h1 className="page-title">{title}</h1>
          {subtitle && <p className="text-muted text-xs mt-0.5">{subtitle}</p>}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
      {/* Content */}
      <div className="flex-1 p-6">{children}</div>
    </div>
  );
}
