from fastapi import APIRouter
from .plans import router as plans_router
from .settings import router as settings_router
from .statistics import router as statistics_router

router = APIRouter()

router.include_router(plans_router, prefix="/subscription-plans", tags=["Admin - Plans"])
router.include_router(settings_router, prefix="/settings", tags=["Admin - Settings"])
router.include_router(statistics_router, prefix="/statistics", tags=["Admin - Statistics"])