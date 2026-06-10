"""Appointment Service"""

from datetime import datetime, date, time
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session

from app.database.models import Appointment, AuditLog
from app.database.schemas import AppointmentCreate, AppointmentUpdate
from app.core.exceptions import ResourceNotFoundException


class AppointmentService:
    """Service for appointment operations"""
    
    def __init__(self, db: Session):
        """Initialize appointment service with database session"""
        self.db = db
    
    def generate_appointment_id(self) -> str:
        """
        Generate unique appointment ID (APT-001, APT-002, etc.).
        
        Returns:
            Generated appointment ID
        """
        appointment_count = self.db.query(Appointment).count()
        next_id = appointment_count + 1
        return f"APT-{next_id:05d}"
    
    def create_appointment(
        self,
        appointment_data: AppointmentCreate,
        created_by_user_id: int,
    ) -> Appointment:
        """
        Create a new appointment.
        
        Args:
            appointment_data: Appointment creation data
            created_by_user_id: ID of user creating the appointment
            
        Returns:
            Created Appointment object
        """
        # Generate appointment ID
        appointment_id = self.generate_appointment_id()
        
        # Create new appointment
        new_appointment = Appointment(
            appointment_id=appointment_id,
            patient_id=appointment_data.patient_id,
            doctor_id=appointment_data.doctor_id,
            appointment_date=appointment_data.appointment_date,
            appointment_time=appointment_data.appointment_time,
            type=appointment_data.type,
            notes=appointment_data.notes,
            status="scheduled",
        )
        
        self.db.add(new_appointment)
        self.db.commit()
        self.db.refresh(new_appointment)
        
        # Log appointment creation
        audit_log = AuditLog(
            user_id=created_by_user_id,
            action="create",
            table_name="appointments",
            record_id=new_appointment.id,
            new_values={
                "appointment_id": appointment_id,
                "patient_id": appointment_data.patient_id,
                "appointment_date": str(appointment_data.appointment_date),
            },
        )
        self.db.add(audit_log)
        self.db.commit()
        
        return new_appointment
    
    def get_appointment(self, appointment_id: int) -> Appointment:
        """
        Get appointment by ID.
        
        Args:
            appointment_id: Appointment's ID
            
        Returns:
            Appointment object
            
        Raises:
            ResourceNotFoundException: If appointment not found
        """
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.deleted_at.is_(None),
        ).first()
        
        if not appointment:
            raise ResourceNotFoundException("Appointment", str(appointment_id))
        
        return appointment
    
    def list_appointments(
        self,
        page: int = 1,
        page_size: int = 20,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        doctor_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        status: Optional[str] = None,
        appointment_type: Optional[str] = None,
    ) -> Tuple[List[Appointment], int]:
        """
        List appointments with filtering and pagination.
        
        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            date_from: Filter from date
            date_to: Filter to date
            doctor_id: Filter by doctor
            patient_id: Filter by patient
            status: Filter by status
            appointment_type: Filter by type
            
        Returns:
            Tuple of (appointments list, total count)
        """
        query = self.db.query(Appointment).filter(Appointment.deleted_at.is_(None))
        
        # Apply filters
        if date_from:
            query = query.filter(Appointment.appointment_date >= date_from)
        
        if date_to:
            query = query.filter(Appointment.appointment_date <= date_to)
        
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        if appointment_type:
            query = query.filter(Appointment.type == appointment_type)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and sorting
        appointments = query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc(),
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return appointments, total
    
    def update_appointment(
        self,
        appointment_id: int,
        appointment_data: AppointmentUpdate,
    ) -> Appointment:
        """
        Update appointment information.
        
        Args:
            appointment_id: Appointment's ID
            appointment_data: Updated appointment data
            
        Returns:
            Updated Appointment object
            
        Raises:
            ResourceNotFoundException: If appointment not found
        """
        appointment = self.get_appointment(appointment_id)
        
        # Update fields
        update_data = appointment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(appointment, field, value)
        
        appointment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def update_appointment_status(
        self,
        appointment_id: int,
        new_status: str,
    ) -> Appointment:
        """
        Update appointment status.
        
        Args:
            appointment_id: Appointment's ID
            new_status: New status value
            
        Returns:
            Updated Appointment object
        """
        appointment = self.get_appointment(appointment_id)
        appointment.status = new_status
        appointment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def cancel_appointment(self, appointment_id: int) -> None:
        """
        Cancel an appointment (soft delete).
        
        Args:
            appointment_id: Appointment's ID
            
        Raises:
            ResourceNotFoundException: If appointment not found
        """
        appointment = self.get_appointment(appointment_id)
        appointment.status = "cancelled"
        appointment.deleted_at = datetime.utcnow()
        self.db.commit()
    
    def check_appointment_conflict(
        self,
        doctor_id: int,
        appointment_date: date,
        appointment_time: time,
        exclude_appointment_id: Optional[int] = None,
    ) -> bool:
        """
        Check if there's a time slot conflict for a doctor.
        
        Args:
            doctor_id: Doctor's ID
            appointment_date: Appointment date
            appointment_time: Appointment time
            exclude_appointment_id: Appointment ID to exclude from check
            
        Returns:
            True if conflict exists, False otherwise
        """
        query = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status.in_(["scheduled", "completed"]),
            Appointment.deleted_at.is_(None),
        )
        
        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
        
        return query.first() is not None
    
    def get_doctor_schedule(
        self,
        doctor_id: int,
        date_from: date,
        date_to: date,
    ) -> List[Appointment]:
        """
        Get doctor's schedule for a date range.
        
        Args:
            doctor_id: Doctor's ID
            date_from: Start date
            date_to: End date
            
        Returns:
            List of appointments for the date range
        """
        appointments = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= date_from,
            Appointment.appointment_date <= date_to,
            Appointment.status.in_(["scheduled", "completed"]),
            Appointment.deleted_at.is_(None),
        ).order_by(
            Appointment.appointment_date.asc(),
            Appointment.appointment_time.asc(),
        ).all()
        
        return appointments
