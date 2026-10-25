import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { MemberGapPage, MemberProfile } from "../types/member";

export interface MemberGapFilters {
  contract_id?: string;
  measure_code?: string;
  gap_status?: string;
  propensity?: string;
  page?: number;
  page_size?: number;
}

export function useGetMemberGaps(filters: MemberGapFilters = {}) {
  const params = new URLSearchParams();
  if (filters.contract_id) params.set("contract_id", filters.contract_id);
  if (filters.measure_code) params.set("measure_code", filters.measure_code);
  if (filters.gap_status) params.set("gap_status", filters.gap_status);
  if (filters.propensity) params.set("propensity", filters.propensity);
  params.set("page", String(filters.page ?? 1));
  params.set("page_size", String(filters.page_size ?? 50));
  return useQuery<MemberGapPage>({
    queryKey: ["member-gaps", filters],
    queryFn: () => apiFetch(`/api/members/gaps?${params.toString()}`),
    staleTime: 2 * 60 * 1000,
  });
}

export function useGetMemberProfile(memberKey: string | null) {
  return useQuery<MemberProfile>({
    queryKey: ["member", memberKey],
    queryFn: () => apiFetch(`/api/members/${memberKey}`),
    enabled: !!memberKey,
    staleTime: 5 * 60 * 1000,
  });
}
