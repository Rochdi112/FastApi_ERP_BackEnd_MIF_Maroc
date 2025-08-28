# Cahier des charges – ERP MIF Maroc

Gestion des interventions correctives et préventives

- Version: 1.0
- Date: 22/08/2025
- Projet: ERP MIF Maroc – Application web
- Rédaction: Ingénieur Génie Informatique – Option Développement Web & Logiciel

---

## 1. Contexte et objectifs

MIF Maroc souhaite une application ERP pour piloter l’activité de maintenance industrielle, couvrant les interventions correctives et préventives, la planification, la traçabilité et les échanges avec les parties prenantes (responsables, techniciens, clients). L’objectif est de fournir une plateforme sécurisée, performante et auditée permettant:
- La création, l’affectation, le suivi et la clôture d’interventions.
- La maintenance préventive (plannings récurrents, génération d’interventions).
- La gestion des équipements, techniciens, documents et notifications.
- L’application de rôles et permissions (RBAC) et un audit des actions.

Ce cahier des charges s’appuie sur le backend actuellement développé (FastAPI + PostgreSQL) et en précise l’usage et les attentes fonctionnelles et non-fonctionnelles.


## 2. Périmètre fonctionnel

Modules couverts en V1 (backend prêt):
- Authentification & RBAC (JWT, rôles admin/responsable/technicien/client).
- Utilisateurs (gestion par l’admin, profil /me, mise à jour du profil).
- Interventions (correctives et préventives): création, consultation, changement de statut, historique, KPI de base.
- Planning préventif: création, lecture, mise à jour, génération automatique d’interventions via tâche planifiée.
- Équipements: création, consultation, suppression (pour responsables/admin).
- Techniciens & compétences: création, association de compétences, consultation.
- Documents: upload de fichiers liés aux interventions, consultation.
- Notifications: création et consultation (email/log), filtrage.
- Filtres interventions: filtrage par statut, urgence, type, technicien.

Hors périmètre immédiat (préparé côté modèle mais non exposé en API V1 ou non finalisé UI):
- Gestion clients/contrats avancée, stock/pièces, rapports/analytics détaillés, templates emails complets.


## 3. Rôles et droits (RBAC)

- Admin: gestion complète (utilisateurs, techniciens, équipements, planning, documents, notifications, interventions).
- Responsable: gestion opérationnelle (interventions, équipements, planning, techniciens/compétences), consultation globale.
- Technicien: exécution et mise à jour d’interventions (changements de statut, ajouts de documents), consultation de ses éléments.
- Client: consultation limitée des interventions les concernant (à étendre à l’UI ultérieurement).

Des dépendances FastAPI garantissent l’accès selon le rôle. Les tokens JWT portent les claims: `sub` (email), `user_id`, `role`.


## 4. Exigences fonctionnelles détaillées

### 4.1 Authentification et sécurité
- Connexion via endpoint d’authentification (email + mot de passe) retournant un JWT.
- Le JWT est repris dans le header Authorization: `Bearer <token>` pour toutes les routes protégées.
- Les routes imposent les rôles requis via dépendances RBAC.
- Le profil courant est accessible via `/auth/me` et `/users/me`.

Critères d’acceptation:
- Connexion valide renvoie `access_token` et `token_type=bearer`.
- Accès aux routes restreintes si et seulement si le rôle l’autorise.

### 4.2 Utilisateurs
- Admin: créer, lister, consulter par ID, désactiver/réactiver un utilisateur.
- Tout utilisateur: consulter et mettre à jour son propre profil (fullname, mot de passe).

Critères d’acceptation:
- Unicité email/username garantie.
- Désactivation empêche l’accès protégé.

### 4.3 Interventions
- Création d’intervention (corrective/préventive), avec priorité, urgence, dates, affectation optionnelle.
- Consultation: liste et détail par ID.
- Changement de statut par les profils autorisés (technicien/responsable selon flux).
- Historisation automatique des changements avec l’utilisateur acteur.
- KPI: délais, urgences, coûts agrégés (basique dans la V1).

Règles métiers clés:
- Interdiction de modification après statut `cloturee`.
- Interdiction d’archiver sans clôture préalable.
- Historique obligatoire à chaque changement de statut (user_id requis).

