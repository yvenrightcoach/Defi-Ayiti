interface MascotProps {
  className?: string;
}

/**
 * "Ti Kok" -- mascotte maison de Defi Ayiti, un jeune coq stylise (symbole
 * populaire haitien) dans les couleurs du drapeau. Dessine en formes
 * simples pour rester leger (pas d'asset image a charger).
 */
export default function Mascot({ className = "" }: MascotProps) {
  return (
    <svg
      viewBox="0 0 200 200"
      className={className}
      role="img"
      aria-label="Ti Kok, la mascotte de Defi Ayiti"
    >
      {/* Ombre au sol */}
      <ellipse cx="100" cy="182" rx="46" ry="8" fill="#00265A" opacity="0.12" />

      {/* Queue */}
      <path
        d="M138 108 C 172 88, 176 54, 156 34 C 166 62, 158 84, 132 100 Z"
        fill="#D21034"
      />
      <path
        d="M132 100 C 158 78, 160 48, 142 30 C 148 56, 142 76, 118 96 Z"
        fill="#FFD447"
      />

      {/* Corps */}
      <ellipse cx="100" cy="122" rx="52" ry="48" fill="#0057B8" />
      <ellipse cx="86" cy="140" rx="30" ry="22" fill="#FFFFFF" opacity="0.9" />

      {/* Aile */}
      <path
        d="M64 108 C 48 118, 46 144, 66 156 C 58 138, 62 118, 78 108 Z"
        fill="#003D82"
      />

      {/* Tete */}
      <circle cx="112" cy="70" r="34" fill="#0057B8" />

      {/* Crete */}
      <path
        d="M96 40 C 92 26, 102 22, 104 32 C 108 20, 120 22, 116 34 C 124 26, 132 32, 124 42 Z"
        fill="#D21034"
      />

      {/* Barbillon */}
      <path d="M124 84 C 132 86, 134 96, 126 100 C 126 92, 122 88, 118 86 Z" fill="#D21034" />

      {/* Bec */}
      <path d="M140 68 L 156 74 L 140 80 Z" fill="#FFD447" />

      {/* Oeil */}
      <circle cx="122" cy="66" r="6" fill="#00131F" />
      <circle cx="124" cy="64" r="2" fill="#FFFFFF" />

      {/* Joue */}
      <circle cx="104" cy="78" r="6" fill="#D21034" opacity="0.35" />

      {/* Pattes */}
      <path d="M90 168 L 86 184 M90 168 L 94 184 M90 168 L 98 180" stroke="#FFD447" strokeWidth="4" strokeLinecap="round" />
      <path d="M112 168 L 108 184 M112 168 L 116 184 M112 168 L 120 180" stroke="#FFD447" strokeWidth="4" strokeLinecap="round" />
    </svg>
  );
}
