# ERP MIF Maroc — Backend FastAPI Runbook

Ce document est votre guide opérationnel « sans blocage » pour utiliser, tester, faire tourner, migrer et déployer le backend, sur Windows (PowerShell), Docker et CI.

---

## Start here
- Open `BACKEND_RUNBOOK.md` in the backend folder.
- Choose your path:
  - Local (Windows, Python venv)
  - Docker (Compose)

### Local (Windows PowerShell)
```powershell
Set-Location -Path d:\ERP_MIF_Maroc\FastApi_ERP_BackEnd_MIF_Maroc
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker
```powershell
Set-Location -Path d:\ERP_MIF_Maroc\FastApi_ERP_BackEnd_MIF_Maroc
docker compose up --build -d
```

Next: use the runbook sections for migrations, uploads, and troubleshooting when needed.

---

## Vue d’ensemble

- Base API: http://localhost:8000 (versionnée sous `/api/v1`)
- Docs: `/docs` et `/redoc`
- Santé: `GET /health` → `{"status":"ok"}`
- Fichiers statiques: `/static/uploads/`
- DB: PostgreSQL (prod), SQLite (tests)
- Migrations: Alembic (dossier `app/db/migrations`)
- Couverture tests: 90% min (actuellement > 95%)

Arborescence (extrait):

```
FastApi_ERP_BackEnd_MIF_Maroc/
  app/
    api/v1/         # Routes
    core/           # Config, sécurité, RBAC
    db/             # DB engine, Alembic
    models/         # ORM SQLAlchemy
    schemas/        # Pydantic v2
    services/       # Métier (auth, documents, ...)
    tasks/          # Scheduler (optionnel)
    templates/      # Emails Jinja2
    tests/          # Pytest
  alembic.ini       # Config Alembic (script_location = app/db/migrations)
  README.md         # Intro
  BACKEND_RUNBOOK.md# Ce fichier
```

---

## Prérequis

- Windows PowerShell 5.1+ (ou Windows Terminal)
- Python 3.11+
- Docker Desktop (optionnel, pour la stack complète)

Vérifier la version Python:

```powershell
python --version
```

---

## Démarrage rapide (Windows local)

1) Se placer dans le dossier backend:

```powershell
Set-Location -Path d:\ERP_MIF_Maroc\FastApi_ERP_BackEnd_MIF_Maroc
```

2) Créer/activer venv et installer:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Appliquer les migrations Postgres (si DB locale disponible):

```powershell
alembic upgrade head
```

4) Lancer l’API:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Ouvrir http://localhost:8000/docs

Astuce: Toujours exécuter `pytest`/`alembic` depuis le dossier `FastApi_ERP_BackEnd_MIF_Maroc` pour éviter les problèmes de chemins relatifs.

---

## Démarrage rapide (Docker)

1) Créer `.env` (voir plus bas) au besoin.

2) Lancer:

```powershell
docker compose up --build -d
```

- Le backend applique `alembic upgrade head` au démarrage, puis lance Uvicorn.

Arrêt:

```powershell
docker compose down -v
```

---

## Fichier .env (exemple minimal)

Créer un `.env` à la racine du backend si nécessaire:

```
# Sécurité
SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Base de données (prod/docker)
POSTGRES_USER=erp_user
POSTGRES_PASSWORD=erp_pass
POSTGRES_DB=erp_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# CORS
CORS_ALLOW_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Uploads (par défaut)
UPLOAD_DIRECTORY=app/static/uploads

# Emails (dev)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=user
SMTP_PASSWORD=password
EMAILS_FROM_EMAIL=no-reply@example.com

# Scheduler
ENABLE_SCHEDULER=false
```

Validation rapide:

```powershell
python validate_env.py
```

---

## Migrations Alembic

- Config: `alembic.ini` → `script_location = app/db/migrations`
- Dossier scripts: `app/db/migrations/versions`

Commandes courantes:

```powershell
# Générer une révision (après modifications modèles)
alembic revision -m "message" --autogenerate

