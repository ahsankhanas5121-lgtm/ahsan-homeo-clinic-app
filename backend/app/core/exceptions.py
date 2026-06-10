"""Custom Application Exceptions"""

from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """Base application exception"""
    pass


class AuthenticationException(BaseAppException):
    """Authentication related exceptions"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsException(AuthenticationException):
    """Invalid username or password"""
    def __init__(self):
        super().__init__("Invalid username or password")


class TokenExpiredException(AuthenticationException):
    """Token has expired"""
    def __init__(self):
        super().__init__("Token has expired")


class InvalidTokenException(AuthenticationException):
    """Invalid or malformed token"""
    def __init__(self):
        super().__init__("Invalid token")


class UserNotActiveException(AuthenticationException):
    """User account is inactive"""
    def __init__(self):
        super().__init__("User account is inactive")


class PermissionException(BaseAppException):
    """Permission/Authorization related exceptions"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class ResourceNotFoundException(BaseAppException):
    """Resource not found"""
    def __init__(self, resource: str, identifier: str = ""):
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} with id {identifier} not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ValidationException(BaseAppException):
    """Data validation exception"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class ConflictException(BaseAppException):
    """Resource conflict (e.g., duplicate entry)"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class InternalServerException(BaseAppException):
    """Internal server error"""
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
