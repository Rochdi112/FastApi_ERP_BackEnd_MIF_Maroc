<h1 align="center">ERP MIF Maroc — Backend FastAPI</h1>
<p align="center"><em>Sabir Rochdi — MIF Maroc</em></p>

<p align="center">
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-blue.svg"></a>
  <a href="https://fastapi.tiangolo.com/"><img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.116-009688.svg"></a>
  <a href="https://www.sqlalchemy.org/"><img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-red.svg"></a>
  <a href="https://www.postgresql.org/"><img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16-336791.svg"></a>
  <a href="https://www.docker.com/"><img alt="Docker" src="https://img.shields.io/badge/Docker-ready-2496ED.svg"></a>
  <a href="#api-openapi"><img alt="OpenAPI" src="https://img.shields.io/badge/OpenAPI-3.0-green.svg"></a>
</p>

Plateforme backend moderne pour la gestion des interventions industrielles: authentification JWT, RBAC, gestion des utilisateurs/techniciens/équipements, interventions et planning, notifications, et documents. Prêt pour la prod (Docker), migrations Alembic, export OpenAPI pour le front.

---

## Sommaire

- Aperçu rapide
- Architecture & fonctionnalités
- Structure du projet
- Prérequis
- Démarrage (Docker / local / VS Code)
- Configuration (.env)
- Base de données (migrations, seed)
- API & OpenAPI
- Développement quotidien (tâches utiles)
- Sécurité, CORS & uploads
- Déploiement
- Dépannage rapide (FAQ)
- Licence

---

## Aperçu rapide

- Base API: `http://localhost:8000` (préfixe REST: `/api/v1`)
- Documentation: `/docs` (Swagger) et `/redoc`
- Santé: `GET /health` → `{ "status": "ok" }`
- Fichiers statiques: `/static/uploads` (public)

---

## Architecture & fonctionnalités

Caractéristiques clés:

- Authentification JWT, hachage mots de passe (passlib[bcrypt])
- RBAC: rôles `admin`, `responsable`, `technicien`, `client`
- SQLAlchemy 2.0 + Alembic (migrations), Pydantic v2 (schemas)
- Uploads de documents (servis sous `/static/uploads`)
- Notifications email (fastapi-mail), tâches planifiées (APScheduler)
- Export OpenAPI pour générer SDK front

Aperçu architecture (simplifié):

```
┌──────────────┐   JWT   ┌──────────────┐
│ Front (Web)  │◀──────▶│  API REST     │
└──────────────┘        │  FastAPI      │
                        ├───────────────┤
                        │ Services      │
                        │ (logic métier)│
                        ├───────────────┤
                        │ SQLAlchemy ORM│
                        └──────┬────────┘
                               │
                         ┌─────▼─────┐
                         │ PostgreSQL │
                         └───────────┘
```

---

## Structure du projet

```
app/
  main.py               # App FastAPI, CORS, statique, routes
  api/v1/               # Endpoints REST par domaine
  core/                 # Config (pydantic-settings), sécurité, RBAC, exceptions
  db/                   # Engine, SessionLocal, Base, migrations Alembic
  models/               # ORM SQLAlchemy
  schemas/              # Schémas Pydantic v2
  services/             # Logique métier
  tasks/                # Scheduler & tâches
  seed/                 # Données d'initialisation (optionnel)
  static/               # Monté en /static (incl. uploads/)
templates/              # Templates email
scripts/                # Outils (export OpenAPI, AST fallback, etc.)
Dockerfile, docker-compose.yml, alembic.ini, requirements.txt, pyproject.toml
```

---

## Prérequis

- Windows 10/11, macOS ou Linux
- Python 3.11+
- Docker Desktop (pour l’option Docker)
- VS Code recommandé (tâches intégrées), Git

---

## Démarrage

### Option A — Docker Compose (recommandé)

1) Créez un `.env` à la racine (voir section Configuration).  
2) Lancez:

```bash
docker compose up --build -d
```

Le backend attend Postgres, applique `alembic upgrade head`, puis démarre Uvicorn sur `0.0.0.0:8000`.

### Option B — Local (Windows PowerShell)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
# Démarrer Postgres (via Docker) avant Alembic
docker compose up -d db
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Remarque: hors Docker, Alembic nécessite un Postgres accessible (sinon l’application bascule en SQLite en mémoire pour l’exécution, mais les migrations échoueront).

### Option C — Tâches VS Code (Windows)

