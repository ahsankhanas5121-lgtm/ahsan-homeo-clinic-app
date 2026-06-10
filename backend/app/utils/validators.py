"""Input validation utilities"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Validate Pakistani phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if phone is valid, False otherwise
    """
    # Accept formats like 03001234567, +923001234567, 0300-123-4567
    pattern = r'^(\+92|0)[0-9]{10}$'
    # Remove common separators
    clean_phone = phone.replace('-', '').replace(' ', '')
    return re.match(pattern, clean_phone) is not None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_age(age: int) -> bool:
    """
    Validate patient age.
    
    Args:
        age: Age to validate
        
    Returns:
        True if age is valid, False otherwise
    """
    return 0 < age < 150


def validate_blood_group(blood_group: str) -> bool:
    """
    Validate blood group.
    
    Args:
        blood_group: Blood group to validate
        
    Returns:
        True if blood group is valid, False otherwise
    """
    valid_groups = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
    return blood_group in valid_groups
