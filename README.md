<h1 align="center">ERP MIF Maroc — Backend FastAPI</h1>
<p align="center"><em>Par : Sabir Rochdi</em></p>

<p align="center">
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-blue.svg"></a>
  <a href="https://fastapi.tiangolo.com/"><img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg"></a>
  <a href="https://www.postgresql.org/"><img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16%2B-336791.svg"></a>
  <a href="#tests--couverture"><img alt="Tests" src="https://img.shields.io/badge/tests-pytest%20%2B%20coverage-brightgreen.svg"></a>
</p>

Plateforme backend pour la gestion des interventions industrielles. Authentification JWT, RBAC, gestion des utilisateurs/techniciens/équipements, interventions et planning, notifications et documents. Prête pour la production (Docker), migrations Alembic et tests automatisés.

---

## Sommaire

* Aperçu rapide
* Technologies & fonctionnalités
* Structure du projet
* Démarrage (Docker / local / tâches VS Code)
* Configuration (.env)
* Migrations & données de seed
* Tests & couverture
* Intégration Frontend
* Déploiement
* Dépannage rapide
* Crédits & licence

---

## Aperçu rapide

* Base API : `http://localhost:8000` (versionnée sous `/api/v1`)
* Documentation : `/docs` (Swagger) et `/redoc`
* Santé : `GET /health` → `{"status":"ok"}`
* Racine : `GET /`
* Fichiers statiques : `/static/uploads`

---

## Technologies & fonctionnalités

**Stack**

* FastAPI, Uvicorn, SQLAlchemy 2.0, Alembic, Pydantic v2
* PostgreSQL (prod) / SQLite (tests)

**Sécurité**

* Authentification JWT (`python-jose`)
* Mots de passe hachés (`passlib[bcrypt]`)
* RBAC intégré : `admin`, `responsable`, `technicien`, `client`

**Opérations**

* APScheduler pour les tâches planifiées
* Upload de fichiers et envoi d’e-mails (`fastapi-mail`)

---

## Structure du projet

```
app/
  main.py               # App FastAPI, CORS, statique, routes, lifespan
  api/v1/               # Endpoints REST par domaine
  core/                 # Config, sécurité, rbac, exceptions
  db/                   # Engine, session, Base
  models/               # ORM SQLAlchemy
  schemas/              # Schémas Pydantic v2
  services/             # Logique métier
  tasks/                # Tâches planifiées / utilitaires asynchrones
  seed/                 # Données d'initialisation
  tests/                # Suite de tests
static/uploads/
```

Fichiers utiles : `Dockerfile`, `docker-compose.yml`, `alembic.ini`, `migration.sql`, `openapi.json`, `openapi.generated.json`, `frontend_contract.json`, `validate_env.py`, `generate_report.py`, `deploy/nginx.sample.conf`.

---

## Démarrage

### Option A — Docker Compose (recommandé)

1. Créer `.env` (copie de `.env.example` si présent).
2. Lancer :

```bash
docker compose up --build -d
```

Le backend attend Postgres, applique `alembic upgrade head`, puis démarre Uvicorn sur `0.0.0.0:8000`.

### Option B — En local (Windows PowerShell)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option C — Tâches VS Code (Windows)

* **Python: Create venv & Install** — crée `.venv` et installe les dépendances
* **DB: Alembic upgrade head** — applique les migrations
* **Dev: Run FastAPI (reload)** — lance Uvicorn en mode reload
* **Tests: run** — exécute la suite de tests

Palette de commandes → “Run Task” → choisir la tâche.

---

## Configuration (.env)

Variables clés :

* `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
* `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
* `CORS_ALLOW_ORIGINS` (JSON array)
* `UPLOAD_DIRECTORY` (défaut : `app/static/uploads`)
* `SMTP_*`, `EMAILS_FROM_EMAIL`

Validation optionnelle :

```bash
python validate_env.py
```

---

## Migrations & données de seed

Appliquer les migrations :

```bash
alembic upgrade head
```

Charger des données d’exemple (optionnel) :

```bash
python app/seed/seed_data.py
```

---

## Tests & couverture

Exécuter les tests :

```bash
pytest -q
```

Rapport de couverture (optionnel) :

```bash
pytest --cov=app --cov-report=term --cov-report=html:htmlcov -q
```

---

## Intégration Frontend

* Auth : `POST /api/v1/auth/token` (form : `email`, `password`) → `{ "access_token", "token_type" }`
* Header : `Authorization: Bearer <token>`
* Principales routes :

  * `/api/v1/users`
  * `/api/v1/techniciens`
  * `/api/v1/equipements`
  * `/api/v1/interventions`
  * `/api/v1/planning`
  * `/api/v1/notifications`
  * `/api/v1/documents`
  * `/api/v1/filters`
* CORS : `http://localhost:3000` autorisé par défaut
* Uploads : `POST /api/v1/documents/` puis accès via `/static/uploads/...`

Le contrat d’API est fourni par `openapi.json` ou `openapi.generated.json`.

---

## Déploiement

* Image Docker prête via `Dockerfile` : exécute migrations puis Uvicorn.
* `docker-compose.yml` orchestre Postgres, backend et volumes (uploads, base).
* Placer un reverse proxy (nginx/traefik), activer HTTPS, injecter les secrets par variables d’environnement.
* Exemple de proxy : `deploy/nginx.sample.conf`.

Consulter `DEPLOY_CHECKLIST.md` pour la checklist de production.

---

## Dépannage rapide

* **Connexion Postgres** : vérifier `.env` et l’état du service `db`.
* **Uploads manquants** : contrôler le volume et `UPLOAD_DIRECTORY`.
* **CORS** : ajuster `CORS_ALLOW_ORIGINS`.
* **JWT invalide** : confirmer `SECRET_KEY` et l’horloge système.
* **Alembic** : en cas d’écart de schéma, générer une nouvelle révision puis `upgrade`.

---

## Crédits & licence

* Auteur : Sabir Rochdi — MIF Maroc
* Licence : à définir

© 2025 MIF Maroc — Backend ERP Interventions
# FastApi_ERP_BackEnd_MIF_Maroc
