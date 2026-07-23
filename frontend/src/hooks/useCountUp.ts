import { useEffect, useState } from "react";
import { animate } from "framer-motion";

/** Anime un nombre de 0 (ou de sa valeur precedente) jusqu'a `value`, façon compteur de jeu. */
export function useCountUp(value: number, durationSeconds = 0.8): number {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const controls = animate(0, value, {
      duration: durationSeconds,
      ease: "easeOut",
      onUpdate: (latest) => setDisplay(Math.round(latest)),
    });
    return () => controls.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return display;
}
