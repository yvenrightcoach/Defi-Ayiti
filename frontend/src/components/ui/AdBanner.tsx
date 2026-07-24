import { useEffect, useRef } from "react";

// Bloc "Defi Ayiti - banniere bas" cree dans Google AdSense. Le type global
// `Window.adsbygoogle` est deja declare dans lib/ads.ts.
const AD_CLIENT = "ca-pub-9287512825633750";
const AD_SLOT = "7693463192";

/** Banniere display AdSense, responsive. Affichee sur les pages principales. */
export default function AdBanner() {
  const pushed = useRef(false);

  useEffect(() => {
    if (pushed.current) return;
    pushed.current = true;
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch {
      // Script AdSense pas encore charge (bloqueur de pub, hors ligne...) : on ignore.
    }
  }, []);

  return (
    <div className="mx-auto w-full max-w-md overflow-hidden bg-white/95 px-3 pt-2 backdrop-blur">
      <ins
        className="adsbygoogle"
        style={{ display: "block" }}
        data-ad-client={AD_CLIENT}
        data-ad-slot={AD_SLOT}
        data-ad-format="auto"
        data-full-width-responsive="true"
      />
    </div>
  );
}
