const SPARKLES = [
  { top: "8%", left: "12%", size: "text-lg", delay: "0s" },
  { top: "18%", left: "82%", size: "text-2xl", delay: "0.4s" },
  { top: "34%", left: "6%", size: "text-sm", delay: "1.1s" },
  { top: "52%", left: "90%", size: "text-lg", delay: "0.7s" },
  { top: "68%", left: "20%", size: "text-2xl", delay: "1.6s" },
  { top: "78%", left: "70%", size: "text-sm", delay: "0.2s" },
  { top: "90%", left: "40%", size: "text-lg", delay: "1.3s" },
  { top: "12%", left: "50%", size: "text-sm", delay: "0.9s" },
];

interface AnimatedBackgroundProps {
  variant?: "light" | "dark";
}

/**
 * Fond anime persistant (bulles colorees a la derive + etincelles qui
 * clignotent), a la Duolingo -- toujours en mouvement plutot qu'une
 * image statique. z-index negatif : ne capte jamais les clics et reste
 * derriere le contenu quel que soit l'ordre du DOM.
 */
export default function AnimatedBackground({ variant = "light" }: AnimatedBackgroundProps) {
  const blobOpacity = variant === "light" ? "opacity-30" : "opacity-25";

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden" aria-hidden="true">
      <div className={`absolute inset-0 ${variant === "light" ? "bg-haiti-blueLight" : "bg-haiti-blue"}`} />

      <div
        className={`absolute -left-16 -top-16 h-72 w-72 rounded-full bg-haiti-blue blur-3xl ${blobOpacity} animate-drift-1`}
      />
      <div
        className={`absolute -right-20 top-10 h-80 w-80 rounded-full bg-haiti-red blur-3xl ${blobOpacity} animate-drift-2`}
      />
      <div
        className={`absolute -left-10 bottom-0 h-64 w-64 rounded-full bg-haiti-green blur-3xl ${blobOpacity} animate-drift-3`}
      />
      <div
        className={`absolute -right-10 bottom-10 h-56 w-56 rounded-full bg-haiti-yellow blur-3xl ${blobOpacity} animate-drift-1`}
      />
      <div
        className={`absolute left-1/3 top-1/2 h-48 w-48 rounded-full bg-haiti-yellow blur-3xl ${blobOpacity} animate-drift-2`}
      />

      {SPARKLES.map((s, i) => (
        <span
          key={i}
          className={`absolute animate-twinkle ${s.size} ${
            variant === "light" ? "text-haiti-yellowDark/70" : "text-white/70"
          }`}
          style={{ top: s.top, left: s.left, animationDelay: s.delay }}
        >
          ✦
        </span>
      ))}
    </div>
  );
}
