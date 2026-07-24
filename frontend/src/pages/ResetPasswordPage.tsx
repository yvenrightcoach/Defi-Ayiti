import { useState } from "react";
import { motion } from "framer-motion";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import AnimatedBackground from "@/components/ui/AnimatedBackground";
import Mascot from "@/components/ui/Mascot";
import { getErrorMessage } from "@/lib/errors";
import { confirmPasswordReset } from "@/services/endpoints/auth";

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const uid = searchParams.get("uid") ?? "";
  const token = searchParams.get("token") ?? "";

  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  const linkIsValid = uid.length > 0 && token.length > 0;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (password1 !== password2) {
      setError("Les mots de passe ne correspondent pas.");
      return;
    }
    setIsSubmitting(true);
    try {
      await confirmPasswordReset(uid, token, password1, password2);
      setDone(true);
    } catch (err) {
      setError(getErrorMessage(err, "Ce lien n'est plus valide, demande-en un nouveau."));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center gap-6 p-6 text-white">
      <AnimatedBackground variant="dark" />

      <motion.div
        initial={{ opacity: 0, scale: 0.5, y: -20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "backOut" }}
        className="relative z-10 w-full max-w-sm text-center"
      >
        <Mascot className="mx-auto h-32 w-32 animate-float drop-shadow-xl" />
        <h1 className="text-toon mt-1 text-center text-4xl">Nouveau mot de passe</h1>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, delay: 0.15 }}
        className="relative z-10 w-full max-w-sm"
      >
        {!linkIsValid ? (
          <div className="card-game space-y-3 text-center text-slate-800">
            <p>Ce lien de reinitialisation est incomplet ou invalide.</p>
            <Link to="/connexion" className="btn-game-secondary block w-full">
              Retour a la connexion
            </Link>
          </div>
        ) : done ? (
          <div className="card-game space-y-3 text-center text-slate-800">
            <p>Ton mot de passe a ete change avec succes.</p>
            <button type="button" onClick={() => navigate("/connexion")} className="btn-game-primary w-full">
              Se connecter
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="card-game space-y-3 text-slate-800">
            <input
              type="password"
              placeholder="Nouveau mot de passe"
              value={password1}
              onChange={(e) => setPassword1(e.target.value)}
              className="w-full rounded-pill border border-slate-200 px-4 py-2 outline-none focus:border-haiti-blue"
              required
            />
            <input
              type="password"
              placeholder="Confirmer le mot de passe"
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
              className="w-full rounded-pill border border-slate-200 px-4 py-2 outline-none focus:border-haiti-blue"
              required
            />
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-game-primary w-full disabled:opacity-60"
            >
              {isSubmitting ? "..." : "Changer le mot de passe"}
            </button>
            {error && <p className="text-center text-sm text-haiti-red">{error}</p>}
          </form>
        )}
      </motion.div>
    </section>
  );
}
