"""JWT Authentication Middleware"""

from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.core.security import decode_token, extract_token_from_header
from app.core.exceptions import InvalidTokenException, UserNotActiveException


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Dependency to get current authenticated user.
    
    Extracts JWT token from Authorization header and validates it.
    
    Returns:
        User object if authentication successful, raises exception otherwise
    """
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token
    try:
        token = extract_token_from_header(auth_header)
    except InvalidTokenException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode token
    try:
        payload = decode_token(token)
    except InvalidTokenException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current authenticated admin user.
    
    Returns:
        User object if user is admin, raises exception otherwise
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access this resource",
        )
    return current_user


async def get_current_doctor_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current authenticated doctor user.
    
    Returns:
        User object if user is doctor or admin, raises exception otherwise
    """
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors and admin can access this resource",
        )
    return current_user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current authenticated active user.
    
    Returns:
        Active User object
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )
    return current_user