- Python: Create venv & Install — crée `.venv` et installe les dépendances
- DB: Alembic upgrade head — applique les migrations
- Dev: Run FastAPI (reload) — lance Uvicorn en mode reload
- Tests: run — exécute la suite de tests si présents
- OpenAPI: export (ast fallback) — export approximatif via analyse statique

Palette de commandes → “Run Task” → choisir la tâche souhaitée.

---

## Configuration (.env)

Variables principales (valeurs par défaut en dev dans `app/core/config.py`):

- `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `UPLOAD_DIRECTORY` (défaut: `app/static/uploads`)
- `CORS_ALLOW_ORIGINS` (liste JSON d’origines autorisées)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAILS_FROM_EMAIL`

Exemple minimal:

```dotenv
SECRET_KEY=change-me
POSTGRES_USER=erp_user
POSTGRES_PASSWORD=erp_pass
POSTGRES_DB=erp_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
UPLOAD_DIRECTORY=app/static/uploads
CORS_ALLOW_ORIGINS=["http://localhost:3000","http://localhost:8000"]
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=user
SMTP_PASSWORD=password
EMAILS_FROM_EMAIL=no-reply@example.com
```

Validation rapide:

```bash
python validate_env.py
```

---

## Base de données

Migrations Alembic:

```bash
alembic upgrade head
```

Données de seed (optionnel pour démo):

```bash
python app/seed/seed_data.py
```

---

## API & OpenAPI

Documentation interactive: `http://localhost:8000/docs` et `http://localhost:8000/redoc`.

Export du contrat OpenAPI:

- Runtime complet (recommandé):

```powershell
. .\.venv\Scripts\Activate.ps1; $env:ENV='test'; $env:DATABASE_URL='sqlite:///:memory:'; .\.venv\Scripts\python.exe scripts/openapi_export_runtime.py
```

Le fichier `openapi.json` est généré à la racine. Ce mode évite les problèmes de quoting PowerShell.

- Fallback AST (approximation):

```powershell
. .\.venv\Scripts\Activate.ps1; .\.venv\Scripts\python.exe scripts/openapi_export.py | Out-File -FilePath openapi.generated.json -Encoding utf8
```

Handoff Frontend:

- Base URL: `http://localhost:8000/api/v1`
- Utilisez `openapi.json` pour générer types/clients (openapi-typescript, Orval, Swagger Codegen, etc.)

---

## Développement quotidien

Commandes utiles (Makefile):

- `make install` — installer les dépendances
- `make validate` — valider l’environnement
- `make migrate` — appliquer les migrations (démarre `db` via Docker si nécessaire)
- `make serve` — démarrer Uvicorn en reload
- `make format` / `make lint` — qualité de code
- `make report` — générer un rapport projet
- `make docker-build` / `make docker-run` — construire/lancer via Docker

Tâches VS Code équivalentes sont fournies pour Windows.

---

## Sécurité, CORS & uploads

- JWT: auth Bearer à partir de `POST /api/v1/auth/token` (form-data: `email`, `password`)
- CORS: configurez `CORS_ALLOW_ORIGINS` pour le front
- Uploads: `POST /api/v1/documents/` → accès public via `/static/uploads/...`
- Notifications: templates sous `templates/`, envoi via fastapi-mail
- Tâches planifiées: APScheduler (activable via configuration)

---

## Déploiement

- Dockerfile + docker-compose.yml prêts: applique migrations puis lance Uvicorn
- Volumes: base Postgres + `static/uploads`
- Placez un reverse proxy (nginx/traefik), activez HTTPS, et injectez les secrets via variables d’environnement
- Exemple de config proxy: `deploy/nginx.sample.conf`

---

## Dépannage rapide (FAQ)

- Alembic échoue en local: démarrez `docker compose up -d db` ou configurez un Postgres local; hors Docker, l’app peut basculer en SQLite en mémoire (exécution OK, migrations KO)
- Export OpenAPI qui échoue dans PowerShell: utilisez `scripts/openapi_export_runtime.py` (gère le quoting)
- Fichiers `/static/uploads` non servis: vérifiez `UPLOAD_DIRECTORY` et le montage `/static` dans `app/main.py`
- CORS: ajustez `CORS_ALLOW_ORIGINS` pour inclure l’URL du front

---

## Licence

© 2025 MIF Maroc — Tous droits réservés. Licence à définir.

# FastApi_ERP_BackEnd_MIF_Maroc
