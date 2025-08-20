# Patch Plan — Corrections recommandées

Objectif: corriger les écarts et améliorer la cohérence du contrat.

## 1) Enum Intervention — harmonisation schémas ↔ ORM

- Fichier: `app/schemas/intervention.py`
- Ajouts proposés:
  - Dans `InterventionType`: ajouter `ameliorative`, `diagnostic` (si réellement supportés côté métier)
  - Dans `StatutIntervention`: ajouter `annulee`
- Impact: aligner les DTO sur le modèle SQLAlchemy.

Snippet (à adapter):
- Ajouter lignes:
  - `ameliorative = "ameliorative"`
  - `diagnostic = "diagnostic"`
  - `annulee = "annulee"`

## 2) Service documents — dossier configurable et URL

- Fichier: `app/services/document_service.py`
  - Remplacer la constante `UPLOAD_DIR = "app/static/uploads"` par `settings.UPLOAD_DIRECTORY` (importer `from app.core.config import settings`).
- Fichier: `app/models/document.py`
  - Propriété `url`: utiliser `chemin` au lieu de `nom_fichier` pour construire `/static/<chemin>`.

## 3) Montage des fichiers statiques

- Fichier: `app/main.py`
  - Ajouter:
    ```python
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    ```
  - Note: vérifier si cela n’interfère pas avec l’exécution Docker.

## 4) RBAC sur GET équipements (si souhaité)

- Fichier: `app/api/v1/equipements.py`
  - Ajouter dépendance `get_current_user` sur `list_equipements` et `get_equipement`:
    ```python
    from app.core.rbac import get_current_user
    def list_equipements(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
        ...
    def get_equipement(equipement_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
        ...
    ```
  - Sinon, documenter que la lecture est publique.

## 5) Nettoyage scheduler

- Fichier: `app/tasks/scheduler.py`
  - Décommenter `start_scheduler()` et retirer `##` en fin de `scheduler.start()`.
  - Option: appeler `start_scheduler()` depuis `lifespan` si variable d’env `ENABLE_SCHEDULER=true`.

## 6) Génération OpenAPI stable

- Si l’appli ne démarre pas en local, utiliser `scripts/openapi_export.py` (fallback AST) pour fournir un JSON approximatif acceptable par le front.

---

Après application, relancer:
- `python scripts/validate_contract.py --contract frontend_contract.json`
- `python scripts/openapi_export.py > openapi.json`
