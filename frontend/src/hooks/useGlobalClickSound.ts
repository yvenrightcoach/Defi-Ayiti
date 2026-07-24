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
      // Pas de verification "disabled" ici : un bouton deja desactive AVANT
      // le clic ne declenche jamais d'evenement "click" natif (le
      // navigateur ne le dispatche pas). La verifier quand meme est
      // contre-productif, car de nombreux boutons se desactivent de facon
      // synchrone des le clic (ex. setLoadingAction avant un appel reseau) --
      // React re-rend avant que l'evenement natif ne remonte jusqu'a
      // document, donc cette verification bloquait le son sur la plupart
      // des boutons d'action.
      const className = typeof el.className === "string" ? el.className : "";
      if (className.includes("btn-game") || className.includes("tile-game")) {
        playClick();
      }
    }

    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, []);
}
