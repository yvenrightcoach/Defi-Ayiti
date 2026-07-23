import { createClient } from "@supabase/supabase-js";

/**
 * Client Supabase cote frontend.
 * Utilise uniquement la cle publique "anon" (jamais la service role key,
 * qui reste strictement cote serveur Django).
 * Sert principalement a lire des URLs Supabase Storage (avatars, badges,
 * images de heros) ; l'authentification et les donnees de jeu passent par
 * l'API Django (voir services/apiClient.ts).
 */
export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY,
);
