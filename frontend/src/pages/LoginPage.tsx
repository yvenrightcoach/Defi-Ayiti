import { useState } from "react";
import { motion } from "framer-motion";
import { Navigate, useNavigate } from "react-router-dom";

import { emailLogin, emailRegister, guestLogin } from "@/services/endpoints/auth";
import { getErrorMessage } from "@/lib/errors";
import { useAuthStore } from "@/store/authStore";
import Mascot from "@/components/ui/Mascot";

export default function LoginPage() {
  const navigate = useNavigate();
  const accessToken = useAuthStore((state) => state.accessToken);
  const setSession = useAuthStore((state) => state.setSession);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [loadingAction, setLoadingAction] = useState<"guest" | "email" | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (accessToken) {
    return <Navigate to="/" replace />;
  }

  function switchMode(nextMode: "login" | "register") {
    setMode(nextMode);
    setError(null);
    setPassword("");
    setPassword2("");
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

  async function handleRegister(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (password !== password2) {
      setError("Les mots de passe ne correspondent pas.");
      return;
    }
    setLoadingAction("email");
    try {
      const { access, refresh, user } = await emailRegister({
        username,
        email,
        password1: password,
        password2,
      });
      setSession({
        accessToken: access,
        refreshToken: refresh,
        user: { id: user.pk, username: user.username, email: user.email, isGuest: false },
      });
      navigate("/", { replace: true });
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de creer le compte."));
    } finally {
      setLoadingAction(null);
    }
  }

  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center gap-6 overflow-hidden bg-gradient-to-b from-haiti-blue to-haiti-blueDark p-6 text-white">
      {/* Bulles decoratives en fond, style "aire de jeu" */}
      <div className="pointer-events-none absolute -left-12 -top-12 h-40 w-40 rounded-full bg-haiti-yellow/20 blur-2xl" />
      <div className="pointer-events-none absolute -right-16 top-16 h-56 w-56 rounded-full bg-haiti-red/20 blur-2xl" />
      <div className="pointer-events-none absolute bottom-0 left-1/2 h-64 w-64 -translate-x-1/2 rounded-full bg-haiti-green/10 blur-3xl" />

      <motion.div
        initial={{ opacity: 0, scale: 0.5, y: -20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "backOut" }}
        className="relative z-10 w-full max-w-sm text-center"
      >
        <Mascot className="mx-auto h-32 w-32 animate-float drop-shadow-xl" />
        <h1 className="mt-1 text-center font-display text-4xl font-extrabold drop-shadow-sm">Defi Ayiti</h1>
        <p className="mt-1 text-center font-display text-lg text-haiti-yellow">
          Connecte-toi pour commencer l'aventure
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, delay: 0.15 }}
        className="relative z-10 w-full max-w-sm"
      >
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

        <form
          onSubmit={mode === "login" ? handleEmailLogin : handleRegister}
          className="card-game space-y-3 text-slate-800"
        >
          <input
            type="text"
            placeholder="Nom d'utilisateur"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full rounded-pill border border-slate-200 px-4 py-2 outline-none focus:border-haiti-blue"
            required
          />
          {mode === "register" && (
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-pill border border-slate-200 px-4 py-2 outline-none focus:border-haiti-blue"
              required
            />
          )}
          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-pill border border-slate-200 px-4 py-2 outline-none focus:border-haiti-blue"
            required
          />
          {mode === "register" && (
            <input
              type="password"
              placeholder="Confirmer le mot de passe"
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
              className="w-full rounded-pill border border-slate-200 px-4 py-2 outline-none focus:border-haiti-blue"
              required
            />
          )}
          <button
            type="submit"
            disabled={loadingAction !== null}
            className="btn-game-secondary w-full disabled:opacity-60"
          >
            {loadingAction === "email"
              ? mode === "login"
                ? "Connexion..."
                : "Creation..."
              : mode === "login"
                ? "Se connecter"
                : "Creer mon compte"}
          </button>
        </form>

        <button
          type="button"
          onClick={() => switchMode(mode === "login" ? "register" : "login")}
          disabled={loadingAction !== null}
          className="mt-3 w-full text-center text-sm text-white/80 underline-offset-2 hover:underline disabled:opacity-60"
        >
          {mode === "login" ? "Pas de compte ? Inscris-toi" : "Deja un compte ? Connecte-toi"}
        </button>

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
