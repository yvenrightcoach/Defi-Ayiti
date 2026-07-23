import { apiClient } from "@/services/apiClient";
import type { Friend, Paginated, UserProfile } from "@/types/api";

export async function listFriendRequests(): Promise<Friend[]> {
  const { data } = await apiClient.get<Paginated<Friend>>("/social/friends/", { params: { page_size: 50 } });
  return data.results;
}

export async function listFriends(): Promise<UserProfile[]> {
  const { data } = await apiClient.get<UserProfile[]>("/social/friends/friends/");
  return data;
}

export async function sendFriendRequest(addresseeId: string): Promise<Friend> {
  const { data } = await apiClient.post<Friend>("/social/friends/", { addressee_id: addresseeId });
  return data;
}

export async function acceptFriendRequest(id: string): Promise<Friend> {
  const { data } = await apiClient.post<Friend>(`/social/friends/${id}/accept/`);
  return data;
}

export async function declineFriendRequest(id: string): Promise<Friend> {
  const { data } = await apiClient.post<Friend>(`/social/friends/${id}/decline/`);
  return data;
}
