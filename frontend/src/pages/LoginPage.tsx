import { useState } from "react";
import { motion } from "framer-motion";
import { Navigate, useNavigate } from "react-router-dom";

import { emailLogin, guestLogin } from "@/services/endpoints/auth";
import { getErrorMessage } from "@/lib/errors";
import { useAuthStore } from "@/store/authStore";

export default function LoginPage() {
  const navigate = useNavigate();
  const accessToken = useAuthStore((state) => state.accessToken);
  const setSession = useAuthStore((state) => state.setSession);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loadingAction, setLoadingAction] = useState<"guest" | "email" | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (accessToken) {
    return <Navigate to="/" replace />;
  }

  async function handleGuestLogin() {
    setError(null);
    setLoadingAction("guest");
    try {
      const { access, refresh, user } = await guestLogin();
      setSession({
        accessToken: access,
        refreshToken: refresh,
        user: { id: user.id, username: user.username, isGuest: user.is_guest },
      });
      navigate("/", { replace: true });
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de creer une session invite pour le moment."));
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleEmailLogin(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setLoadingAction("email");
    try {
      const { access, refresh, user } = await emailLogin(username, password);
      setSession({
        accessToken: access,
        refreshToken: refresh,
        user: { id: user.pk, username: user.username, email: user.email, isGuest: false },
      });
      navigate("/", { replace: true });
    } catch (err) {
      setError(getErrorMessage(err, "Identifiants incorrects."));
    } finally {
      setLoadingAction(null);
    }
  }

  return (
    <section className="flex min-h-screen flex-col items-center justify-center gap-6 bg-haiti-blue p-6 text-white">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="w-full max-w-sm"
      >
        <h1 className="mb-1 text-center text-3xl font-display">Defi Ayiti</h1>
        <p className="mb-6 text-center text-haiti-yellow">Connecte-toi pour commencer l'aventure</p>

        <button
          type="button"
          onClick={handleGuestLogin}
          disabled={loadingAction !== null}
          className="btn-game-primary mb-4 w-full disabled:opacity-60"
        >
          {loadingAction === "guest" ? "Creation..." : "Jouer en mode invite"}
        </button>

        <div className="mb-4 flex items-center gap-3 text-white/60">
          <span className="h-px flex-1 bg-white/20" />
          <span className="text-xs">ou avec un compte</span>
          <span className="h-px flex-1 bg-white/20" />
        </div>

        <form onSubmit={handleEmailLogin} className="card-game space-y-3 text-slate-800">
          <input
            type="text"
            placeholder="Nom d'utilisateur"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full rounded-pill border border-slate-200 px-4 py-2 outline-none focus:border-haiti-blue"
            required
          />
          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-pill border border-slate-200 px-4 py-2 outline-none focus:border-haiti-blue"
            required
          />
          <button
            type="submit"
            disabled={loadingAction !== null}
            className="btn-game-secondary w-full disabled:opacity-60"
          >
            {loadingAction === "email" ? "Connexion..." : "Se connecter"}
          </button>
        </form>

        {error && <p className="mt-4 text-center text-sm text-haiti-yellow">{error}</p>}

        <div className="mt-6 flex justify-center gap-3 opacity-60">
          <button type="button" disabled className="btn-game bg-white/10 text-white text-sm">
            Google (bientot)
          </button>
          <button type="button" disabled className="btn-game bg-white/10 text-white text-sm">
            Facebook (bientot)
          </button>
        </div>
      </motion.div>
    </section>
  );
}
