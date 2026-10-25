import type { Channel, GapStatus } from "./common";

export interface MemberGapRow {
  member_key: string;
  display_name: string;
  age: number;
  propensity_score: number;
  measure_code: string;
  measure_name: string;
  gap_status: GapStatus;
  last_contact: string;
  recommended_channel: Channel;
  pcp_name: string;
  campaign_name?: string | null;
}

export interface MemberGapPage {
  items: MemberGapRow[];
  total: number;
  page: number;
  page_size: number;
}

export interface MemberClinicalEvent {
  event_date: string;
  event_type: string;
  description: string;
  provider: string;
}

export interface MemberMedication {
  drug_name: string;
  ndc: string;
  days_supply: number;
  last_fill: string;
  adherent: boolean;
}

export interface MemberProfile {
  member_key: string;
  display_name: string;
  age: number;
  gender: string;
  plan_name: string;
  contract_id: string;
  dual_eligible: boolean;
  lis_flag: boolean;
  utilization_segment: string;
  propensity_score: number;
  open_gaps: MemberGapRow[];
  clinical_events: MemberClinicalEvent[];
  medications: MemberMedication[];
}
