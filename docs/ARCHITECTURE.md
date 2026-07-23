# Architecture — Defi Ayiti

## Vue d'ensemble

```
┌──────────────────┐        HTTPS/REST         ┌───────────────────────┐
│  React PWA        │ ───────────────────────▶ │  Django REST Framework │
│  (Vite, Tailwind,  │ ◀─────────────────────── │  (config/, apps/*)     │
│  Framer Motion)    │       WebSocket (Battle)  │  + Django Channels     │
└──────────────────┘ ◀────────────────────────▶ └───────────┬───────────┘
                                                              │
                                            ┌─────────────────┼─────────────────┐
                                            ▼                 ▼                 ▼
                                     Supabase Postgres   Redis (cache,     Celery worker
                                     + Supabase Storage   Channels layer,   + Celery beat
                                                            broker Celery)   (taches planifiees)
```

- **Frontend** : PWA installable (Android/iPhone), mobile-first, appelle
  l'API REST Django et ouvre une connexion WebSocket pour les battles.
- **Backend** : Django expose l'API REST (DRF) et le temps reel (Channels).
  Celery + Redis gerent les taches asynchrones/planifiees (reset des quetes
  quotidiennes, calcul des classements hebdomadaires, fin de saison...).
- **Donnees** : Supabase heberge PostgreSQL (donnees de jeu) et Storage
  (avatars, images de heros, badges, icones de departements).
- **Deploiement** : Render heberge le web service Django (ASGI/Daphne), le
  worker Celery, Celery beat et une instance Redis managee. Supabase reste
  independant de Render.

## Structure des dossiers

### Backend (`backend/`)

```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py          # reglages communs (DRF, Channels, Celery, Supabase, CORS...)
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py               # racine des routes API (api/v1/...)
│   ├── asgi.py                # Channels (HTTP + WebSocket)
│   ├── wsgi.py
│   └── celery.py              # app Celery + planification (beat_schedule)
├── apps/
│   ├── core/                  # modeles abstraits, permissions, pagination partagees
│   ├── accounts/               # User custom + auth (email, Google, Facebook, invite)
│   ├── heroes/                  # Hero, HeroCard
│   ├── geography/                # Department (mode Aventure)
│   ├── quiz/                      # Category, Question, Answer, Level
│   ├── progress/                   # PlayerProgress
│   ├── battles/                     # Match, BattleRoom + WebSocket consumers
│   ├── social/                       # Friend
│   ├── competition/                   # Leaderboard, Season, Event
│   ├── rewards/                        # Achievement, Reward, Mission, ShopItem, Purchase
│   └── notifications/                  # Notification
├── requirements/
│   ├── base.txt / development.txt / production.txt
├── conftest.py / pytest.ini      # fixtures + config pytest-django
└── manage.py
```

Chaque app suit la meme convention : `models.py`, `serializers.py`,
`views.py`, `urls.py`, `admin.py`, `migrations/`, `tests.py`.

Le blueprint `render.yaml` vit a la racine du monorepo (pas dans `backend/`)
pour pouvoir declarer a la fois les services Python (`rootDir: backend`) et
le site statique du frontend (`rootDir: frontend`) -- voir
[RENDER_DEPLOY.md](RENDER_DEPLOY.md).

