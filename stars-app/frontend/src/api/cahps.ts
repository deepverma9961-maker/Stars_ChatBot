import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { CahpsOverview } from "../types/cahps";

export function useGetCahpsOverview(contractId = "H3312") {
  return useQuery<CahpsOverview>({
    queryKey: ["cahps", contractId],
    queryFn: () => apiFetch(`/api/cahps?contract_id=${contractId}`),
    staleTime: 5 * 60 * 1000,
  });
}
