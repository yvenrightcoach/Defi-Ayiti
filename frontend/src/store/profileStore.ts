import { create } from "zustand";

import { fetchMe } from "@/services/endpoints/auth";
import type { UserProfile } from "@/types/api";

interface ProfileState {
  profile: UserProfile | null;
  isLoading: boolean;
  refresh: () => Promise<UserProfile | null>;
  clear: () => void;
}

export const useProfileStore = create<ProfileState>()((set) => ({
  profile: null,
  isLoading: false,
  refresh: async () => {
    set({ isLoading: true });
    try {
      const profile = await fetchMe();
      set({ profile, isLoading: false });
      return profile;
    } catch {
      set({ isLoading: false });
      return null;
    }
  },
  clear: () => set({ profile: null }),
}));