### Frontend (`frontend/`)

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/        # AppLayout (transition de page), BottomNav
│   │   └── ui/             # Loader, ErrorMessage
│   ├── features/quiz/        # QuestionCard (reutilise par QuizPage et BattlePage)
│   ├── pages/                 # une page par route
│   ├── hooks/                   # useCountUp (compteurs animes)
│   ├── store/                     # etat global (Zustand) — authStore, profileStore
│   ├── services/endpoints/          # 1 client par app backend (auth, quiz, battles...)
│   ├── lib/                           # supabaseClient, errors.ts, leagues.ts
│   ├── types/                           # types TypeScript partages (api.ts, auth.ts)
│   ├── styles/                            # index.css (Tailwind + classes de jeu)
│   ├── test/setup.ts                        # config Vitest (jest-dom)
│   ├── App.tsx                              # routes
│   └── main.tsx                              # point d'entree
├── public/icons/               # icones PWA (192/512/maskable/apple-touch)
├── vite.config.ts              # alias @, plugin PWA, config Vitest (test: {...})
└── tailwind.config.ts           # couleurs Haiti, ligues, animations de jeu
```

## Modeles de donnees (phase 2 -- termine)

Tous les modeles sont implementes et migres :

| App | Modeles |
|---|---|
| accounts | `User`, `UserProfile` |
| geography | `Department`, `Level` (chapitres d'aventure) |
| quiz | `Category`, `Question`, `Answer` |
| heroes | `Hero`, `HeroCard` |
| progress | `PlayerProgress` |
| battles | `BattleRoom`, `Match`, `MatchParticipant` |
| social | `Friend` |
| competition | `Season`, `Event`, `Leaderboard` |
| rewards | `Reward`, `Achievement`, `PlayerAchievement`, `Mission`, `PlayerMission`, `ShopItem`, `Purchase` |
| notifications | `Notification` |

`MatchParticipant`, `PlayerAchievement` et `PlayerMission` sont des tables
de jointure necessaires (score par joueur dans un match, progression par
joueur d'un achievement/d'une mission) -- non citees individuellement dans
le cahier des charges initial mais indispensables au meme titre que
`HeroCard` (qui joue ce role pour `Hero`).

Tous les modeles de jeu heritent de `apps.core.models.BaseModel` (cle
primaire UUID + `created_at`/`updated_at`).

Le modele `User` (email, Google, Facebook, mode invite) reste distinct de
`UserProfile` (XP, monnaies, ligue, serie de victoires...) : `AUTH_USER_MODEL`
doit exister des la premiere migration, `UserProfile` porte les donnees de jeu.

Une fixture (`apps/geography/fixtures/departments.json`) fournit les 10
departements officiels d'Haiti :

```bash
python manage.py loaddata departments
```

## Authentification

- Email/mot de passe et JWT via `djangorestframework-simplejwt` + `dj-rest-auth`.
- Google et Facebook via `django-allauth` (providers configures dans
  `config/settings/base.py`, cles fournies par variables d'environnement).
- Mode invite : `POST /api/v1/auth/guest/` cree un compte temporaire et
  renvoie directement une paire de jetons JWT.

## API REST (phase 3 -- termine)

Chaque app expose ses endpoints sous `/api/v1/<app>/...` via des routers DRF
(`DefaultRouter`), documentes automatiquement sur `/api/docs/` (Swagger,
genere par drf-spectacular). Points notables :

| Endpoint | Description |
|---|---|
| `POST /auth/guest/`, `/auth/register/`, `/auth/login/` | Authentification (JWT) |
| `GET/PATCH /auth/me/` | Profil de jeu du joueur connecte |
| `GET /geography/departments/{id}/` | Departement + ses chapitres (`levels`) |
| `GET /quiz/questions/` + `POST .../submit/` | Question SANS la bonne reponse ; `submit` corrige et attribue l'XP |
| `GET /heroes/heroes/` | Catalogue avec `is_unlocked` calcule pour le joueur |
| `POST /progress/entries/complete-level/` | Valide un chapitre : XP, pieces, deblocage de heros si `unlocks_hero` |
| `POST /battles/rooms/`, `.../join/`, `.../{id}/start/` | Creation de salle, jonction par code, lancement d'un match |
| `POST /battles/matches/{id}/submit-score/`, `.../finish/` | Score par joueur, cloture avec calcul du gagnant (trophees, serie) |
| `POST /social/friends/`, `.../accept/`, `.../decline/`, `.../friends/` | Systeme d'amis complet |
| `GET /competition/leaderboards/?scope=...&period=...` | Classements (alimentes par Celery beat) |
| `POST /rewards/player-missions/{id}/claim/` | Reclamation de la recompense d'une quete terminee |
| `POST /rewards/purchases/` | Achat boutique (deduction pieces/diamants) |
| `POST /notifications/notifications/{id}/mark-read/` | Marquage des notifications |

Regles transverses :
- Les questions ne renvoient jamais `is_correct`/`explanation` avant `submit/` (anti-triche cote API).
- `MatchParticipant`, `PlayerAchievement`, `PlayerMission` sont peuples/mis a jour automatiquement par les actions de jeu (reponse a une question, fin de match).
- `BattleRoom.participants` (M2M) suit qui a rejoint une salle ; `start` cree un `MatchParticipant` pour chacun.

## Temps reel (Battles)

`apps/battles/routing.py` + `apps/battles/consumers.py` sont le point
d'entree WebSocket (duels 1v1, battles entre amis, tournois). Les consumers
concrets (`DuelConsumer`, `TournamentConsumer`, ...) restent a implementer :
le flux REST actuel (creer salle/joindre/lancer/soumettre score/cloturer)
fonctionne en mode "tour par tour" via polling ; le WebSocket apportera le
temps reel (minuteur partage, notifications de progression des adversaires).

## Taches planifiees (Celery beat)

Definies dans `config/celery.py` :
- reset des quetes quotidiennes (minuit) ;
- calcul du classement hebdomadaire (lundi 00h05) ;
- verification du statut des saisons (tous les jours a 1h).

Les taches elles-memes (`apps.rewards.tasks`, `apps.competition.tasks`)
restent a implementer (elles alimenteront le modele `Leaderboard`, deja
consultable en lecture via l'API).

## Notes techniques

Django est fixe a **5.2 LTS** (et non 5.0) : sous Python 3.14, Django 5.0/5.1
plantent au rendu des templates admin (`AttributeError: 'super' object has
no attribute 'dicts'`), un probleme resolu en 5.2. `django-celery-beat` est
en consequence fixe a `2.9.0` (la 2.7.0 plafonnait `Django<5.2`).

## Roadmap des phases

1. ✅ Architecture, configuration Django, connexion Supabase, structure React
2. ✅ Modeles Django (toutes les entites listees ci-dessus) + admin + fixture departements
3. ✅ API REST (serializers + viewsets + routers DRF) -- voir tableau des endpoints ci-dessus
4. ✅ Interfaces React (mode Aventure, quiz, profil, heros, ligues, amis, battle) -- voir section ci-dessous
5. ✅ Animations supplementaires + tests automatises -- voir section ci-dessous
6. Preparation finale du deploiement (Render + Supabase en production)

## Animations et tests automatises (phase 5 -- termine)

**Animations ajoutees** (en plus des transitions Framer Motion et confettis deja
presents depuis la phase 4) :
- Transition de page (fondu + glissement) dans `AppLayout`, via `AnimatePresence`
  + `useOutlet()`/`useLocation()` a la place d'un `<Outlet />` simple.
- `hooks/useCountUp.ts` : anime un nombre de 0 jusqu'a sa valeur cible (pieces,
  diamants, trophees sur Accueil/Profil ; XP/pieces gagnes sur l'ecran de fin de
  quiz). Utilise `framer-motion`'s `animate()` en dehors du JSX.
- L'animation `coin-bounce` (definie des la phase 1 dans `tailwind.config.ts`
  mais jamais utilisee) est desormais appliquee a l'icone piece du profil.

**Bug reel trouve et corrige pendant les tests navigateur** : les appels a
`useCountUp` avaient d'abord ete places apres un `return` conditionnel dans
`HomePage` (retour anticipe pendant le chargement du profil), violant les
Rules of Hooks React ("Rendered fewer hooks than expected"). Un test Playwright
avec un profil pre-charge (donc sans passer par l'etat de chargement) a fait
crasher la page. Corrige en remontant les hooks avant tout `return`.

**Tests automatises** :
- Backend : `config/settings/test.py` isole les tests de toute dependance
  externe (sqlite en memoire, cache local, Celery en mode eager) -- `pytest`
  tourne partout sans Supabase ni Redis. 34 tests couvrant la logique metier
  reelle : invite/profil, correction de quiz + progression de quete, validation
  de chapitre + deblocage de heros, cycle de vie complet d'une battle (creation
  de salle, capacite max, cloture et recompenses), demandes d'ami, reclamation
  de mission et achats en boutique.
- Frontend : Vitest + Testing Library (jsdom). 17 tests sur `lib/errors.ts`,
  `lib/leagues.ts`, `store/authStore.ts` et le composant `QuestionCard`.
- **Bugs reels trouves grace aux tests d'integration multi-clients** (pas les
  tests unitaires eux-memes, mais leur ecriture a revele un piege reutilisable) :
  dans les premiers jets de tests `battles`/`social`, un meme `APIClient` etait
  partage entre deux "joueurs" via deux fixtures qui se resolvaient au meme
  objet ; ré-authentifier ce client comme le deuxieme joueur changeait aussi
  silencieusement l'identite du premier. Corrige en instanciant un `APIClient()`
  independant par acteur (fixture `second_client`).

## Interfaces React (phase 4 -- termine)

Structure ajoutee dans `frontend/src/` :

```
services/endpoints/    # 1 fichier par app backend (auth, geography, quiz, heroes,
                        # progress, battles, social, competition, rewards, notifications)
