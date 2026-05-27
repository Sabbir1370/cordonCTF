from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth import decode_access_token
from .database import get_db

# This is the security scheme that tells FastAPI to expect a Bearer token in the Authorization header
security_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    cursor = Depends(get_db)
) -> dict:
    """
    Extracts the JWT from the request, validates it, and returns the user row
    from the database. Raises 401 if the token is missing, invalid, or the user
    no longer exists.
    """
    token = credentials.credentials

    # Decode the token; this verifies the signature and expiration
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except Exception:
        # JWTError, missing field, etc.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Fetch the actual user from the database
    cursor.execute(
        "SELECT id, username, role, score, solve_count FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def admin_required(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that checks the current user is an admin. Raises 403 if not.
    Use this after `get_current_user` on admin-only endpoints.
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user