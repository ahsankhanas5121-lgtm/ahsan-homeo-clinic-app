"""Patient endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database.database import get_db
from app.database.models import User, Patient, Appointment, Consultation, BillingInvoice
from app.database.schemas import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PaginatedResponse,
    MessageResponse,
)
from app.middleware.auth_middleware import get_current_user
from app.core.exceptions import ResourceNotFoundException, PermissionException
from app.services.patient_service import PatientService
from app.utils.validators import validate_age, validate_blood_group, validate_phone

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new patient record.
    
    Only doctors, receptionists, and admins can create patients.
    
    - **full_name**: Patient's full name (required)
    - **age**: Patient's age (optional)
    - **gender**: Male, Female, or Other (optional)
    - **phone**: Contact phone number (optional)
    - **email**: Patient's email (optional)
    - **address**: Patient's address (optional)
    - **blood_group**: Blood group like O+, A-, etc. (optional)
    - **medical_info**: Main complaint, past history, etc. (optional)
    """
    # Validate age if provided
    if patient_data.age and not validate_age(patient_data.age):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Age must be between 0 and 150"
        )
    
    # Validate blood group if provided
    if patient_data.blood_group and not validate_blood_group(patient_data.blood_group):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid blood group. Valid groups: O+, O-, A+, A-, B+, B-, AB+, AB-"
        )
    
    # Validate phone if provided
    if patient_data.phone and not validate_phone(patient_data.phone):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid phone number format. Use format like 03001234567 or +923001234567"
        )
    
    patient_service = PatientService(db)
    new_patient = patient_service.create_patient(patient_data, current_user.id)
    
    return new_patient


@router.get("", response_model=dict)
async def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    blood_group: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all patients with pagination and filtering.
    
    - **page**: Page number (default: 1)
    - **page_size**: Results per page (default: 20, max: 100)
    - **search**: Search by name, phone, or patient ID
    - **gender**: Filter by gender (Male, Female, Other)
    - **blood_group**: Filter by blood group (O+, A-, etc.)
    """
    patient_service = PatientService(db)
    patients, total = patient_service.list_patients(
        page=page,
        page_size=page_size,
        search=search,
        gender=gender,
        blood_group=blood_group,
    )
    
    return {
        "items": [PatientResponse.from_orm(p) for p in patients],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{patient_id}", response_model=dict)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed patient information.
    
    Returns patient details including:
    - Personal information
    - Medical history
    - Recent appointments
    - Recent consultations
    - Billing history
    """
    patient_service = PatientService(db)
    patient = patient_service.get_patient(patient_id)
    
    # Get related data
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).order_by(Appointment.appointment_date.desc()).limit(5).all()
    
    consultations = db.query(Consultation).filter(
        Consultation.patient_id == patient_id
    ).order_by(Consultation.consultation_date.desc()).limit(5).all()
    
    invoices = db.query(BillingInvoice).filter(
        BillingInvoice.patient_id == patient_id
    ).order_by(BillingInvoice.invoice_date.desc()).limit(5).all()
    
    return {
        "patient": PatientResponse.from_orm(patient),
        "recent_appointments": len(appointments),
        "recent_consultations": len(consultations),
        "recent_invoices": len(invoices),
        "total_appointments": db.query(Appointment).filter(
            Appointment.patient_id == patient_id
        ).count(),
        "total_consultations": db.query(Consultation).filter(
            Consultation.patient_id == patient_id
        ).count(),
    }


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update patient information.
    
    Doctors, receptionists, and admins can update patient records.
    """
    # Validate age if provided
    if patient_data.age and not validate_age(patient_data.age):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Age must be between 0 and 150"
        )
    
    # Validate blood group if provided
    if patient_data.blood_group and not validate_blood_group(patient_data.blood_group):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid blood group"
        )
    
    # Validate phone if provided
    if patient_data.phone and not validate_phone(patient_data.phone):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid phone number format"
        )
    
    patient_service = PatientService(db)
    updated_patient = patient_service.update_patient(patient_id, patient_data)
    
    return updated_patient


@router.delete("/{patient_id}", response_model=MessageResponse)
async def delete_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete/Deactivate a patient record (soft delete).
    
    Only admins can delete patient records.
    """
    if current_user.role != "admin":
        raise PermissionException("Only admins can delete patient records")
    
    patient_service = PatientService(db)
    patient_service.delete_patient(patient_id)
    
    return MessageResponse(
        message=f"Patient {patient_id} has been deactivated",
        success=True,
    )


@router.get("/{patient_id}/appointments", response_model=dict)
async def get_patient_appointments(
    patient_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all appointments for a patient.
    """
    patient_service = PatientService(db)
    patient = patient_service.get_patient(patient_id)
    
    query = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).order_by(Appointment.appointment_date.desc())
    
    total = query.count()
    appointments = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.full_name,
        "items": appointments,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{patient_id}/consultations", response_model=dict)
async def get_patient_consultations(
    patient_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all consultations for a patient.
    """
    patient_service = PatientService(db)
    patient = patient_service.get_patient(patient_id)
    
    query = db.query(Consultation).filter(
        Consultation.patient_id == patient_id
    ).order_by(Consultation.consultation_date.desc())
    
    total = query.count()
    consultations = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.full_name,
        "items": consultations,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{patient_id}/billing", response_model=dict)
async def get_patient_billing(
    patient_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get billing history for a patient.
    """
    patient_service = PatientService(db)
    patient = patient_service.get_patient(patient_id)
    
    query = db.query(BillingInvoice).filter(
        BillingInvoice.patient_id == patient_id
    ).order_by(BillingInvoice.invoice_date.desc())
    
    total = query.count()
    invoices = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # Calculate totals
    all_invoices = db.query(BillingInvoice).filter(
        BillingInvoice.patient_id == patient_id
    ).all()
    
    total_spent = sum(float(inv.total_amount) for inv in all_invoices)
    total_paid = sum(float(inv.paid_amount) for inv in all_invoices)
    outstanding = total_spent - total_paid
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.full_name,
        "items": invoices,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "summary": {
            "total_spent": float(total_spent),
            "total_paid": float(total_paid),
            "outstanding": float(outstanding),
        },
    }
