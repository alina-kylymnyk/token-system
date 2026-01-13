from fastapi import APIRouter
from .subscription import router as subscription_router
from .transactions import router as transactions_router
from .credits import router as credits_router

router = APIRouter()

router.include_router(subscription_router, prefix="/subscription", tags=["Public - Subscription"])
router.include_router(transactions_router, prefix="/transactions", tags=["Public - Transactions"])
router.include_router(credits_router, prefix="/credits", tags=["Public - Credits"])