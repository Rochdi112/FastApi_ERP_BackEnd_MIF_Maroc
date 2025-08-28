# Cahier des charges BACKEND – ERP MIF Maroc

Gestion des interventions correctives et préventives (FastAPI • SQLAlchemy • Docker • PostgreSQL)

- Version: 1.0
- Date: 22/08/2025
- Portée: Backend (API + Modèle + Services + Tâches + Déploiement)
- Référence: Code actuel du dossier FastApi_ERP_BackEnd_MIF_Maroc

---

## 1) Objectifs et périmètre

Fournir une API REST sécurisée et performante pour l’ERP de maintenance:
- Interventions: création, cycle de vie, KPI, audit.
- Préventif: planning + génération d’interventions via scheduler.
- Équipements, techniciens/compétences, documents, notifications.
- Utilisateurs & RBAC (JWT + rôles), profil /me, CORS.
- Déploiement conteneurisé (Docker), DB PostgreSQL, migrations.

Hors périmètre immédiat: analytics avancés, gestion stock approfondie, clients/contrats complets (déjà modélisés, à exposer V2), SSO/OIDC.

---

## 2) Architecture & technologies

- API: FastAPI (OpenAPI, docs intégrées), versionnée sous `/api/v1`.
- ORM: SQLAlchemy (2.x), sessions par dépendance, Base declarative.
- Validation: Pydantic v2 (schemas), pydantic-settings pour configuration.
- Sécurité: JWT (python-jose), RBAC (dépendances), hashage (passlib/bcrypt).
- Tâches: APScheduler (génération préventif), toggle `ENABLE_SCHEDULER`.
- Email: fastapi-mail + templates Jinja2 (notifications).
- Fichiers statiques: `app/static/uploads` servi via `/static`.
- DB: PostgreSQL (prod/dev), fallback SQLite in-memory (tests).
- Migrations: Alembic (commande `alembic upgrade head`).
- Déploiement: Dockerfile + docker-compose (services: db, backend).

---

## 3) Conception API (exigences)

- Versionnement stable `/api/v1` + compat racine (déjà présent pour tests).
- Contrats clairs (OpenAPI): schémas et enums alignés.
- Erreurs: HTTPException cohérentes (401/403/404/409/400) + messages explicites.
- Auth: endpoints `/auth/token` (Form email+password), `/auth/me`.
- RBAC par dépendances: `admin_required`, `responsable_required`, etc.
- Pagination/filtrage (V1: filtres interventions; V1.x: pagination généralisée).
- Upload multipart pour documents; limites taille & type (à préciser ci-dessous).

---

## 4) Domaine & règles métier

- Interventions: machine d’état (ouverte → affectee → en_cours → [en_attente] → cloturee → archivee; annulee autorisé hors terminaux). Verrous: pas de modif après `cloturee`, pas d’`archivee` sans `cloturee`.
- Historisation: chaque création/changement doit générer une entrée (statut, horodatage, user_id, remarque).
- KPI: délais restant/écoulé, durées estimée/réelle, coûts calculés (pièces + MO), SLA par priorité.
- Préventif: Planning par équipement; job périodique pour créer l’intervention et recalculer dates (dernière/prochaine).
- Documents: lien obligatoire à une intervention; stockage en `/static/uploads`; URL publique sous `/static/...`.
- Techniciens: créés uniquement si user.role == technicien; compétences uniques.
- Notifications: par email (ou log), filtrables par user/intervention.

---

## 5) Modèle de données (synthèse)

- User(id, username, email, role[admin|responsable|technicien|client], is_active, timestamps, relations 1:1 technicien/client, 1:N notifications/historiques/rapports).
- Technicien(id, user_id, equipe, disponibilite, compétences[n..m]).
- Équipement(id, ...), relations interventions, planning.
- Intervention(id, titre, description, type, statut, priorite, urgence, dates clés, coûts, rapport, relations: equipement, technicien, client, contrat, documents, historiques, notifications, stock).
- Document(id, nom_fichier, chemin, date_upload, intervention_id).
- Planning(id, frequence, prochaine_date, derniere_date, equipement_id).
- Notification(id, type, message, date_envoi, user_id, intervention_id).
- HistoriqueIntervention(id, statut, remarque, horodatage, user_id, intervention_id).
- Client/Contrat/Stock/Report: présents pour extensions.

Indexes ciblés par métier (statut+priorite, technicien+statut, dates, etc.).

---

## 6) Sécurité & conformité

- JWT signé HS256, `exp` paramétré; claims: `sub` (email), `user_id`, `role` (string).
- Hashage bcrypt via passlib; compte `is_active` vérifié.
- CORS: origines restrictives en production (pas `*`).
- Autorisations granulaires par rôle; endpoints admin protégés.
- Upload: contrôle extension/MIME et taille max (ex: 10 Mo); filtrage nom; stockage hors racine publique sauf `/static` contrôlé.
- Journalisation: logs d’accès et erreurs; événements critiques (auth, statut interventions).
- Données personnelles minimisées; suppression/désactivation utilisateurs documentée.

---

## 7) Performance & qualité

