import { create } from "zustand";
import { persist } from "zustand/middleware";

import { setSoundEnabled } from "@/lib/sound";

interface SoundState {
  enabled: boolean;
  toggle: () => void;
}

export const useSoundStore = create<SoundState>()(
  persist(
    (set, get) => ({
      enabled: true,
      toggle: () => {
        const next = !get().enabled;
        setSoundEnabled(next);
        set({ enabled: next });
      },
    }),
    {
      name: "defi-ayiti-sound",
      onRehydrateStorage: () => (state) => {
        if (state) setSoundEnabled(state.enabled);
      },
    },
  ),
);
