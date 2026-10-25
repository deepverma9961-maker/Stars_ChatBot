export interface CampaignRow {
  campaign_name: string;
  measure_code: string;
  channel: string;
  member_count: number;
  projected_closures: number;
  actual_closures: number | null;
  lift_pct: string;
  cost_str: string;
  roi_str: string;
  status: string;
}

export interface ROISummary {
  total_members: number;
  total_closures: number;
  avg_roi: string;
  total_cost: string;
}

export interface CampaignResponse {
  items: CampaignRow[];
  summary: ROISummary;
}
