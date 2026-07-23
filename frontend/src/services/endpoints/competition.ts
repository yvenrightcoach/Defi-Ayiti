import { apiClient } from "@/services/apiClient";
import type { LeaderboardEntry, LeaderboardPeriod, LeaderboardScope, Paginated, Season } from "@/types/api";

export async function listSeasons(): Promise<Season[]> {
  const { data } = await apiClient.get<Paginated<Season>>("/competition/seasons/", { params: { page_size: 10 } });
  return data.results;
}

export async function listLeaderboard(
  scope: LeaderboardScope,
  period: LeaderboardPeriod,
  departmentId?: string,
): Promise<LeaderboardEntry[]> {
  const { data } = await apiClient.get<Paginated<LeaderboardEntry>>("/competition/leaderboards/", {
    params: { scope, period, department: departmentId, page_size: 50 },
  });
  return data.results;
}
