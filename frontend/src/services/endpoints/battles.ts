import { apiClient } from "@/services/apiClient";
import type { BattleRoom, Match, Paginated, RoomType } from "@/types/api";

export async function listRooms(): Promise<BattleRoom[]> {
  const { data } = await apiClient.get<Paginated<BattleRoom>>("/battles/rooms/", { params: { page_size: 20 } });
  return data.results;
}

export async function createRoom(roomType: RoomType, maxPlayers: number): Promise<BattleRoom> {
  const { data } = await apiClient.post<BattleRoom>("/battles/rooms/", { room_type: roomType, max_players: maxPlayers });
  return data;
}

export async function joinRoom(roomCode: string): Promise<BattleRoom> {
  const { data } = await apiClient.post<BattleRoom>("/battles/rooms/join/", { room_code: roomCode });
  return data;
}

export async function getRoom(id: string): Promise<BattleRoom> {
  const { data } = await apiClient.get<BattleRoom>(`/battles/rooms/${id}/`);
  return data;
}

export async function startMatch(
  roomId: string,
  payload: { category?: string; department?: string; question_count?: number; time_limit_seconds?: number },
): Promise<Match> {
  const { data } = await apiClient.post<Match>(`/battles/rooms/${roomId}/start/`, payload);
  return data;
}

export async function getMatch(id: string): Promise<Match> {
  const { data } = await apiClient.get<Match>(`/battles/matches/${id}/`);
  return data;
}

export async function submitMatchScore(matchId: string, score: number, correctAnswers: number): Promise<Match> {
  const { data } = await apiClient.post<Match>(`/battles/matches/${matchId}/submit-score/`, {
    score,
    correct_answers: correctAnswers,
  });
  return data;
}

export async function finishMatch(matchId: string): Promise<Match> {
  const { data } = await apiClient.post<Match>(`/battles/matches/${matchId}/finish/`);
  return data;
}
