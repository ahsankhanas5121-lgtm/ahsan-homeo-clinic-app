"""Authentication Service"""

from datetime import datetime
from sqlalchemy.orm import Session

from app.database.models import User, AuditLog
from app.core.security import verify_password, get_password_hash
from app.core.exceptions import (
    InvalidCredentialsException,
    UserNotActiveException,
    ResourceNotFoundException,
)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: Session):
        """Initialize auth service with database session"""
        self.db = db
    
    def authenticate_user(self, username: str, password: str) -> User:
        """
        Authenticate user with username and password.
        
        Args:
            username: User's username
            password: User's password (plain text)
            
        Returns:
            User object if authentication successful
            
        Raises:
            InvalidCredentialsException: If credentials are invalid
            UserNotActiveException: If user account is inactive
        """
        # Find user by username
        user = self.db.query(User).filter(
            User.username == username
        ).first()
        
        if not user:
            raise InvalidCredentialsException()
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        
        # Check if user is active
        if not user.is_active:
            raise UserNotActiveException()
        
        return user
    
    def get_user_by_id(self, user_id: int) -> User:
        """
        Get user by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            User object
            
        Raises:
            ResourceNotFoundException: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ResourceNotFoundException("User", str(user_id))
        
        return user
    
    def get_user_by_username(self, username: str) -> User:
        """
        Get user by username.
        
        Args:
            username: User's username
            
        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(
            User.username == username
        ).first()
    
    def get_user_by_email(self, email: str) -> User:
        """
        Get user by email.
        
        Args:
            email: User's email
            
        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(
            User.email == email
        ).first()
    
    def create_user(
        self,
        username: str,
        email: str,
        full_name: str,
        password: str,
        role: str = "receptionist",
        phone: str = None,
        department: str = None,
    ) -> User:
        """
        Create a new user.
        
        Args:
            username: User's username
            email: User's email
            full_name: User's full name
            password: User's password (plain text)
            role: User's role
            phone: User's phone number
            department: User's department
            
        Returns:
            Created User object
        """
        # Check if username exists
        if self.get_user_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        
        # Check if email exists
        if self.get_user_by_email(email):
            raise ValueError(f"Email '{email}' already exists")
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Create user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=role,
            is_active=True,
            phone=phone,
            department=department,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Log user creation
        audit_log = AuditLog(
            user_id=None,  # System action
            action="create",
            table_name="users",
            record_id=user.id,
            new_values={"username": username, "email": email, "role": role},
        )
        self.db.add(audit_log)
        self.db.commit()
        
        return user
    
    def update_password(self, user_id: int, new_password: str) -> User:
        """
        Update user's password.
        
        Args:
            user_id: User's ID
            new_password: New password (plain text)
            
        Returns:
            Updated User object
        """
        user = self.get_user_by_id(user_id)
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def deactivate_user(self, user_id: int) -> User:
        """
        Deactivate a user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            Updated User object
        """
        user = self.get_user_by_id(user_id)
        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def activate_user(self, user_id: int) -> User:
        """
        Activate a user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            Updated User object
        """
        user = self.get_user_by_id(user_id)
        user.is_active = True
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
