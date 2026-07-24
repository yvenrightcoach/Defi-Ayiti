/**
 * Pub video recompensee, via l'API "H5 Games Ads" de Google (le meme
 * ecosysteme Google Ads qu'AdMob -- utile si l'app est plus tard empaquetee
 * en app native avec Capacitor et migree vers AdMob).
 *
 * Necessite un vrai compte Google AdSense/Ad Manager for Games (approbation
 * du site, ID "ca-pub-XXXX") pour fonctionner -- voir VITE_ADS_CLIENT_ID.
 * Tant que cette variable n'est pas configuree, les pubs sont desactivees
 * (aucune simulation de recompense) : verifier la doc Google a jour
 * (https://developers.google.com/ad-placement) avant de brancher un vrai
 * compte, l'API pouvant evoluer.
 */

declare global {
  interface Window {
    adsbygoogle?: unknown[];
    adBreak?: (config: AdBreakConfig) => void;
    adConfig?: (config: Record<string, unknown>) => void;
  }
}

interface AdBreakConfig {
  type: "reward";
  name: string;
  beforeReward: (showAdFn: () => void) => void;
  adDismissed?: () => void;
  adViewed?: () => void;
  adBreakDone?: (placementInfo: { breakStatus: string }) => void;
}

const clientId = import.meta.env.VITE_ADS_CLIENT_ID;
let scriptLoaded = false;

export function isAdsEnabled(): boolean {
  return Boolean(clientId);
}

function loadScript(): Promise<void> {
  if (scriptLoaded) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://ads.google.com/games/hs.js";
    script.dataset.adClient = clientId;
    script.onload = () => {
      scriptLoaded = true;
      resolve();
    };
    script.onerror = () => reject(new Error("Impossible de charger le script publicitaire."));
    document.head.appendChild(script);
  });
}

/**
 * Affiche une pub video recompensee. Se resout a `true` si le joueur l'a
 * regardee jusqu'au bout, `false` si elle a ete fermee avant la fin ou si
 * les pubs ne sont pas configurees.
 */
export async function showRewardedAd(placementName: string): Promise<boolean> {
  if (!isAdsEnabled()) return false;

  try {
    await loadScript();
  } catch {
    return false;
  }

  return new Promise((resolve) => {
    let viewed = false;
    window.adBreak?.({
      type: "reward",
      name: placementName,
      beforeReward: (showAdFn) => showAdFn(),
      adViewed: () => {
        viewed = true;
      },
      adDismissed: () => resolve(false),
      adBreakDone: () => resolve(viewed),
    });
  });
}
