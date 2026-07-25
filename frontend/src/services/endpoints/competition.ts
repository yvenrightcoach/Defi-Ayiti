import { apiClient } from "@/services/apiClient";
import type { LeaderboardPeriod, LeaderboardResponse, LeaderboardScope, Paginated, Season } from "@/types/api";

export async function listSeasons(): Promise<Season[]> {
  const { data } = await apiClient.get<Paginated<Season>>("/competition/seasons/", { params: { page_size: 10 } });
  return data.results;
}

export async function getLeaderboard(
  scope: LeaderboardScope,
  period: LeaderboardPeriod,
): Promise<LeaderboardResponse> {
  const { data } = await apiClient.get<LeaderboardResponse>("/competition/leaderboards/", {
    params: { scope, period },
  });
  return data;
}
