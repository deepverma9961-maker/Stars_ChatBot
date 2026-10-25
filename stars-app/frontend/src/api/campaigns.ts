import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { CampaignResponse } from "../types/campaign";

export function useGetCampaigns(status?: string, measureCode?: string) {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (measureCode) params.set("measure_code", measureCode);
  return useQuery<CampaignResponse>({
    queryKey: ["campaigns", status, measureCode],
    queryFn: () => apiFetch(`/api/campaigns?${params.toString()}`),
    staleTime: 5 * 60 * 1000,
  });
}