store/authStore.ts      # session JWT (persistee en localStorage via zustand/persist)
store/profileStore.ts    # cache du profil courant (UserProfile), rafraichi par les pages
types/api.ts              # types TypeScript miroir des serializers DRF
lib/errors.ts               # extraction de message d'erreur depuis une reponse axios
lib/leagues.ts                # libelles/couleurs des 7 ligues
features/quiz/QuestionCard.tsx # carte de question reutilisee par QuizPage et BattlePage
```

Pages connectees a l'API (plus plus de donnees factices) :

| Page | Route | Contenu |
|---|---|---|
| LoginPage | `/connexion` | Invite (fonctionnel) + email/mdp (dj-rest-auth) ; Google/Facebook en attente des cles OAuth |
| HomePage | `/` | Tableau de bord : XP/niveau, monnaies, raccourcis vers chaque mode |
| AdventureMapPage | `/aventure` | Les 10 departements + etoiles de progression |
| DepartmentDetailPage | `/aventure/:id` | Chapitres du departement, verrouilles selon la progression |
| QuizPage | `/quiz`, `/quiz/level/:levelId` | Questions -> soumission -> XP -> ecran de fin (deblocage de heros + confettis si chapitre boss) |
| ProfilePage | `/profil` | Stats completes, badge de ligue, deconnexion |
| HeroesPage | `/heros` | Collection avec etats verrouille/debloque + fiche heros |
| LeaderboardPage | `/classements` | Filtres scope (national/departement/amis) x periode |
| FriendsPage | `/amis` | Recherche par pseudo, demandes, liste d'amis |
| BattlePage | `/battle` | Creation/jonction de salle par code, lancement de match, quiz synchronise par polling, cloture avec classement |

`AppLayout` redirige automatiquement vers `/connexion` si aucun token n'est present
(garde d'authentification centralisee, pas de duplication par page).

**Bugs reels trouves et corriges pendant les tests navigateur (Playwright)** :
- `FriendsPage`, `LeaderboardPage` et `BattlePage` lisaient `profileStore.profile`
  sans jamais le rafraichir : un acces direct a l'URL (sans passer par Accueil/Profil
  au prealable) laissait `profile` a `null` et cassait silencieusement les demandes
  d'ami entrantes, le surlignage du joueur dans le classement et la detection de l'hote
  dans une battle. Corrige en appelant `refresh()` au montage de chaque page si le
  profil n'est pas deja charge.
- Dans `BattlePage`, seul l'hote recuperait les questions du match au lancement ;
  le joueur qui rejoint une salle detectait bien le changement de statut (polling)
  mais ne chargeait jamais les questions, laissant son ecran de quiz vide. Corrige en
  chargeant les questions dans le callback de polling des que `room.status` passe a
  `in_progress`, avec un `ref` pour eviter de recharger/reinitialiser le quiz de l'hote.
