# app/api/v1/techniciens.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db           # <-- Important : importer get_db (pas redéfinir)
from app.schemas.technicien import (
    TechnicienCreate, TechnicienOut,
    CompetenceCreate, CompetenceOut
)
from app.services.technicien_service import (
    create_technicien,
    get_technicien_by_id,
    get_all_techniciens,
    create_competence,
    get_all_competences
)
from app.core.rbac import responsable_required, get_current_user

router = APIRouter(
    prefix="/techniciens",
    tags=["techniciens"],
    responses={404: {"description": "Technicien ou compétence introuvable"}}
)

@router.post("/", response_model=TechnicienOut, summary="Créer un technicien")
def create_new_technicien(
    data: TechnicienCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(responsable_required)
):
    """
    Crée un nouveau technicien (réservé aux responsables).
    """
    return create_technicien(db, data)

@router.get("/", response_model=List[TechnicienOut], summary="Lister les techniciens")
def list_techniciens(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Liste tous les techniciens.
    """
    return get_all_techniciens(db)

@router.post("/competences", response_model=CompetenceOut, summary="Créer une compétence")
def create_new_competence(
    data: CompetenceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(responsable_required)
):
    """
    Crée une nouvelle compétence (réservé aux responsables).
    """
    return create_competence(db, data)

@router.get("/competences", response_model=List[CompetenceOut], summary="Lister les compétences")
def list_competences(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Liste toutes les compétences.
    """
    return get_all_competences(db)

@router.get("/{technicien_id}", response_model=TechnicienOut, summary="Détail d’un technicien")
def get_technicien(
    technicien_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Récupère le détail d’un technicien par ID.
    """
    return get_technicien_by_id(db, technicien_id)
