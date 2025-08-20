# app/seed/seed_data.py

from faker import Faker
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.technicien import Technicien, Competence
from app.models.equipement import Equipement
from app.models.intervention import Intervention, StatutIntervention, InterventionType
from app.models.planning import Planning
from app.models.notification import Notification
from app.models.historique import HistoriqueIntervention
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import random

fake = Faker()

def seed_all(db: Session):
    # --- USERS ---
    admin = User(
        full_name="Admin MIF",
        email="admin@mif.ma",
        role=UserRole.admin,
        hashed_password=get_password_hash("admin123"),
        is_active=True
    )
    db.add(admin)

    responsables = []
    for _ in range(2):
        user = User(
            full_name=fake.name(),
            email=fake.unique.email(),
            role=UserRole.responsable,
            hashed_password=get_password_hash("responsable123"),
            is_active=True
        )
        responsables.append(user)
        db.add(user)

    techniciens = []
    for _ in range(3):
        user = User(
            full_name=fake.name(),
            email=fake.unique.email(),
            role=UserRole.technicien,
            hashed_password=get_password_hash("tech123"),
            is_active=True
        )
        db.add(user)
        db.flush()  # pour obtenir l'ID
        tech = Technicien(user_id=user.id, equipe="A", disponibilite=True)
        db.add(tech)
        techniciens.append(tech)

    clients = []
    for _ in range(2):
        user = User(
            full_name=fake.name(),
            email=fake.unique.email(),
            role=UserRole.client,
            hashed_password=get_password_hash("client123"),
            is_active=True
        )
        db.add(user)
        clients.append(user)

    # --- COMPÉTENCES ---
    competence_labels = ["mécanique", "électrique", "hydraulique"]
    for nom in competence_labels:
        db.add(Competence(nom=nom))

    # --- ÉQUIPEMENTS ---
    equipements = []
    for _ in range(5):
        equip = Equipement(
            nom=fake.word().capitalize() + " Machine",
            type=random.choice(["électrique", "hydraulique"]),
            localisation=fake.city(),
            frequence_entretien=random.choice(["mensuel", "hebdomadaire", "trimestriel"])
        )
        db.add(equip)
        equipements.append(equip)

    db.flush()

    # --- INTERVENTIONS ---
    for _ in range(10):
        i = Intervention(
            titre=fake.sentence(nb_words=3),
            description=fake.text(),
            type=random.choice(list(InterventionType)),
            statut=random.choice(list(StatutIntervention)),
            priorite=random.randint(1, 3),
            urgence=random.choice([True, False]),
            date_creation=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            date_limite=datetime.utcnow() + timedelta(days=random.randint(1, 10)),
            date_cloture=None,
            technicien_id=random.choice(techniciens).id,
            equipement_id=random.choice(equipements).id
        )
        db.add(i)

    # --- PLANNING ---
    for equip in equipements[:2]:
        planning = Planning(
            frequence="mensuel",
            prochaine_date=datetime.utcnow() + timedelta(days=30),
            derniere_date=datetime.utcnow() - timedelta(days=30),
            date_creation=datetime.utcnow(),
            equipement_id=equip.id
        )
        db.add(planning)

    # --- NOTIFICATIONS SIMULÉES ---
    for _ in range(5):
        notif = Notification(
            type="affectation",
            canal="email",
            contenu="Intervention affectée à un technicien.",
            date_envoi=datetime.utcnow(),
            user_id=random.choice(techniciens).user_id,
            intervention_id=1
        )
        db.add(notif)

    # --- HISTORIQUE ---
    historique = HistoriqueIntervention(
        statut=StatutIntervention.en_cours,
        remarque="Intervention démarrée automatiquement.",
        horodatage=datetime.utcnow(),
        user_id=admin.id,
        intervention_id=1
    )
    db.add(historique)

    db.commit()
# app/seed/seed_data.py