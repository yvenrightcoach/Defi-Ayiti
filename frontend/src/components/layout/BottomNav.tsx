import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Accueil", icon: "🏠" },
  { to: "/aventure", label: "Aventure", icon: "🗺️" },
  { to: "/quiz", label: "Quiz", icon: "❓" },
  { to: "/battle", label: "Battle", icon: "⚔️" },
  { to: "/profil", label: "Profil", icon: "👤" },
];

export default function BottomNav() {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-50 flex justify-around border-t border-haiti-blue/10 bg-white/95 py-2 backdrop-blur safe-area-bottom">
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `flex flex-col items-center gap-0.5 px-2 py-1 text-xs font-display transition-colors ${
              isActive ? "text-haiti-blue" : "text-slate-400"
            }`
          }
        >
          <span className="text-lg" aria-hidden="true">
            {item.icon}
          </span>
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
