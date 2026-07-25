import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

import { useInstallPrompt } from "@/hooks/useInstallPrompt";

const DISMISSED_KEY = "defi-ayiti-install-banner-dismissed";

export default function InstallBanner() {
  const { canInstall, isIOS, isStandalone, promptInstall } = useInstallPrompt();
  const [dismissed, setDismissed] = useState(true);

  useEffect(() => {
    setDismissed(localStorage.getItem(DISMISSED_KEY) === "1");
  }, []);

  function dismiss() {
    localStorage.setItem(DISMISSED_KEY, "1");
    setDismissed(true);
  }

  const shouldShow = !isStandalone && !dismissed && (canInstall || isIOS);

  return (
    <AnimatePresence>
      {shouldShow && (
        <motion.div
          initial={{ opacity: 0, y: -24 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -24 }}
          className="fixed inset-x-0 top-0 z-50 flex items-center gap-3 bg-haiti-blue px-4 py-2.5 text-sm text-white shadow-card"
          style={{ paddingTop: "calc(env(safe-area-inset-top) + 0.625rem)" }}
        >
          <span className="text-xl">🐓</span>
          {canInstall ? (
            <>
              <span className="flex-1">Installe Defi Ayiti sur ton appareil pour y jouer plus vite.</span>
              <button
                type="button"
                onClick={() => void promptInstall()}
                className="shrink-0 rounded-pill bg-haiti-yellow px-3 py-1.5 font-display text-haiti-blue"
              >
                Installer
              </button>
            </>
          ) : (
            <span className="flex-1">
              Pour installer : appuie sur <strong>⬆️ Partager</strong> puis{" "}
              <strong>"Sur l'écran d'accueil"</strong>.
            </span>
          )}
          <button type="button" onClick={dismiss} aria-label="Fermer" className="shrink-0 text-lg text-white/80">
            ×
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