Critères d’acceptation:
- Création valide → intervention persistée avec historique “Création”.
- Transition invalide → erreur 400/409 conforme.

### 4.4 Planning (préventif)
- Création et gestion de plannings par équipement (fréquence, prochaine date).
- Tâche planifiée (APScheduler) qui génère automatiquement des interventions préventives à l’échéance, et met à jour les dates (dernière/prochaine).

Critères d’acceptation:
- Les plannings arrivés à échéance génèrent des interventions `ouverte`.
- Mise à jour cohérente des dates de planning.

### 4.5 Techniciens & compétences
- Création d’un technicien lié à un utilisateur au rôle “technicien”.
- Gestion et liste des compétences (unicité du nom), attachement au technicien.

Critères d’acceptation:
- Validation du rôle de l’utilisateur lié.
- Requêtes cohérentes sur les compétences existantes.

### 4.6 Équipements
- Création, consultation, liste, suppression (responsable/admin).
- Lien avec interventions et planning.

Critères d’acceptation:
- Suppression impossible si contraintes futures (à préciser en V2 si nécessaire), soft/hard delete selon règles.

### 4.7 Documents
- Upload de documents (photo, PDF, rapport) liés à une intervention.
- Sauvegarde physique en dossier `static/uploads/` et exposition via `/static`.
- Consultation globale et par intervention.

Critères d’acceptation:
- Fichier enregistré avec nom unique et consultable via URL statique.
- Référence persistée (nom original, chemin, date, intervention_id).

### 4.8 Notifications
- Création et envoi de notifications (email/log) pour des événements (ex: affectation, clôture).
- Consultation et filtrage par utilisateur/intervention.

Critères d’acceptation:
- Environnement SMTP configurable (dev: mailhog/mailcatcher).
- Templates HTML rendus correctement.

### 4.9 Filtres
- Filtrer les interventions par statut, urgence, type, technicien.

Critères d’acceptation:
- Combinaisons de filtres renvoient un sous-ensemble correct.


## 5. API & Intégration (extraits)

- Base URL: `http(s)://<host>:<port>/api/v1`.
- Auth:
  - POST `/auth/token` (Form email/password) → TokenResponse.
  - GET `/auth/me` → profil courant.
- Users: `POST /users` (admin), `GET /users`, `GET /users/{id}`, `GET /users/me`, `PUT /users/update`, `DELETE /users/{id}`, `PATCH /users/{id}/activate`.
- Interventions: `POST /interventions` (resp), `GET /interventions`, `GET /interventions/{id}`, `PATCH /interventions/{id}/statut` (tech).
- Planning: `POST /planning` (resp/admin), `GET /planning`, `GET /planning/{id}`, `PUT /planning/{id}`, `PATCH /planning/{id}/dates`, `DELETE /planning/{id}`.
- Techniciens: `POST /techniciens` (resp), `GET /techniciens`, `GET /techniciens/{id}`, `POST /techniciens/competences`, `GET /techniciens/competences`.
- Équipements: `POST /equipements` (resp), `GET /equipements`, `GET /equipements/{id}`, `DELETE /equipements/{id}`.
- Documents: `POST /documents` (admin), `POST /documents/upload` (alias), `GET /documents`, `GET /documents/{intervention_id}`.
- Notifications: `POST /notifications` (admin), `GET /notifications`, `GET /notifications/user/{user_id}`, `DELETE /notifications/{id}`.
- Filtres: `GET /filters/interventions` (query: statut, urgence, type, technicien_id).

Authentification requise sur la majorité des routes; contrôles d’accès par rôles selon route.


## 6. Modèle de données (vue d’ensemble)

Entités principales:
- User (rôle, identifiants, timestamps, état actif) – relations 1:1 avec Technicien/Client, 1:N notifications/historiques/rapports.
- Technicien (user_id, équipe, disponibilité, compétences[n..m]).
- Équipement (caractéristiques, client, relations interventions et planning).
- Intervention (type, statut, priorité, urgence, dates clés, coûts, rapports, relations: équipement, technicien, client, contrat, documents, historiques, notifications, stock).
- Document (nom original, chemin, date_upload, intervention_id).
- Planning (fréquence, prochaine/dernière date, équipement_id).
- Notification (type, message, date, user_id, intervention_id).
- HistoriqueIntervention (statut, remarque, horodatage, user_id, intervention_id).
- Client/Contrat/Stock/Report (déjà modélisés pour extensions futures).


