import { apiClient } from "@/services/apiClient";
import type { UserProfile } from "@/types/api";

export interface GuestLoginResponse {
  access: string;
  refresh: string;
  user: { id: string; username: string; is_guest: boolean };
}

export async function guestLogin(): Promise<GuestLoginResponse> {
  const { data } = await apiClient.post<GuestLoginResponse>("/auth/guest/");
  return data;
}

export interface EmailLoginResponse {
  access: string;
  refresh: string;
  user: { pk: string; username: string; email: string };
}

export async function emailLogin(username: string, password: string): Promise<EmailLoginResponse> {
  const { data } = await apiClient.post<EmailLoginResponse>("/auth/login/", { username, password });
  return data;
}

export async function emailRegister(payload: {
  username: string;
  email: string;
  password1: string;
  password2: string;
}): Promise<EmailLoginResponse> {
  const { data } = await apiClient.post<EmailLoginResponse>("/auth/register/", payload);
  return data;
}

export async function fetchMe(): Promise<UserProfile> {
  const { data } = await apiClient.get<UserProfile>("/auth/me/");
  return data;
}

export async function updateMe(payload: Partial<Pick<UserProfile, "avatar_url" | "active_frame" | "department">>) {
  const { data } = await apiClient.patch<UserProfile>("/auth/me/", payload);
  return data;
}

export async function searchProfiles(search: string): Promise<UserProfile[]> {
  const { data } = await apiClient.get(`/auth/profiles/`, { params: { search } });
  return data.results;
}
