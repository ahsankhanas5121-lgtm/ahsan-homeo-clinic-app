"""Pydantic schemas for request/response validation"""

from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator

from app.core.constants import UserRole, AppointmentType, AppointmentStatus


# ============== Base Schemas ==============

class BaseSchema(BaseModel):
    """Base schema with common config"""
    class Config:
        from_attributes = True


# ============== User Schemas ==============

class UserBase(BaseSchema):
    """Base user schema"""
    username: str
    email: EmailStr
    full_name: str
    role: str = UserRole.RECEPTIONIST
    is_active: bool = True
    phone: Optional[str] = None
    department: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str

    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserUpdate(BaseSchema):
    """User update schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    created_at: datetime
    updated_at: datetime


# ============== Authentication Schemas ==============

class UserLogin(BaseSchema):
    """User login schema"""
    username: str
    password: str


class TokenResponse(BaseSchema):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefresh(BaseSchema):
    """Token refresh schema"""
    refresh_token: str


class TokenPayload(BaseSchema):
    """Token payload schema"""
    sub: int
    role: str
    type: str = "access"


# ============== Patient Schemas ==============

class PatientBase(BaseSchema):
    """Base patient schema"""
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    occupation: Optional[str] = None
    marital_status: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    blood_group: Optional[str] = None
    main_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    past_history: Optional[str] = None
    family_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medicines: Optional[str] = None


class PatientCreate(PatientBase):
    """Patient creation schema"""
    pass


class PatientUpdate(BaseSchema):
    """Patient update schema"""
    full_name: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    main_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    past_history: Optional[str] = None
    family_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medicines: Optional[str] = None


class PatientResponse(PatientBase):
    """Patient response schema"""
    id: int
    patient_id: str
    created_at: datetime
    updated_at: datetime


# ============== Appointment Schemas ==============

class AppointmentBase(BaseSchema):
    """Base appointment schema"""
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    type: str = AppointmentType.CLINIC_VISIT
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    """Appointment creation schema"""
    pass


class AppointmentUpdate(BaseSchema):
    """Appointment update schema"""
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    notes: Optional[str] = None


class AppointmentStatusUpdate(BaseSchema):
    """Appointment status update schema"""
    status: str


class AppointmentResponse(AppointmentBase):
    """Appointment response schema"""
    id: int
    appointment_id: str
    status: str
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime


# ============== Pagination Schemas ==============

class PaginationParams(BaseSchema):
    """Pagination parameters"""
    page: int = 1
    page_size: int = 20

    @validator('page')
    def page_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('Page must be >= 1')
        return v

    @validator('page_size')
    def page_size_must_be_valid(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Page size must be between 1 and 100')
        return v


class PaginatedResponse(BaseSchema):
    """Paginated response schema"""
    items: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== Generic Response Schemas ==============

class MessageResponse(BaseSchema):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseSchema):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
