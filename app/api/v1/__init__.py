# app/api/v1/__init__.py

from .auth import router as auth_router
from .users import router as users_router
from .techniciens import router as techniciens_router
from .equipements import router as equipements_router
from .interventions import router as interventions_router
from .planning import router as planning_router
from .notifications import router as notifications_router
from .documents import router as documents_router
from .filters import router as filters_router

__all__ = [
    "auth_router",
    "users_router", 
    "techniciens_router",
    "equipements_router",
    "interventions_router",
    "planning_router",
    "notifications_router",
    "documents_router",
    "filters_router"
]
