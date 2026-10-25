export interface CahpsComposite {
  composite_code: string;
  composite_name: string;
  current_pct: number;
  status: string;
  weight: string;
  part: string;
}

export interface CahpsOverview {
  contract_id: string;
  current_rating: number;
  projected_rating: number;
  gap_to_4_star: number;
  days_remaining: number;
  qbp_at_stake: number;
  composites: CahpsComposite[];
}
