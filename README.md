# Defi Ayiti

Jeu mobile web educatif et competitif sur l'histoire, les heros nationaux, la
geographie, la constitution, le civisme et la culture d'Haiti.

## Etat du projet

**Phase 1 ✅ — Architecture, configuration Django, connexion Supabase, structure React.**
**Phase 2 ✅ — Modeles Django complets (voir tableau dans docs/ARCHITECTURE.md), admin, fixture des departements.**
**Phase 3 ✅ — API REST complete (serializers, viewsets, routers DRF) pour les 10 apps, testee de bout en bout.**
**Phase 4 ✅ — Interfaces React connectees a l'API (aventure, quiz, profil, heros, ligues, amis, battle), validees dans un vrai navigateur avec deux joueurs simultanes.**
**Phase 5 ✅ — Animations supplementaires (transitions de page, compteurs animes) + suite de tests automatises (34 tests pytest-django, 17 tests Vitest).**
**Phase 6 ✅ (cote code) — Blueprint Render (5 services), icones PWA reelles, endpoint de sante, verification `check --deploy`, depot Git initialise.**

Il ne reste que le **provisionnement externe**, qui necessite tes propres
comptes (voir [docs/RENDER_DEPLOY.md](docs/RENDER_DEPLOY.md) et
[docs/SUPABASE_SETUP.md](docs/SUPABASE_SETUP.md)) :
1. Creer le projet Supabase et renseigner les vraies valeurs dans `.env`.
2. Pousser ce depot sur GitHub/GitLab (`git remote add origin ... && git push`).
3. Sur Render, **New > Blueprint** en pointant vers ce depot.
4. Renseigner les variables marquees `sync: false` dans le dashboard Render.

## Stack technique

| Domaine       | Technologies |
|---------------|--------------|
| Frontend      | React, TypeScript, Vite, Tailwind CSS, Framer Motion, PWA |
| Backend       | Django, Django REST Framework, Django Channels, Celery, Redis |
| Base de donnees | Supabase (PostgreSQL + Storage) |
| Deploiement   | Render (Web Service, Worker Celery, Redis) + Supabase |
| Authentification | Email/mot de passe, Google, Facebook, Mode invite |

## Structure du monorepo

```
ewonouyo/
├── backend/     # API Django (voir backend/README.md)
├── frontend/    # PWA React (voir frontend/README.md)
└── docs/        # Architecture, setup Supabase, deploiement Render
```

## Demarrage rapide

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements/development.txt
copy .env.example .env          # puis renseigner les valeurs Supabase/Redis
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env.local    # puis renseigner VITE_API_BASE_URL, Supabase...
npm run dev
```

L'application est servie sur `http://localhost:5173` et consomme l'API sur
`http://localhost:8000/api/v1`.

## Tests

Aucune dependance externe requise (Supabase/Redis) : les deux suites tournent
en local avec une base en memoire / un cache local.

```bash
# Backend (34 tests) -- utilise config/settings/test.py (sqlite en memoire)
cd backend && python -m pytest

# Frontend (17 tests) -- Vitest + Testing Library
cd frontend && npm test
```

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — architecture complete, apps Django, structure React, roadmap des phases
- [docs/SUPABASE_SETUP.md](docs/SUPABASE_SETUP.md) — configuration de Supabase (base de donnees + storage)
- [docs/RENDER_DEPLOY.md](docs/RENDER_DEPLOY.md) — deploiement du backend sur Render
