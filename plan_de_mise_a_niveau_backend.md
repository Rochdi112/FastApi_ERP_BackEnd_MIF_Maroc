# Plan de mise à niveau du Backend (FastAPI) – ERP MIF Maroc

Objectif: Corriger, valider et finaliser le backend pour une intégration sereine avec le Frontend, avec une liste d’actions vérifiables et des critères d’acceptation.

## Vue d’ensemble – Checklist maître

- [ ] Environnement et variables (.env) vérifiés et documentés
- [ ] Base de données migrée et données de seed disponibles
- [ ] Qualité de code (formatage, lint, types) appliquée et CI configurée
- [ ] Tests automatisés stables avec couverture minimale définie
- [ ] Contrat d’API validé (OpenAPI ↔ contrat frontend)
- [ ] Authentification, RBAC et CORS vérifiés (happy path + edge cases)
- [ ] Uploads/documents, notifications et tâches planifiées testés
- [ ] Observabilité (logs/erreurs) et gestion d’erreurs uniformisées
- [ ] Conteneurisation (Docker) et orchestration (docker-compose) fonctionnelles
- [ ] Documentation d’intégration frontend fournie (guides, exemples, Postman)
- [ ] Critères d’acceptation et procédure de recette signés

---

## 1) Environnement & Démarrage

Répertoires principaux:
- Backend: `FastApi_ERP_BackEnd_MIF_Maroc/`
- Code app: `FastApi_ERP_BackEnd_MIF_Maroc/app/`
- Scripts utiles: `FastApi_ERP_BackEnd_MIF_Maroc/scripts/`

Actions:
- [ ] Créer un virtualenv et installer les dépendances
- [ ] Compléter `.env` (ou variables d’environnement) selon `app/core/config.py`
- [ ] Vérifier l’environnement via le script fourni

Commandes (PowerShell):
```powershell
# 1. Créer l’environnement Python
py -3.11 -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r FastApi_ERP_BackEnd_MIF_Maroc/requirements.txt

# 2. Validation rapide de l’env
python FastApi_ERP_BackEnd_MIF_Maroc/validate_env.py
```

Paramètres typiques à renseigner (adapter selon `config.py`):
- `DATABASE_URL` (PostgreSQL recommandé)
- `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `CORS_ORIGINS` (inclure les URLs du frontend)
- SMTP/Notifications si utilisés
- Chemins/quotas pour uploads si nécessaires

Sorties attendues:
- Environnement actif, dépendances installées, validation OK.

## 2) Base de données & Migrations

Présent: `alembic.ini`, `app/db/migrations/`, `migration.sql`, `app/seed/seed_data.py`.

Actions:
- [ ] Configurer `DATABASE_URL` (projet dev)
- [ ] Appliquer les migrations Alembic
- [ ] Exécuter le seed initial
- [ ] Vérifier index/contraintes clés étrangères selon modèles

Commandes:
```powershell
# Alembic (depuis la racine du repo)
$env:DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@localhost:5432/erp_mif"
# Si migrations prêtes
alembic -c FastApi_ERP_BackEnd_MIF_Maroc/alembic.ini upgrade head
# Sinon, utiliser temporairement migration.sql
psql "postgres://USER:PASSWORD@localhost:5432/erp_mif" -f FastApi_ERP_BackEnd_MIF_Maroc/migration.sql

