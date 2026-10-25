import type { Status } from "./common";

export interface HedisMeasure {
  measure_code: string;
  measure_name: string;
  weight: string;
  current_rate: number;
  open_gap_count: number;
  status: Status;
  target_rate: number;
  projected_rate: number;
  part: string;
}
