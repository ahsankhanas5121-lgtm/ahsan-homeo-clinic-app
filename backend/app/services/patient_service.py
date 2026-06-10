"""Patient Service"""

from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.models import Patient, User, AuditLog
from app.database.schemas import PatientCreate, PatientUpdate
from app.core.exceptions import ResourceNotFoundException


class PatientService:
    """Service for patient operations"""
    
    def __init__(self, db: Session):
        """Initialize patient service with database session"""
        self.db = db
    
    def generate_patient_id(self) -> str:
        """
        Generate unique patient ID (PAT-001, PAT-002, etc.).
        
        Returns:
            Generated patient ID
        """
        # Get the count of existing patients
        patient_count = self.db.query(Patient).count()
        next_id = patient_count + 1
        return f"PAT-{next_id:05d}"
    
    def create_patient(self, patient_data: PatientCreate, created_by_user_id: int) -> Patient:
        """
        Create a new patient record.
        
        Args:
            patient_data: Patient creation data
            created_by_user_id: ID of user creating the patient
            
        Returns:
            Created Patient object
        """
        # Generate patient ID
        patient_id = self.generate_patient_id()
        
        # Create new patient
        new_patient = Patient(
            patient_id=patient_id,
            full_name=patient_data.full_name,
            age=patient_data.age,
            gender=patient_data.gender,
            phone=patient_data.phone,
            whatsapp_number=patient_data.whatsapp_number,
            email=patient_data.email,
            address=patient_data.address,
            occupation=patient_data.occupation,
            marital_status=patient_data.marital_status,
            height=patient_data.height,
            weight=patient_data.weight,
            blood_group=patient_data.blood_group,
            main_complaint=patient_data.main_complaint,
            history_of_present_illness=patient_data.history_of_present_illness,
            past_history=patient_data.past_history,
            family_history=patient_data.family_history,
            allergies=patient_data.allergies,
            current_medicines=patient_data.current_medicines,
            created_by_user_id=created_by_user_id,
        )
        
        self.db.add(new_patient)
        self.db.commit()
        self.db.refresh(new_patient)
        
        # Log patient creation
        audit_log = AuditLog(
            user_id=created_by_user_id,
            action="create",
            table_name="patients",
            record_id=new_patient.id,
            new_values={
                "patient_id": patient_id,
                "full_name": patient_data.full_name,
                "age": patient_data.age,
            },
        )
        self.db.add(audit_log)
        self.db.commit()
        
        return new_patient
    
    def get_patient(self, patient_id: int) -> Patient:
        """
        Get patient by ID.
        
        Args:
            patient_id: Patient's ID
            
        Returns:
            Patient object
            
        Raises:
            ResourceNotFoundException: If patient not found
        """
        patient = self.db.query(Patient).filter(
            Patient.id == patient_id,
            Patient.deleted_at.is_(None),
        ).first()
        
        if not patient:
            raise ResourceNotFoundException("Patient", str(patient_id))
        
        return patient
    
    def get_patient_by_patient_id(self, patient_id: str) -> Optional[Patient]:
        """
        Get patient by patient ID (PAT-001, etc.).
        
        Args:
            patient_id: Patient's patient ID
            
        Returns:
            Patient object or None if not found
        """
        return self.db.query(Patient).filter(
            Patient.patient_id == patient_id,
            Patient.deleted_at.is_(None),
        ).first()
    
    def list_patients(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        gender: Optional[str] = None,
        blood_group: Optional[str] = None,
    ) -> Tuple[List[Patient], int]:
        """
        List patients with filtering and pagination.
        
        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            search: Search by name, phone, or patient ID
            gender: Filter by gender
            blood_group: Filter by blood group
            
        Returns:
            Tuple of (patients list, total count)
        """
        query = self.db.query(Patient).filter(Patient.deleted_at.is_(None))
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Patient.full_name.ilike(search_term),
                    Patient.phone.ilike(search_term),
                    Patient.patient_id.ilike(search_term),
                )
            )
        
        if gender:
            query = query.filter(Patient.gender == gender)
        
        if blood_group:
            query = query.filter(Patient.blood_group == blood_group)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        patients = query.order_by(
            Patient.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return patients, total
    
    def update_patient(self, patient_id: int, patient_data: PatientUpdate) -> Patient:
        """
        Update patient information.
        
        Args:
            patient_id: Patient's ID
            patient_data: Updated patient data
            
        Returns:
            Updated Patient object
            
        Raises:
            ResourceNotFoundException: If patient not found
        """
        patient = self.get_patient(patient_id)
        
        # Store old values for audit log
        old_values = {
            "full_name": patient.full_name,
            "age": patient.age,
            "phone": patient.phone,
        }
        
        # Update fields
        update_data = patient_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
        
        patient.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(patient)
        
        return patient
    
    def delete_patient(self, patient_id: int) -> None:
        """
        Delete/Deactivate a patient record (soft delete).
        
        Args:
            patient_id: Patient's ID
            
        Raises:
            ResourceNotFoundException: If patient not found
        """
        patient = self.get_patient(patient_id)
        patient.deleted_at = datetime.utcnow()
        self.db.commit()
    
    def search_patients(self, search_term: str) -> List[Patient]:
        """
        Search patients by name, phone, or patient ID.
        
        Args:
            search_term: Search term
            
        Returns:
            List of matching patients
        """
        search_pattern = f"%{search_term}%"
        return self.db.query(Patient).filter(
            Patient.deleted_at.is_(None),
            or_(
                Patient.full_name.ilike(search_pattern),
                Patient.phone.ilike(search_pattern),
                Patient.patient_id.ilike(search_pattern),
                Patient.email.ilike(search_pattern),
            )
        ).order_by(Patient.full_name).all()
