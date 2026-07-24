import { useEffect } from "react";

import { playClick } from "@/lib/sound";

/**
 * Joue un petit clic sur tous les boutons/tuiles du "design system" du jeu
 * (classes btn-game-*, tile-game-*), sans avoir a instrumenter chaque
 * bouton individuellement dans chaque page. Ecoute unique au niveau du
 * document, montee une seule fois a la racine de l'app.
 */
export function useGlobalClickSound() {
  useEffect(() => {
    function handleClick(event: MouseEvent) {
      const target = event.target as HTMLElement | null;
      const el = target?.closest<HTMLElement>("button, a");
      if (!el) return;
      if ((el as HTMLButtonElement).disabled) return;
      const className = typeof el.className === "string" ? el.className : "";
      if (className.includes("btn-game") || className.includes("tile-game")) {
        playClick();
      }
    }

    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, []);
}
