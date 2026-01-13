from fastapi import HTTPException, Security, status, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.core.config import settings

# Headers
service_token_header = APIKeyHeader(name="X-Service-Token", auto_error=True)
admin_token_header = APIKeyHeader(name="X-Admin-Token", auto_error=True)
bearer_scheme = HTTPBearer(auto_error=True)


def verify_service_token(token: str = Security(service_token_header)) -> str:
    """
    Service-to-service token validation

    Args:
    token: Token with header X-Service-Token

    Returns:
    token: Validated token

    Raises:
    HTTPException: If token is invalid
    """
    if token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service token"
        )
    return token

def verify_admin_token(token: str = Security(admin_token_header)) -> str:
    """
    Admin token validation

    Args:
    token: Token with header X-Admin-Token

    Returns:
    token: Validated token

    Raises:
    HTTPException: If token is invalid
    """
    if token != settings.ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin token"
        )
    return token

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> str:
    """
    Getting user_id from Bearer token

    In production this should be a real JWT validation.
    For demo we just extract user_id from token.

    Args:
    credentials: Bearer token

    Returns:
    user_id: User ID

    Example token format: "Bearer user_123"
    """
    token = credentials.credentials

    # DEMO: Just use the token as user_id
    # In production, you need to validate the JWT and extract the user_id
    if not token or len(token) < 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # For production, add real JWT validation:
    # try:
    # payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    # user_id = payload.get("sub")
    # if not user_id:
    # raise HTTPException(...)
    # return user_id
    # except JWTError:
    # raise HTTPException(...)
    # DEMO: token = user_id
    return token


# Dependencies
async def require_service_token(token: str = Security(service_token_header)) -> str:
    """Dependency для internal API"""
    return verify_service_token(token)


async def require_admin_token(token: str = Security(admin_token_header)) -> str:
    """Dependency для admin API"""
    return verify_admin_token(token)


async def require_user(user_id: str = Depends(get_current_user)) -> str:
    """Dependency для public API"""
    return user_id