# Seed
python FastApi_ERP_BackEnd_MIF_Maroc/app/seed/seed_data.py
```

Sorties attendues:
- Schéma à jour, seed OK, logs sans erreurs.

## 3) Qualité de code & CI

Objectif: formatage, lint et contrôle de qualité reproductibles en local et CI.

Actions:
- [ ] Ajouter/valider Black, isort, Flake8 (ou Ruff), Mypy (optionnel)
- [ ] Intégrer dans un workflow CI (GitHub Actions) avec matrice Python 3.11
- [ ] Activer hooks pre-commit (format + lint + tests courts)

Exemples de commandes locales:
```powershell
pip install black isort flake8
black FastApi_ERP_BackEnd_MIF_Maroc/app
isort FastApi_ERP_BackEnd_MIF_Maroc/app
flake8 FastApi_ERP_BackEnd_MIF_Maroc/app
```

Sorties attendues:
- Zéro erreur de lint; formatage uniforme; CI verte.

## 4) Tests & Couverture

Présent: `pytest.ini`, `coverage.xml` (à consolider), dossier `app/tests/` à compléter.

Actions:
- [ ] Écrire/designer tests unitaires pour services (ex: `services/*_service.py`)
- [ ] Ajouter tests d’API (happy path + erreurs) avec `TestClient`
- [ ] Fixer seuil de couverture (ex: 80%) et en échec si < seuil

Commandes:
```powershell
pip install pytest pytest-cov
pytest -q --maxfail=1 --disable-warnings --cov=FastApi_ERP_BackEnd_MIF_Maroc/app --cov-report=xml:FastApi_ERP_BackEnd_MIF_Maroc/coverage.xml
```

Sorties attendues:
- Tests verts; couverture >= seuil; rapport coverage mis à jour.

## 5) Contrat d’API (OpenAPI ↔ Frontend)

Présent: `openapi.json`, `openapi.generated.json`, `frontend_contract.json`, scripts `scripts/openapi_export.py`, `scripts/validate_contract.py`.

Actions:
- [ ] Générer l’OpenAPI depuis l’app (source de vérité)
- [ ] Comparer/diff avec `openapi.generated.json`
- [ ] Valider conformité au contrat frontend (`frontend_contract.json`)
- [ ] Résorber les écarts (schemas, champs obligatoires, codes d’erreur, pagination)

Commandes:
```powershell
# Export OpenAPI (adapter si script attend des arguments)
python FastApi_ERP_BackEnd_MIF_Maroc/scripts/openapi_export.py

# Validation du contrat
python FastApi_ERP_BackEnd_MIF_Maroc/scripts/validate_contract.py --openapi FastApi_ERP_BackEnd_MIF_Maroc/openapi.json --contract FastApi_ERP_BackEnd_MIF_Maroc/frontend_contract.json
```

Points d’attention:
- Noms et formats des champs (snakeCase vs camelCase côté FE)
- Codes HTTP, enveloppe d’erreur uniforme (`detail`, `code` interne)
- Pagination/tri/filtre (noms de query params cohérents)
- Stabilité des IDs et enums (documents, techniciens, équipements…)

Sorties attendues:
- 0 écart bloquant; conventions documentées.

## 6) Sécurité: Auth, RBAC, CORS

Présent: `app/core/security.py`, `app/core/rbac.py`, `services/auth_service.py`.

Actions:
- [ ] Vérifier le hashage mots de passe et expiration tokens
- [ ] Couvrir RBAC par rôles (accès routes sensibles)
- [ ] Configurer CORS pour le domaine frontend
- [ ] Tests: accès non authentifié, token expiré, rôle insuffisant

Commandes utiles:
```powershell
# Smoke local
uvicorn FastApi_ERP_BackEnd_MIF_Maroc.app.main:app --reload --port 8000
# Tester via Swagger: http://localhost:8000/docs
```

Sorties attendues:
- Flux login/refresh opérationnels, RBAC effectif, CORS OK.

## 7) Uploads/documents & Notifications/Jobs

Présent: `services/document_service.py`, `static/uploads/`, tâches `app/tasks/` (scheduler, notifications).

Actions (uploads):
- [ ] Limites taille, types MIME autorisés, dossiers, nettoyage
- [ ] URL d’accès statique (Nginx/ASGI), protections

Actions (notifications/tâches):
- [ ] Lancement scheduler en dev/prod, idempotence et logs
- [ ] Tests unitaires sur `notification_tasks.py` (cas succès/échec)

Sorties attendues:
- Upload sécurisé/stable; jobs planifiés observables et sans fuite.

## 8) Observabilité & Gestion d’erreurs

Actions:
- [ ] Logger structuré (niveau, corrélation requête, userId si authentifié)
- [ ] Handlers d’exceptions centralisés (`app/core/exceptions.py`) → formats homogènes
- [ ] Option: intégration Sentry/Rollbar en prod

Sorties attendues:
- Traces diagnostiques suffisantes, erreurs client/serveur distinguées.

## 9) Conteneurs & Orchestration

Présent: `Dockerfile`, `docker-compose.yml`, `deploy/nginx.sample.conf`.

Actions:
- [ ] Construire image, paramétrer variables (.env Docker)
- [ ] Verrouiller un tag d’image versionné
- [ ] docker-compose pour dev (DB + backend + stockage uploads)
- [ ] Vérifier Nginx sample (routes, static, taille uploads)

Commandes:
```powershell
# Build
docker build -t erp-mif-backend:dev FastApi_ERP_BackEnd_MIF_Maroc

# Compose (adapter services/ports/volumes)
docker compose -f FastApi_ERP_BackEnd_MIF_Maroc/docker-compose.yml up -d --build
```

Sorties attendues:
- Services up, healthchecks OK, endpoints accessibles.

## 10) Performance & Robustesse

Actions:
- [ ] Paramétrer workers Uvicorn/Gunicorn (CPU) et keep-alive
- [ ] Index DB sur colonnes de recherche (interventions, équipements)
- [ ] Pagination obligatoire sur listes volumineuses
- [ ] Timeouts côté service externe; retries limités

Sorties attendues:
- Latence stable sous charge raisonnable; absence de endpoints O(N).

## 11) Documentation d’intégration Frontend

Livrables à fournir au FE:
- [ ] Base URL et environnements (dev/stage/prod)
- [ ] Guide Auth (flux login/refresh, scopes/roles, durée token)
- [ ] Catalogue endpoints stabilisé (avec exemples de requêtes/réponses)
- [ ] Postman/Insomnia collection + variables d’environnement
- [ ] Comptes de test (admin, technicien, user), matrice RBAC
- [ ] Règles d’upload (taille max, types, endpoints d’accès)

## 12) Critères d’acceptation (Go FE)

Cette phase est “OK” si:
- [ ] Tests verts, couverture ≥ seuil
- [ ] `validate_contract.py` sans écarts bloquants
- [ ] Smoke tests manuels sur cas clés (CRUD clients, équipements, interventions)
- [ ] RBAC confirmé sur routes sensibles
- [ ] Build Docker et compose fonctionnels
- [ ] Documentation d’intégration remise et validée par le FE

## 13) Plan de recette rapide

- [ ] CRUD Client/Équipement/Technicien/Intervention (création → listing → update → delete)
- [ ] Upload document et consultation
- [ ] Notification/scheduler: déclenchement d’un job de test
- [ ] Auth: login, accès protégé, refus accès par rôle insuffisant

## 14) Annexes – Points spécifiques au repo

- Scripts clés:
  - `scripts/openapi_export.py`: export OpenAPI depuis l’app
  - `scripts/validate_contract.py`: vérifie la conformité avec `frontend_contract.json`
  - `scripts/check.ps1`, `scripts/debug_repro_me.py`: support debug
- Dossiers clés:
  - Modèles: `app/models/` – garder en phase avec `app/schemas/`
  - Services métier: `app/services/`
  - Tâches planifiées/notifications: `app/tasks/`
  - Migrations: `app/db/migrations/`, config Alembic: `alembic.ini`

---

## Feuille de route synthétique (exécution séquencée)

Semaine 1:
- Env + DB + migrations + seed + smoke local (docs OK)
- Lint/format + premiers tests unitaires services

Semaine 2:
- Validation contrat d’API; correction écarts; tests d’API
- Sécurité (auth/RBAC/CORS) + uploads + tâches planifiées

Semaine 3:
- Observabilité/logs + Docker/compose + perfs (index/pagination)
- Documentation d’intégration + collection Postman + recette conjointe FE

---

Dernière mise à jour: 2025-08-28