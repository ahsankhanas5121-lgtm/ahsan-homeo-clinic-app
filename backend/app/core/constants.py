"""Application Constants"""

# User Roles
class UserRole:
    """User role constants"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    RECEPTIONIST = "receptionist"
    
    ALL_ROLES = [ADMIN, DOCTOR, RECEPTIONIST]


# Appointment Types
class AppointmentType:
    """Appointment type constants"""
    CLINIC_VISIT = "clinic_visit"
    ONLINE_CONSULTATION = "online_consultation"
    
    ALL_TYPES = [CLINIC_VISIT, ONLINE_CONSULTATION]


# Appointment Status
class AppointmentStatus:
    """Appointment status constants"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FOLLOW_UP = "follow_up"
    NO_SHOW = "no_show"
    
    ALL_STATUSES = [SCHEDULED, COMPLETED, CANCELLED, FOLLOW_UP, NO_SHOW]


# Gender
class Gender:
    """Gender constants"""
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    
    ALL_GENDERS = [MALE, FEMALE, OTHER]


# Marital Status
class MaritalStatus:
    """Marital status constants"""
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"
    
    ALL_STATUSES = [SINGLE, MARRIED, DIVORCED, WIDOWED]


# Blood Groups
class BloodGroup:
    """Blood group constants"""
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    
    ALL_GROUPS = [O_POSITIVE, O_NEGATIVE, A_POSITIVE, A_NEGATIVE,
                   B_POSITIVE, B_NEGATIVE, AB_POSITIVE, AB_NEGATIVE]


# Payment Methods
class PaymentMethod:
    """Payment method constants"""
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    ONLINE = "online"
    
    ALL_METHODS = [CASH, CARD, BANK_TRANSFER, ONLINE]


# Payment Status
class PaymentStatus:
    """Payment status constants"""
    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    
    ALL_STATUSES = [PENDING, PAID, PARTIAL, CANCELLED, REFUNDED]


# Audit Actions
class AuditAction:
    """Audit action constants"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    VIEW = "view"
    EXPORT = "export"
    
    ALL_ACTIONS = [CREATE, UPDATE, DELETE, LOGIN, LOGOUT, VIEW, EXPORT]
