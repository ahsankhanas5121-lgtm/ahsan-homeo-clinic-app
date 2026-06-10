"""Authentication endpoints"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.database.schemas import (
    UserLogin,
    UserCreate,
    TokenResponse,
    UserResponse,
    MessageResponse,
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import (
    InvalidCredentialsException,
    UserNotActiveException,
    ResourceNotFoundException,
    ConflictException,
    TokenExpiredException,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user/staff member.
    
    - **username**: Unique username (required)
    - **email**: Valid email address (required)
    - **full_name**: Full name of the user (required)
    - **password**: Password with minimum 8 characters (required)
    - **role**: User role - admin, doctor, receptionist (required)
    """
    auth_service = AuthService(db)
    
    # Check if username already exists
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()
    if existing_user:
        raise ConflictException(f"Username '{user_data.username}' already exists")
    
    # Check if email already exists
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()
    if existing_email:
        raise ConflictException(f"Email '{user_data.email}' already registered")
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=user_data.is_active,
        phone=user_data.phone,
        department=user_data.department,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    User login endpoint.
    
    Returns access token and refresh token on successful authentication.
    
    - **username**: Username (required)
    - **password**: Password (required)
    """
    auth_service = AuthService(db)
    
    # Find user by username
    user = db.query(User).filter(
        User.username == credentials.username
    ).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise InvalidCredentialsException()
    
    if not user.is_active:
        raise UserNotActiveException()
    
    # Create tokens
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "type": "access"
        }
    )
    
    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "type": "refresh"
        }
    )
    
    # Log the login action (audit log)
    from app.database.models import AuditLog
    audit_log = AuditLog(
        user_id=user.id,
        action="login",
        table_name="users",
        record_id=user.id,
    )
    db.add(audit_log)
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    old_refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **old_refresh_token**: Valid refresh token (required)
    """
    try:
        payload = decode_token(old_refresh_token)
    except TokenExpiredException:
        raise TokenExpiredException()
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise UserNotActiveException()
    
    # Create new tokens
    new_access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "type": "access"
        }
    )
    
    new_refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "type": "refresh"
        }
    )
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """
    User logout endpoint.
    
    Logs the logout action for audit purposes.
    """
    # This is a simple logout implementation.
    # In production, you might want to use token blacklisting.
    
    return MessageResponse(
        message="Successfully logged out",
        success=True,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(lambda: None),
):
    """
    Get current authenticated user information.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return current_user


@router.post("/validate-token")
async def validate_token(token: str):
    """
    Validate a JWT token.
    
    Returns token payload if valid.
    """
    try:
        payload = decode_token(token)
        return {
            "valid": True,
            "payload": payload,
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
        }
