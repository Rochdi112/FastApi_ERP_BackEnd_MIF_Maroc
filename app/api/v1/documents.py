# app/api/v1/documents.py

from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentOut
from app.services.document_service import create_document
from app.core.rbac import technicien_required, responsable_required, admin_required

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Document non trouvé"}}
)

# Dépendance DB
# get_db central (override en tests)

@router.post(
    "/",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Uploader un document",
    description="Upload d’un fichier lié à une intervention (photo, rapport, preuve, etc.).",
    dependencies=[Depends(admin_required)]
)
def upload_document(
    intervention_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return create_document(db, file, intervention_id)

# Alias attendu par certains tests: /documents/upload
@router.post(
    "/upload",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Uploader un document (alias)",
    dependencies=[Depends(admin_required)]
)
def upload_document_alias(
    intervention_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return create_document(db, file, intervention_id)

@router.get(
    "/",
    response_model=List[DocumentOut],
    summary="Lister tous les documents",
    description="Accès à la liste de tous les documents liés aux interventions (admin/responsable uniquement).",
    dependencies=[Depends(admin_required)]
)
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).all()

# Endpoint attendu par tests: /documents/{intervention_id}
@router.get(
    "/{intervention_id}",
    response_model=List[DocumentOut],
    summary="Lister les documents d'une intervention",
    dependencies=[Depends(admin_required)]
)
def list_documents_by_intervention(intervention_id: int, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.intervention_id == intervention_id).all()
