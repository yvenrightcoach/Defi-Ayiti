import { useEffect } from "react";

import { playMenuMusic, stopMenuMusic } from "@/lib/sound";

// La musique de menu joue sur toutes les pages sauf pendant une partie
// (quiz/battle), ou le silence aide a se concentrer sur les questions.
const SILENT_PREFIXES = ["/quiz", "/battle"];

export function useMenuMusic(pathname: string) {
  useEffect(() => {
    const shouldPlay = !SILENT_PREFIXES.some((prefix) => pathname.startsWith(prefix));
    if (shouldPlay) {
      playMenuMusic();
    } else {
      stopMenuMusic();
    }
  }, [pathname]);
}