- Temps moyen API cible < 300ms (opérations standard).
- Éviter N+1 (relations lazy vs selectinload où pertinent pour listes).
- Pagination standard (limit/offset) à généraliser V1.x.
- Tests unitaires/intégration sur routes/services (déjà nombreux); couverture cible > 70%.
- Style et lint: Black, isort; règles flake8; CI/CD recommandé.

---

## 8) Déploiement & exploitation

- Docker: image backend; variables `.env` (DB, SMTP, SECRET_KEY, CORS, UPLOAD_DIRECTORY, ENABLE_SCHEDULER).
- docker-compose: Postgres 16 + backend; volume `uploads_data` et `db_data`.
- Migrations Alembic: `alembic upgrade head` au démarrage.
- Santé: endpoint `/health`; readiness/liveness (à prévoir si K8s).
- Observabilité: logs structurés; intégrer un logger JSON + corrélation requêtes (V1.x).

---

## 9) Spécifications d’implémentation (extraits clés)

- Dépendance DB FastAPI `get_db()`: session par requête; fermeture en `finally`.
- Fallback tests: SQLite mémoire; init schéma lazy via Base.metadata.create_all; ne pas utiliser en prod.
- Services: valider ressources liées (ex: technicien/equipement existants), lever 404/400/409 selon cas.
- Historique: `user_id` obligatoire (assuré via token; `ensure_user_for_email` en tests pour robustesse).
- Upload: `uuid` pour nom serveur; stocker chemin relatif; renvoyer URL accessible.
- Scheduler: job idempotent, journaliser exécutions/erreurs; configurable par variable `ENABLE_SCHEDULER`.

---

## 10) Corrections & améliorations recommandées (à appliquer)

1. Document.url vs chemin
- Problème: `Document.url` renvoie `/static/uploads/{nom_fichier}` alors que le fichier sauvegardé utilise un `uuid` (champ `chemin`).
- Action: faire retourner `"/" + chemin` ou stocker le nom serveur distinct et l’utiliser pour l’URL. Harmoniser `DocumentOut` pour exposer `filename` (nom original) + `path` (chemin) et une `url` cohérente.

2. Templates email manquants
- Problème: `notification_tasks.py` référence `notification_affectation.html` et `notification_cloture.html` mais les fichiers présents sont `notification_alerte.html` et `notification_information.html`.
- Action: créer/renommer les templates ou adapter les noms dans le code.

3. JWT `role` sérialisé
- Problème potentiel: `role` (Enum) peut être encodé comme objet; risqué.
- Action: encoder `role.value` dans le token et normaliser partout en string.

4. Doublon en fin de `models/client.py`
- Problème: duplication de relations et `to_dict` simple après une version avancée; artefact de merge.
- Action: supprimer le bloc dupliqué et conserver l’implémentation riche et documentée.

5. Pydantic alias pour Documents
- Problème: alias `filename/path` vs champs ORM `nom_fichier/chemin`; risque d’incohérence si `by_alias` non activé.
- Action: soit éviter les alias, soit forcer `response_model_by_alias=True` sur routes concernées et rester cohérent.

6. Validation upload
- Ajouter: limite de taille, liste blanche d’extensions/MIME (pdf, jpg, png), antivirus optionnel.

7. CORS production
- Restreindre `CORS_ALLOW_ORIGINS` aux domaines approuvés; retirer localhost en prod.

8. Migrations vs modèle
- Garantir que le schéma Alembic reflète l’état des modèles; ajouter scripts migration pour récents index/champs.

9. Pooling DB & timeouts
- Configurer pool_size, max_overflow, pool_pre_ping; timeouts côté engine.

10. Observabilité
- Ajouter un logger structuré, IDs de corrélation, niveau log configurable; métriques (Prometheus) V1.x.

11. Pagination & tri
- Généraliser `limit/offset/sort` sur listes (interventions, équipements, users), par défaut raisonnables.

12. N+1 & performances
- Utiliser `selectinload` pour relations courantes en liste; indices vérifiés sur filtres.

13. Gestion d’erreurs mails
- Encapsuler l’envoi avec retry/backoff, circuit-breaker; fallback log en dev.

---

## 11) Critères d’acceptation (backend)

- Auth: `/auth/token` renvoie JWT; `/auth/me` renvoie 200 avec user.
- Interventions: création 201 (historique créé); transitions illégales → 400/409; statut final verrouille édition.
- Planning: job crée interventions `ouverte` pour plannings échus et met à jour dates.
- Documents: POST upload 201; fichier accessible via `/static/...`; GET par intervention renvoie la liste.
- Notifications: création 201; liste filtrable; suppression 200.
- Qualité: tests unitaires/intégration passent; linter OK; build docker OK; alembic upgrade OK.

---

## 12) Plan de mise en œuvre (résumé)

- Étape 1: Corrections critiques (1–5) + durcissement CORS + alias Document.
- Étape 2: Pagination/tri + perf (selectinload) + logs structurés.
- Étape 3: Alignement complet OpenAPI (vérif schemas) + CI/CD.
- Étape 4: Exposition progressive des modules avancés (clients/contrats/stock) et analytics.

---

Ce cahier des charges backend formalise le fonctionnement actuel, les exigences, et les corrections à appliquer pour un service robuste, sécurisé et prêt pour l’intégration frontend et la mise en production.
