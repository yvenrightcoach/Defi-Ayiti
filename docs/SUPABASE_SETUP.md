# Configuration Supabase — Defi Ayiti

## 1. Creer le projet

1. Sur [supabase.com](https://supabase.com), creer un nouveau projet (region
   proche de vos utilisateurs, ex. `us-east-1`).
2. Noter le mot de passe de la base de donnees choisi a la creation.

## 2. Base de donnees PostgreSQL

1. Aller dans **Project Settings > Database > Connection string > URI**.
2. Utiliser de preference le **connection pooler** (port `6543`, mode
   `transaction`) plutot que la connexion directe (port `5432`), car Render
   ouvre potentiellement plusieurs workers/connexions simultanees.
3. Copier l'URI dans `backend/.env` :

   ```
   DATABASE_URL=postgres://postgres:VOTRE_MDP@db.xxxxxxxxxxxx.supabase.co:6543/postgres
   ```

4. Une fois les modeles Django crees (phase 2), appliquer les migrations :

   ```bash
   python manage.py migrate
   ```

## 3. Storage (avatars, heros, badges, drapeaux)

1. Aller dans **Storage** et creer un bucket `defi-ayiti-media` (public en
   lecture, ecriture restreinte a la service role key).
2. Organiser les dossiers a l'interieur du bucket, par exemple :
   ```
   defi-ayiti-media/
   ├── avatars/
   ├── heroes/
   ├── badges/
   ├── departments/
   └── frames/
   ```
3. Recuperer les cles S3 compatibles : **Storage > S3 Access Keys > New
   access key**. Renseigner dans `backend/.env` :

   ```
   SUPABASE_S3_ACCESS_KEY_ID=...
   SUPABASE_S3_SECRET_ACCESS_KEY=...
   SUPABASE_S3_ENDPOINT_URL=https://xxxxxxxxxxxx.supabase.co/storage/v1/s3
   SUPABASE_S3_REGION=us-east-1
   SUPABASE_STORAGE_BUCKET=defi-ayiti-media
   ```

   Django utilise `django-storages` (backend S3) pour uploader/lire les
   fichiers via cette API compatible S3 — voir `USE_SUPABASE_STORAGE` dans
   `config/settings/base.py`.

## 4. Cles API (frontend)

Dans **Project Settings > API**, copier :
- `Project URL` → `VITE_SUPABASE_URL` (frontend) et `SUPABASE_URL` (backend)
- `anon public` key → `VITE_SUPABASE_ANON_KEY` (frontend) et `SUPABASE_ANON_KEY` (backend)
- `service_role` key → **uniquement** `SUPABASE_SERVICE_ROLE_KEY` cote
  backend. Ne jamais l'exposer au frontend.

## 5. Securite

- Le frontend n'utilise que la cle `anon` (lecture publique de ressources
  Storage). Toute logique de jeu (XP, pieces, resultats de match) passe par
  l'API Django, qui seule detient la `service_role` key.
- Activer **Row Level Security (RLS)** sur les tables si elles sont un jour
  interrogees directement depuis le frontend (non prevu dans l'architecture
  actuelle, ou Django reste l'unique point d'acces aux donnees de jeu).
