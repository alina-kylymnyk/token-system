from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.core.security import require_admin_token
from app.db.models import SystemSettings
from app.schemas import (
    ExchangeRateUpdateRequest,
    ExchangeRateUpdateResponse
)

router = APIRouter()

@router.patch("/excahnge-rate", response_model=ExchangeRateUpdateResponse)
async def update_exchange_rate(
    request: ExchangeRateUpdateRequest,
    db: Session = Depends(get_db),
    _token: str = Depends(require_admin_token)
):
    """
    Updating the base conversion rate

    - **base_rate**: New base rate ($1 = X credits)

    NOTE: Rate change affects all future transactions

    Returns:
    Rate update information
    """
    try:
        setting = db.query(SystemSettings).filter(
            SystemSettings.key == "exchange_rate"
        ).first()

        if not setting:
            # Create settings if they don't exist
            setting = SystemSettings(
                key="exchange_rate",
                value=str(request.base_rate),
                description="Base conversion rate: $1 = X credits"
            )
            db.add(setting)
            old_base_rate = 10000 # Default
        else:
            old_base_rate = int(setting.value)
            setting.value = str(request.base_rate)
            setting.updated_at = datetime.utcnow()

        db.commit()

        return ExchangeRateUpdateResponse(
            success=True,
            old_base_rate=old_base_rate,
            new_base_rate=request.base_rate,
            updated_at=setting.updated_at if hasattr(setting, 'updated_at') else datetime.utcnow()

        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )