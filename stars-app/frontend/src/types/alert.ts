export interface AlertItem {
  alert_id: string;
  severity: "critical" | "warning" | "info";
  title: string;
  body: string;
  meta?: string | null;
  measure_code?: string | null;
  cta_label?: string | null;
  cta_page?: string | null;
}

export interface PriorityItem {
  measure_code: string;
  measure_name: string;
  current_rate: number;
  target_rate: number;
  gap: number;
  priority_score: number;
  owner: string;
}

export interface AlertsResponse {
  alerts: AlertItem[];
  priority_board: PriorityItem[];
}
