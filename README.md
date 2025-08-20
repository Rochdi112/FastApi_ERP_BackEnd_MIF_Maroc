<h1 align="center">ERP MIF Maroc — Backend FastAPI</h1>
<p align="center"><em>Par : Sabir Rochdi</em></p>

<p align="center">
	<a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-blue.svg"></a>
	<a href="https://fastapi.tiangolo.com/"><img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg"></a>
	<a href="https://www.postgresql.org/"><img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16%2B-336791.svg"></a>
	<a href="#tests--couverture"><img alt="Tests" src="https://img.shields.io/badge/tests-pytest%20%2B%20coverage-brightgreen.svg"></a>
</p>

Backend ERP pour la gestion d'interventions industrielles : authentification JWT, RBAC, gestion des utilisateurs/techniciens/équipements/interventions, planning, notifications et documents. Prêt pour la production (Docker), avec migrations Alembic et tests automatisés.

---

## Sommaire

- Aperçu rapide
- Stack & fonctionnalités
- Structure du projet
- Démarrage (Docker / local / tâches VS Code)
- Configuration (.env)
- Migrations & seed
- Tests & couverture
- Intégration Frontend
- Déploiement
- FAQ & dépannage
- Crédit & licence

---

## Aperçu rapide

- Base API: http://localhost:8000 — versionnée sous `/api/v1`
- Docs: `/docs` (Swagger) et `/redoc`
- Santé: GET `/health` → {"status":"ok"}
- Racine: GET `/`
- Statique: `/static/uploads` (accès aux documents)

---

## Stack & fonctionnalités

- FastAPI, Uvicorn, SQLAlchemy 2.0, Alembic, Pydantic v2
- PostgreSQL (prod) / SQLite (tests)
- Auth JWT (python-jose), mots de passe hashés (passlib[bcrypt])
- RBAC: admin, responsable, technicien, client
- APScheduler (tâches planifiées)
- Upload de fichiers, emails (fastapi-mail)

---

## Structure du projet

```
app/
	main.py               # app FastAPI, CORS, static, routes
	api/v1/               # endpoints REST
	core/                 # config, sécurité, rbac, exceptions
	db/                   # engine, session, Base
	models/               # ORM SQLAlchemy
	schemas/              # Pydantic v2
	services/             # logique métier
	tasks/, seed/, tests/ # tâches, données, tests
static/uploads/
```

Fichiers utiles : `Dockerfile`, `docker-compose.yml`, `alembic.ini`, `migration.sql`, `openapi.json`, `openapi.generated.json`, `frontend_contract.json`, `validate_env.py`, `generate_report.py`, `deploy/nginx.sample.conf`.

---

## Démarrage

### Option A — Docker Compose (recommandé)
1) Créer `.env` (copier `.env.example` si présent, sinon créer à partir des variables ci-dessous).
2) Lancer :

```powershell
docker compose up --build -d
```

Le backend attend Postgres, applique `alembic upgrade head`, puis démarre Uvicorn sur 0.0.0.0:8000.

### Option B — Local (venv / Windows PowerShell)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option C — Tâches VS Code (Windows)

- Python: Create venv & Install — crée `.venv` et installe les dépendances
- DB: Alembic upgrade head — applique les migrations
- Dev: Run FastAPI (reload) — lance Uvicorn avec reload
- Tests: run — exécute la suite de tests

Ouvrir la palette de commandes → “Run Task” → choisir la tâche.

---

## Configuration (.env)

Variables clés :
- SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
- POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT
- CORS_ALLOW_ORIGINS (JSON array)
- UPLOAD_DIRECTORY (défaut : `app/static/uploads`)
- SMTP_* et EMAILS_FROM_EMAIL

Valider votre configuration (optionnel) :

```powershell
python validate_env.py
```

---

## Migrations & seed

Appliquer les migrations :

```powershell
alembic upgrade head
```

Charger des données d’exemple (optionnel) :

```powershell
python app/seed/seed_data.py
```

---

## Tests & couverture

Exécuter les tests :

```powershell
pytest -q
```

Couverture (optionnel) :

```powershell
pytest --cov=app --cov-report=term --cov-report=html:htmlcov -q
```

---

## Intégration Frontend

- Auth: POST `/api/v1/auth/token` (form: email, password) → { access_token, token_type }
- Header: `Authorization: Bearer <token>`
- Principales routes: `/api/v1/users`, `/api/v1/techniciens`, `/api/v1/equipements`, `/api/v1/interventions`, `/api/v1/planning`, `/api/v1/notifications`, `/api/v1/documents`, `/api/v1/filters`
- CORS: `http://localhost:3000` autorisé par défaut
- Uploads: POST `/api/v1/documents/` et accès via `/static/uploads/...`

Le contrat d’API est disponible dans `openapi.json` (ou `openapi.generated.json`).

---

## Déploiement

- Image Docker prête (voir `Dockerfile`) : exécute migrations + Uvicorn.
- `docker-compose.yml` orchestre Postgres, backend et volumes persistants (uploads, base).
- Placez un reverse proxy (nginx/traefik) si besoin, configurez HTTPS, et fournissez les secrets via variables d’environnement.
- Exemple de proxy : `deploy/nginx.sample.conf`.

Voir également `DEPLOY_CHECKLIST.md` pour une checklist de production.

---

## FAQ & dépannage

- Connexion Postgres: vérifier `.env` et l’état du service `db` (compose).
- Uploads manquants: vérifier le volume des uploads et `UPLOAD_DIRECTORY` → `app/static/uploads`.
- CORS: ajuster `CORS_ALLOW_ORIGINS`.
- JWT invalide: confirmer `SECRET_KEY` et l’horloge système.
- Alembic: si écart de schéma, régénérer une révision et rejouer `upgrade`.

---

## Crédit & licence

- Auteur: Sabir Rochdi — MIF Maroc
- Licence: -----------------------

© 2025 MIF Maroc — Backend ERP Interventions
