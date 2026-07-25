import { apiClient } from "@/services/apiClient";
import type { ConvertDiamondsResult, UserProfile } from "@/types/api";

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

export async function updateMe(
  payload: Partial<{ avatar_url: string; active_frame: string | null; department: string | null }>,
) {
  const { data } = await apiClient.patch<UserProfile>("/auth/me/", payload);
  return data;
}

/** Choisit un heros debloque comme photo de profil (ou `null` pour revenir a avatar_url/l'avatar par defaut). */
export async function setAvatarHero(heroId: string | null): Promise<UserProfile> {
  const { data } = await apiClient.patch<UserProfile>("/auth/me/", { avatar_hero: heroId });
  return data;
}

export async function searchProfiles(search: string): Promise<UserProfile[]> {
  const { data } = await apiClient.get(`/auth/profiles/`, { params: { search } });
  return data.results;
}

export async function convertDiamondsToCoins(diamonds: number): Promise<ConvertDiamondsResult> {
  const { data } = await apiClient.post<ConvertDiamondsResult>("/auth/me/convert-diamonds/", { diamonds });
  return data;
}

export async function requestPasswordReset(email: string): Promise<void> {
  await apiClient.post("/auth/password/reset/", { email });
}

export async function confirmPasswordReset(
  uid: string,
  token: string,
  newPassword1: string,
  newPassword2: string,
): Promise<void> {
  await apiClient.post("/auth/password/reset/confirm/", {
    uid,
    token,
    new_password1: newPassword1,
    new_password2: newPassword2,
  });
}
