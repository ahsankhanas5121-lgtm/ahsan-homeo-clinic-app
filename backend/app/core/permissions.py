"""Role-Based Access Control (RBAC)"""

from typing import List, Optional
from app.core.constants import UserRole


class Permission:
    """Permission class for RBAC"""
    
    # Patient Permissions
    PATIENT_READ = "patient:read"
    PATIENT_CREATE = "patient:create"
    PATIENT_UPDATE = "patient:update"
    PATIENT_DELETE = "patient:delete"
    
    # Appointment Permissions
    APPOINTMENT_READ = "appointment:read"
    APPOINTMENT_CREATE = "appointment:create"
    APPOINTMENT_UPDATE = "appointment:update"
    APPOINTMENT_DELETE = "appointment:delete"
    
    # Consultation Permissions
    CONSULTATION_READ = "consultation:read"
    CONSULTATION_CREATE = "consultation:create"
    CONSULTATION_UPDATE = "consultation:update"
    
    # Prescription Permissions
    PRESCRIPTION_READ = "prescription:read"
    PRESCRIPTION_CREATE = "prescription:create"
    PRESCRIPTION_UPDATE = "prescription:update"
    
    # Medicine Permissions
    MEDICINE_READ = "medicine:read"
    MEDICINE_CREATE = "medicine:create"
    MEDICINE_UPDATE = "medicine:update"
    MEDICINE_DELETE = "medicine:delete"
    
    # Billing Permissions
    BILLING_READ = "billing:read"
    BILLING_CREATE = "billing:create"
    BILLING_UPDATE = "billing:update"
    
    # Admin Permissions
    USER_MANAGE = "user:manage"
    SYSTEM_MANAGE = "system:manage"
    AUDIT_VIEW = "audit:view"


# Role to Permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        # All permissions
        Permission.PATIENT_READ, Permission.PATIENT_CREATE,
        Permission.PATIENT_UPDATE, Permission.PATIENT_DELETE,
        Permission.APPOINTMENT_READ, Permission.APPOINTMENT_CREATE,
        Permission.APPOINTMENT_UPDATE, Permission.APPOINTMENT_DELETE,
        Permission.CONSULTATION_READ, Permission.CONSULTATION_CREATE,
        Permission.CONSULTATION_UPDATE,
        Permission.PRESCRIPTION_READ, Permission.PRESCRIPTION_CREATE,
        Permission.PRESCRIPTION_UPDATE,
        Permission.MEDICINE_READ, Permission.MEDICINE_CREATE,
        Permission.MEDICINE_UPDATE, Permission.MEDICINE_DELETE,
        Permission.BILLING_READ, Permission.BILLING_CREATE,
        Permission.BILLING_UPDATE,
        Permission.USER_MANAGE, Permission.SYSTEM_MANAGE,
        Permission.AUDIT_VIEW,
    ],
    UserRole.DOCTOR: [
        # Patient permissions
        Permission.PATIENT_READ, Permission.PATIENT_CREATE,
        Permission.PATIENT_UPDATE,
        # Appointment permissions
        Permission.APPOINTMENT_READ, Permission.APPOINTMENT_UPDATE,
        # Consultation permissions
        Permission.CONSULTATION_READ, Permission.CONSULTATION_CREATE,
        Permission.CONSULTATION_UPDATE,
        # Prescription permissions
        Permission.PRESCRIPTION_READ, Permission.PRESCRIPTION_CREATE,
        Permission.PRESCRIPTION_UPDATE,
        # Medicine read-only
        Permission.MEDICINE_READ,
        # Billing read
        Permission.BILLING_READ,
    ],
    UserRole.RECEPTIONIST: [
        # Patient permissions
        Permission.PATIENT_READ, Permission.PATIENT_CREATE,
        # Appointment permissions
        Permission.APPOINTMENT_READ, Permission.APPOINTMENT_CREATE,
        Permission.APPOINTMENT_UPDATE,
        # Billing permissions
        Permission.BILLING_READ, Permission.BILLING_CREATE,
        Permission.BILLING_UPDATE,
        # Medicine read-only
        Permission.MEDICINE_READ,
    ],
}


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission"""
    if role not in ROLE_PERMISSIONS:
        return False
    return permission in ROLE_PERMISSIONS[role]


def has_any_permission(role: str, permissions: List[str]) -> bool:
    """Check if a role has any of the given permissions"""
    return any(has_permission(role, perm) for perm in permissions)


def has_all_permissions(role: str, permissions: List[str]) -> bool:
    """Check if a role has all of the given permissions"""
    return all(has_permission(role, perm) for perm in permissions)