# Appliquer la dernière révision
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```

Problèmes fréquents et solutions:

- Erreur `No 'script_location' key found`: Lancer la commande depuis le dossier `FastApi_ERP_BackEnd_MIF_Maroc` (où se trouve `alembic.ini`).
- SQLite et ALTER TABLE: géré via `render_as_batch` dans `env.py`.
- URL DB différente: définir `DATABASE_URL` dans l’env (prioritaire sur `alembic.ini`).

---

## Tests et couverture

Exécuter depuis le dossier backend:

```powershell
pytest -q
```

- Les tests utilisent SQLite en mémoire pour l’isolation.
- Couverture minimale exigée: 90% (config `pytest.ini`).
- Rapport XML écrit dans `coverage.xml`.

Astuces:

- Filtrer un fichier: `pytest app/tests/test_documents.py -q`
- Voir la sortie détaillée: `pytest -vv`

---

## Uploads & fichiers statiques

- Répertoire de travail: `settings.UPLOAD_DIRECTORY` (défaut `app/static/uploads`).
- L’API monte `/static` pour servir les fichiers; les documents sont accessibles via `/static/uploads/...`.
- Normalisation multi-plateformes implémentée dans `app/main.py` pour Windows/Linux.

À savoir:

- Le service d’upload (`app/services/document_service.py`) écrit physiquement dans `UPLOAD_DIRECTORY` et stocke un chemin relatif (`static/uploads/<uuid>.<ext>`).
- Les endpoints pour documents:
  - POST `/api/v1/documents/upload?intervention_id=<id>` (alias attendu par tests)
  - GET `/api/v1/documents/` (liste complète, admin)
  - GET `/api/v1/documents/{intervention_id}` (par intervention)

---

## Templates d’e-mails (Jinja2)

- Emplacement: `app/templates`
- Exemples: `notification_information.html`, `notification_alerte.html`
- Test rapide de rendu (via tests): `pytest app/tests/services/test_email_templates.py -q`

---

## Authentification & RBAC

- JWT via `python-jose`.
- Rôles: `admin`, `responsable`, `technicien`, `client`.
- Connexion: `POST /api/v1/auth/login` (form: `username` + `password`).
- Header: `Authorization: Bearer <token>`.

---

## Données de seed (facultatif)

```powershell
python app/seed/seed_data.py
```

---

## Dépannage rapide (FAQ)

- `TemplateNotFound` pour e-mails: vérifier le répertoire courant (doit contenir `app/templates`) ou lancer depuis le dossier backend.
- Échec upload pendant les tests: s’assurer que le path temporaire existe; les tests créent `app/tests/test_upload.txt` puis le suppriment.
- Couverture < 90%: exécuter `pytest` depuis le dossier backend pour que `source=app` soit bien résolu; éviter d’exclure des modules essentiels.
- `psycopg2` erreurs: utiliser `psycopg2-binary` (déjà listé) et s’assurer que Postgres est accessible.
- `KeyboardInterrupt` en REPL: exécuter les commandes directement en PowerShell (pas dans le REPL `>>>`). Exemple correct:

```powershell
# (Correct) exécution d’un one-liner Python
python -c "from alembic.config import Config; c=Config('alembic.ini'); print(c.get_main_option('script_location'))"
```

---

## Intégration Frontend

- CORS autorise par défaut `http://localhost:3000`.
- Les routes principales sont montées sous `/api/v1/*` et (compat) à la racine pour certains outils/tests.
- Contrat OpenAPI: `openapi.json` / `openapi.generated.json`.

---

## CI/CD & Production (checklist)

- Construire l’image Docker (inclut migrations au démarrage).
- Variables d’env sécurisées (SECRET_KEY, DB, SMTP, CORS).
- Volumes persistants: base Postgres + `static/uploads`.
- Reverse-proxy (nginx/traefik) + HTTPS.
- Observabilité (logs, Sentry facultatif), sauvegardes DB, rotation des clés.

---

## Annexes

- Lancer validateur d’environnement:

```powershell
python validate_env.py
```

- Générer un rapport de tests (HTMLcov exemple):

```powershell
pytest --cov=app --cov-report=term --cov-report=html:htmlcov -q
```

- Pointer Alembic sur une autre DB à la volée:

```powershell
$env:DATABASE_URL = "sqlite:///$(Resolve-Path .)/alembic_local.sqlite"
alembic upgrade head
Remove-Item Env:DATABASE_URL
```

---

Besoin d’un mode d’emploi supplémentaire (VS Code tasks, Makefile, pipelines) ? Ajoutez-le ici; ce runbook est conçu pour être votre référence unique. ✅
