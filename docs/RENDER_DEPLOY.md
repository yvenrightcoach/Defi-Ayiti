# Deploiement Render — Defi Ayiti

Le blueprint `render.yaml` (a la racine du depot) decrit 5 services Render :
API Django, worker Celery, Celery beat, frontend statique et Redis. Supabase
reste externe a Render (voir [SUPABASE_SETUP.md](SUPABASE_SETUP.md)).

## 1. Pre-requis

- Depot Git pousse sur GitHub/GitLab (Render deploie a partir d'un repo).
- Projet Supabase configure (DATABASE_URL, cles Storage) -- voir
  [SUPABASE_SETUP.md](SUPABASE_SETUP.md).
- Si authentification sociale : applications OAuth Google/Facebook creees
  (voir section 5).

## 2. Creer les services via le Blueprint

1. Sur [dashboard.render.com](https://dashboard.render.com), **New >
   Blueprint**, pointer vers ce depot. Render detecte automatiquement
   `render.yaml` a la racine.
2. Render cree :
   - `defi-ayiti-api` — web service ASGI (Daphne), REST + WebSocket
   - `defi-ayiti-celery-worker` — worker Celery
   - `defi-ayiti-celery-beat` — planificateur Celery beat
   - `defi-ayiti-app` — site statique (PWA React, build Vite)
   - `defi-ayiti-redis` — instance Redis (cache, Channels layer, broker)

   Chaque service Python utilise `rootDir: backend` et le site statique
   `rootDir: frontend`, donc les commandes de build s'executent dans le bon
   sous-dossier du monorepo.

> Les noms exacts de certaines cles du blueprint (notamment `runtime: static`
> pour un site statique) peuvent evoluer avec les versions du format Render.
> Si le dashboard signale une cle inconnue au moment du deploiement, se
> referer a la documentation a jour : https://render.com/docs/blueprint-spec

## 3. Variables d'environnement a renseigner manuellement

Toutes les variables marquees `sync: false` dans `render.yaml` doivent etre
saisies dans le dashboard apres la creation du blueprint.

**`defi-ayiti-api`** (a dupliquer sur les deux workers Celery pour
`DATABASE_URL`/`SUPABASE_*`) :

| Variable | Valeur |
|---|---|
| `DJANGO_SECRET_KEY` | generer une valeur aleatoire forte (ex. `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DATABASE_URL` | URI Supabase (pooler, port 6543) |
| `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | valeurs du projet Supabase |
| `DJANGO_ALLOWED_HOSTS` | domaine Render de l'API, ex. `defi-ayiti-api.onrender.com` |
| `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS` | URL du site statique `defi-ayiti-app`, ex. `https://defi-ayiti-app.onrender.com` |
| `GOOGLE_OAUTH_CLIENT_ID` / `_SECRET`, `FACEBOOK_OAUTH_CLIENT_ID` / `_SECRET` | cles OAuth (optionnel) |

`REDIS_URL` est deja cablee automatiquement via `fromService` pour les 3
services Python.

**`defi-ayiti-app`** (frontend) :

| Variable | Valeur |
|---|---|
| `VITE_API_BASE_URL` | `https://<domaine-render-api>/api/v1` |
| `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` | valeurs publiques du projet Supabase |
| `VITE_GOOGLE_CLIENT_ID`, `VITE_FACEBOOK_APP_ID` | cles OAuth cote client (optionnel) |

## 4. Migrations

La `buildCommand` du service `defi-ayiti-api` execute deja
`python manage.py migrate` a chaque deploiement. Pour une migration
ponctuelle manuelle ou creer un superutilisateur : **Render Dashboard >
defi-ayiti-api > Shell**.

## 5. Authentification sociale (optionnel)

- **Google** : [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
  > creer un "OAuth client ID" de type application web, avec comme URI de
  redirection autorisee `https://<domaine-render-api>/api/v1/auth/social/google/callback/`.
- **Facebook** : [developers.facebook.com](https://developers.facebook.com/apps)
  > creer une app, activer "Facebook Login", meme principe d'URI de
  redirection.

Sans ces cles, l'application reste pleinement fonctionnelle : email/mot de
passe et mode invite suffisent (les boutons Google/Facebook sont desactives
cote frontend tant que les cles `VITE_GOOGLE_CLIENT_ID`/`VITE_FACEBOOK_APP_ID`
ne sont pas renseignees).

## 6. Verification post-deploiement

- `GET https://<domaine-render-api>/healthz/` — verification de sante (utilisee par Render)
- `GET https://<domaine-render-api>/api/docs/` — documentation Swagger de l'API
- `GET https://<domaine-render-api>/admin/` — interface d'administration Django
- `POST https://<domaine-render-api>/api/v1/auth/guest/` — tester le mode invite
- Ouvrir `https://<domaine-render-app>/` — l'application doit se charger et
  permettre une connexion invite de bout en bout

## 7. Alternative frontend : Vercel / Netlify

Le service `defi-ayiti-app` du blueprint est une option parmi d'autres.
Vercel ou Netlify fonctionnent tout aussi bien pour une PWA Vite : build
command `npm run build`, dossier de sortie `frontend/dist`, meme variables
`VITE_*`. Ces plateformes ajoutent au passage CDN/edge caching, ce qui peut
ameliorer les temps de chargement sur mobile.
