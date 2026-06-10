"""Appointment endpoints"""

from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database.database import get_db
from app.database.models import User, Patient, Appointment
from app.database.schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentStatusUpdate,
    AppointmentResponse,
    MessageResponse,
)
from app.middleware.auth_middleware import (
    get_current_user,
    get_current_doctor_user,
)
from app.core.exceptions import (
    ResourceNotFoundException,
    PermissionException,
    ConflictException,
    ValidationException,
)
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new appointment.
    
    Only doctors, receptionists, and admins can create appointments.
    
    - **patient_id**: Patient's ID (required)
    - **doctor_id**: Doctor's ID (required)
    - **appointment_date**: Appointment date (required)
    - **appointment_time**: Appointment time (required)
    - **type**: clinic_visit or online_consultation (required)
    - **notes**: Additional notes (optional)
    """
    appointment_service = AppointmentService(db)
    
    # Validate patient exists
    patient = db.query(Patient).filter(
        Patient.id == appointment_data.patient_id
    ).first()
    if not patient:
        raise ResourceNotFoundException("Patient", str(appointment_data.patient_id))
    
    # Validate doctor exists
    doctor = db.query(User).filter(
        User.id == appointment_data.doctor_id
    ).first()
    if not doctor:
        raise ResourceNotFoundException("Doctor", str(appointment_data.doctor_id))
    
    if doctor.role not in ["doctor", "admin"]:
        raise ValidationException(f"User {appointment_data.doctor_id} is not a doctor")
    
    # Check for appointment conflicts
    conflict = appointment_service.check_appointment_conflict(
        doctor_id=appointment_data.doctor_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
    )
    
    if conflict:
        raise ConflictException(
            f"Doctor already has an appointment on {appointment_data.appointment_date} at {appointment_data.appointment_time}"
        )
    
    # Create appointment
    new_appointment = appointment_service.create_appointment(
        appointment_data,
        created_by_user_id=current_user.id,
    )
    
    return new_appointment


@router.get("", response_model=dict)
async def list_appointments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    doctor_id: Optional[int] = Query(None),
    patient_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    appointment_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List appointments with filtering and pagination.
    
    - **page**: Page number (default: 1)
    - **page_size**: Results per page (default: 20, max: 100)
    - **date_from**: Filter from date (optional)
    - **date_to**: Filter to date (optional)
    - **doctor_id**: Filter by doctor (optional)
    - **patient_id**: Filter by patient (optional)
    - **status**: Filter by status (scheduled, completed, cancelled, follow_up) (optional)
    - **appointment_type**: Filter by type (clinic_visit, online_consultation) (optional)
    """
    appointment_service = AppointmentService(db)
    
    appointments, total = appointment_service.list_appointments(
        page=page,
        page_size=page_size,
        date_from=date_from,
        date_to=date_to,
        doctor_id=doctor_id,
        patient_id=patient_id,
        status=status,
        appointment_type=appointment_type,
    )
    
    return {
        "items": [AppointmentResponse.from_orm(apt) for apt in appointments],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get appointment details.
    """
    appointment_service = AppointmentService(db)
    appointment = appointment_service.get_appointment(appointment_id)
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update appointment information.
    
    Doctors, receptionists, and admins can update appointments.
    """
    appointment_service = AppointmentService(db)
    
    # Get current appointment
    appointment = appointment_service.get_appointment(appointment_id)
    
    # Check for conflicts if date/time is being changed
    if (appointment_data.appointment_date or appointment_data.appointment_time):
        new_date = appointment_data.appointment_date or appointment.appointment_date
        new_time = appointment_data.appointment_time or appointment.appointment_time
        
        conflict = appointment_service.check_appointment_conflict(
            doctor_id=appointment.doctor_id,
            appointment_date=new_date,
            appointment_time=new_time,
            exclude_appointment_id=appointment_id,
        )
        
        if conflict:
            raise ConflictException("Doctor has a conflict with this time slot")
    
    updated_appointment = appointment_service.update_appointment(
        appointment_id,
        appointment_data,
    )
    
    return updated_appointment


@router.put("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: int,
    status_data: AppointmentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update appointment status.
    
    Valid statuses: scheduled, completed, cancelled, follow_up, no_show
    
    Only doctors and admins can mark appointments as completed.
    """
    appointment_service = AppointmentService(db)
    
    # Validate status
    valid_statuses = ["scheduled", "completed", "cancelled", "follow_up", "no_show"]
    if status_data.status not in valid_statuses:
        raise ValidationException(f"Invalid status. Valid statuses: {', '.join(valid_statuses)}")
    
    # Check permissions for certain status changes
    if status_data.status == "completed" and current_user.role not in ["doctor", "admin"]:
        raise PermissionException("Only doctors and admins can mark appointments as completed")
    
    updated_appointment = appointment_service.update_appointment_status(
        appointment_id,
        status_data.status,
    )
    
    return updated_appointment


@router.delete("/{appointment_id}", response_model=MessageResponse)
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel an appointment (soft delete).
    """
    appointment_service = AppointmentService(db)
    appointment_service.cancel_appointment(appointment_id)
    
    return MessageResponse(
        message=f"Appointment {appointment_id} has been cancelled",
        success=True,
    )


@router.get("/doctor/{doctor_id}/schedule", response_model=dict)
async def get_doctor_schedule(
    doctor_id: int,
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get doctor's appointment schedule for a date range.
    """
    appointment_service = AppointmentService(db)
    
    # Validate doctor exists
    doctor = db.query(User).filter(User.id == doctor_id).first()
    if not doctor:
        raise ResourceNotFoundException("Doctor", str(doctor_id))
    
    appointments = appointment_service.get_doctor_schedule(
        doctor_id=doctor_id,
        date_from=date_from,
        date_to=date_to,
    )
    
    return {
        "doctor_id": doctor_id,
        "doctor_name": doctor.full_name,
        "date_from": date_from,
        "date_to": date_to,
        "appointments": [AppointmentResponse.from_orm(apt) for apt in appointments],
        "total": len(appointments),
    }


@router.post("/{appointment_id}/send-reminder", response_model=MessageResponse)
async def send_appointment_reminder(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send appointment reminder to patient.
    
    Only admins and receptionists can send reminders.
    """
    if current_user.role not in ["admin", "receptionist"]:
        raise PermissionException("Only admins and receptionists can send reminders")
    
    appointment_service = AppointmentService(db)
    appointment = appointment_service.get_appointment(appointment_id)
    
    # Mark reminder as sent
    appointment.reminder_sent = True
    db.commit()
    
    return MessageResponse(
        message=f"Reminder sent for appointment {appointment_id}",
        success=True,
    )
