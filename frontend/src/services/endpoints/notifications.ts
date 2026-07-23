import { apiClient } from "@/services/apiClient";
import type { AppNotification, Paginated } from "@/types/api";

export async function listNotifications(): Promise<AppNotification[]> {
  const { data } = await apiClient.get<Paginated<AppNotification>>("/notifications/notifications/", {
    params: { page_size: 20 },
  });
  return data.results;
}

export async function markNotificationRead(id: string) {
  const { data } = await apiClient.post(`/notifications/notifications/${id}/mark-read/`);
  return data;
}
