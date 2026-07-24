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
    <nav className="safe-area-bottom flex justify-center px-3 pb-3">
      <div className="flex w-full max-w-md justify-around rounded-card border-2 border-slate-100 bg-white/95 px-1 py-2 shadow-card backdrop-blur">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex flex-col items-center gap-0.5 rounded-2xl px-3 py-1 font-display text-xs transition-all duration-150 ${
                isActive
                  ? "-translate-y-1 bg-haiti-blueLight text-haiti-blue"
                  : "text-slate-400 hover:text-haiti-blue/70"
              }`
            }
          >
            {({ isActive }) => (
              <>
                <span
                  className={`text-xl transition-transform duration-150 ${isActive ? "scale-125" : "scale-100"}`}
                  aria-hidden="true"
                >
                  {item.icon}
                </span>
                <span className={isActive ? "font-extrabold" : ""}>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
