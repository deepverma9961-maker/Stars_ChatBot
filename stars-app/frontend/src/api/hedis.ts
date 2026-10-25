import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { HedisMeasure } from "../types/hedis";

export function useGetHedisMeasures(contractId = "H3312", colorFilter = "all", sort = "rate_asc") {
  return useQuery<HedisMeasure[]>({
    queryKey: ["hedis", contractId, colorFilter, sort],
    queryFn: () =>
      apiFetch(`/api/hedis-measures?contract_id=${contractId}&color_filter=${colorFilter}&sort=${sort}`),
    staleTime: 5 * 60 * 1000,
  });
}
