# app/api/v1/notifications.py

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.notification import NotificationCreate, NotificationOut
from app.services.notification_service import create_notification
from app.models.notification import Notification
from app.core.rbac import responsable_required, admin_required

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "Notification non trouvée"}}
)

# Dépendance DB
# get_db central (override en tests)

@router.post(
    "/",
    response_model=NotificationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une notification",
    description="Crée une notification par email ou log pour une intervention (admin/responsable uniquement).",
    dependencies=[Depends(admin_required)]
)
def create_new_notification(data: NotificationCreate, db: Session = Depends(get_db)):
    return create_notification(db, data)

@router.get(
    "/",
    response_model=List[NotificationOut],
    summary="Lister les notifications",
    description="Retourne toutes les notifications envoyées (admin/responsable uniquement).",
    dependencies=[Depends(admin_required)]
)
def list_notifications(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    intervention_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
):
    q = db.query(Notification)
    if user_id is not None:
        q = q.filter(Notification.user_id == user_id)
    if intervention_id is not None:
        q = q.filter(Notification.intervention_id == intervention_id)
    return q.offset(offset).limit(min(limit, 200)).all()

@router.get(
    "/user/{user_id}",
    response_model=List[NotificationOut],
    summary="Lister les notifications d'un utilisateur",
    dependencies=[Depends(admin_required)]
)
def list_notifications_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == user_id).all()

@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_200_OK,
    summary="Supprimer une notification",
    dependencies=[Depends(admin_required)]
)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    db.delete(notif)
    db.commit()
    return {"detail": "Notification supprimée"}