## 7. Règles métier (principales)

- Interventions:
  - Transitions autorisées: `ouverte → affectee → en_cours → [en_attente] → cloturee → archivee`.
  - Interdictions: pas de modifications après `cloturee`; pas d’`archivee` sans `cloturee` préalable; `annulee` possible depuis états non-terminaux.
  - Historisation obligatoire avec `user_id` à chaque transition.
  - KPI calculés: délais restants, durées, coûts, SLA (selon priorité), derniers changements.

- Planning:
  - Génération automatique d’interventions préventives à l’échéance; mise à jour des dates.

- Documents:
  - Sauvegarde physique et traçabilité; exposition via `/static/uploads/*`.

- Notifications:
  - Emails basés sur templates HTML; configuration SMTP.

- RBAC:
  - Accès aux opérations sensibles réservé (admin/responsable/technicien selon cas). Client en lecture restreinte.


## 8. Exigences non-fonctionnelles

- Sécurité: JWT, hashage des mots de passe (bcrypt), CORS configuré, contrôle des rôles, protection des uploads.
- Performance: temps de réponse API cible < 300ms sur opérations standards; pagination et filtres côté serveur (extensions V2).
- Disponibilité: service stateless déployable en conteneurs; scheduler activable/désactivable.
- Observabilité: logs structurés, traces d’erreur; couverture de tests (unitaire/intégration) existante côté backend.
- Qualité: PEP8/Black/isort; ESLint/Prettier côté front; CI/CD recommandé.
- Conformité: gestion des données personnelles minimales; suppression/désactivation utilisateurs; journalisation des actions clés.


## 9. Contraintes techniques & déploiement

- Backend: FastAPI, SQLAlchemy, PostgreSQL, Alembic, APScheduler, FastAPI-Mail, Pydantic v2; Python 3.11.
- Frontend: Next.js 14 (App Router), TypeScript, Tailwind; Axios; Zustand.
- Déploiement: docker-compose (services: Postgres, backend). Volume pour `uploads`. Variables `.env` pour DB/SMTP/CORS/UPLOAD_DIRECTORY.
- Statique: montage `/static` pointant sur le parent du dossier uploads.


## 10. Critères d’acceptation (exemples)

- Authentification: POST `/auth/token` avec email/password renvoie un JWT valide; `GET /auth/me` retourne l’utilisateur.
- Interventions: création retournant 201 et un objet avec `id`, `type`, `statut=ouverte`; `PATCH /interventions/{id}/statut` respecte les règles de transition.
- Planning: création et mise à jour; génération automatique vérifiable (job manuel ou horodatage dépassé).
- Documents: upload retourne 201 avec `id`, `filename`, `path`; le fichier est accessible via `/static/uploads/...`.
- Notifications: création/liste/suppression fonctionnelles.


## 11. Roadmap & évolutions

- V1 (présent): périmètre décrit ci-dessus.
- V1.x:
  - Alignement complet Front/Back via génération OpenAPI (orval) et mapping types.
  - UI d’upload de documents, pages listes pour tous modules, persistance du token et garde par rôle.
  - Tableaux paginés/filtrés, vues détail enrichies.
- V2:
  - Clients/Contrats/SLAs avancés, stock/pièces avec valorisation, rapports & analytics, export, tableaux de bord KPI.


## 12. Points d’attention (techniques)

- Documents: s’assurer que l’URL exposée corresponde au fichier réellement écrit (préférer l’utilisation du champ `chemin`/`path`).
- Templates email: vérifier la correspondance entre noms de templates et fichiers présents.
- Sérialisation JWT: conserver `role` en string dans le token.
- Données sensibles: ne pas exposer les champs sensibles dans les endpoints publics; appliquer le principe du moindre privilège.

---

Ce cahier des charges décrit l’application cible en cohérence avec le backend actuel. Il sert de référence pour l’alignement du frontend, l’implémentation des écrans manquants et la planification des évolutions.
