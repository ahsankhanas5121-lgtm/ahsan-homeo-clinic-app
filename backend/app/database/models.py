"""SQLAlchemy ORM Models for database tables"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, Text, Numeric, Date, Time, JSONB
)
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.core.constants import UserRole, AppointmentType, AppointmentStatus, Gender


class User(Base):
    """User/Staff model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.RECEPTIONIST, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    phone = Column(String(20))
    department = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    patients = relationship("Patient", back_populates="created_by_user")
    appointments_as_doctor = relationship(
        "Appointment",
        back_populates="doctor",
        foreign_keys="Appointment.doctor_id"
    )
    consultations = relationship("Consultation", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")
    billing_invoices = relationship("BillingInvoice", back_populates="created_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"


class Patient(Base):
    """Patient model"""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(20), unique=True, index=True, nullable=False)  # e.g., PAT-001
    full_name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))  # Male, Female, Other
    phone = Column(String(20), index=True)
    whatsapp_number = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    occupation = Column(String(100))
    marital_status = Column(String(20))  # Single, Married, Divorced, Widowed
    height = Column(Numeric(5, 2))  # in cm
    weight = Column(Numeric(5, 2))  # in kg
    blood_group = Column(String(5))  # O+, A-, etc.

    # Medical Information
    main_complaint = Column(Text)
    history_of_present_illness = Column(Text)
    past_history = Column(Text)
    family_history = Column(Text)
    allergies = Column(Text)
    current_medicines = Column(Text)

    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    created_by_user = relationship("User", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient")
    consultations = relationship("Consultation", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    billing_invoices = relationship("BillingInvoice", back_populates="patient")

    def __repr__(self):
        return f"<Patient {self.patient_id} - {self.full_name}>"


class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(String(20), unique=True, index=True, nullable=False)  # e.g., APT-001
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(Time, nullable=False)
    type = Column(String(20), default=AppointmentType.CLINIC_VISIT, nullable=False)  # clinic_visit, online_consultation
    status = Column(String(20), default=AppointmentStatus.SCHEDULED, nullable=False)  # scheduled, completed, cancelled, follow_up
    notes = Column(Text)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", back_populates="appointments_as_doctor")
    consultations = relationship("Consultation", back_populates="appointment")
    billing_invoices = relationship("BillingInvoice", back_populates="appointment")

    def __repr__(self):
        return f"<Appointment {self.appointment_id} - {self.appointment_date} {self.appointment_time}>"


class Consultation(Base):
    """Consultation model"""
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(String(20), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))

    # Homeopathic Case Taking
    mental_symptoms = Column(Text)
    physical_generals = Column(Text)
    thermals = Column(Text)
    food_desires = Column(Text)
    food_aversions = Column(Text)
    sleep_pattern = Column(Text)
    dreams = Column(Text)
    perspiration = Column(Text)
    female_complaints = Column(Text)
    male_complaints = Column(Text)
    particular_symptoms = Column(Text)
    consultation_notes = Column(Text)

    consultation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="consultations")
    doctor = relationship("User", back_populates="consultations")
    appointment = relationship("Appointment", back_populates="consultations")
    prescriptions = relationship("Prescription", back_populates="consultation")

    def __repr__(self):
        return f"<Consultation {self.consultation_id}>"


class Prescription(Base):
    """Prescription model"""
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(String(20), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consultation_id = Column(Integer, ForeignKey("consultations.id"))
    prescription_date = Column(Date, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("User", back_populates="prescriptions")
    consultation = relationship("Consultation", back_populates="prescriptions")
    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Prescription {self.prescription_id}>"


class PrescriptionItem(Base):
    """Prescription Item model"""
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    remedy_name = Column(String(100))
    potency = Column(String(20))  # e.g., 30C, 200C
    dose = Column(String(50))
    frequency = Column(String(50))  # e.g., 3 times daily
    duration = Column(String(50))  # e.g., 7 days
    instructions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    prescription = relationship("Prescription", back_populates="items")
    medicine = relationship("Medicine", back_populates="prescription_items")

    def __repr__(self):
        return f"<PrescriptionItem {self.remedy_name}>"


class Medicine(Base):
    """Medicine/Remedy model"""
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    medicine_code = Column(String(20), unique=True, index=True, nullable=False)
    remedy_name = Column(String(100), nullable=False)
    source = Column(String(100))  # Mineral, Plant, Animal
    potency = Column(String(20))  # e.g., 30C, 200C
    batch_number = Column(String(50))
    quantity = Column(Integer, default=0, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    purchase_price = Column(Numeric(10, 2))
    sale_price = Column(Numeric(10, 2))
    expiry_date = Column(Date)

    # Materia Medica Information
    keynotes = Column(Text)
    mind_symptoms = Column(Text)
    general_symptoms = Column(Text)
    particular_symptoms = Column(Text)
    relationships = Column(Text)
    modalities = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    supplier = relationship("Supplier", back_populates="medicines")
    prescription_items = relationship("PrescriptionItem", back_populates="medicine")

    def __repr__(self):
        return f"<Medicine {self.remedy_name} - {self.potency}>"


class Supplier(Base):
    """Supplier model"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    city = Column(String(50))
    country = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    medicines = relationship("Medicine", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier {self.supplier_name}>"


class BillingInvoice(Base):
    """Billing Invoice model"""
    __tablename__ = "billing_invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(20), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))

    consultation_fee = Column(Numeric(10, 2), default=0)
    medicine_charges = Column(Numeric(10, 2), default=0)
    other_charges = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    payment_method = Column(String(20))  # cash, card, bank_transfer
    payment_status = Column(String(20), default="pending")  # pending, paid, partial
    paid_amount = Column(Numeric(10, 2), default=0)
    remaining_amount = Column(Numeric(10, 2))

    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date)

    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="billing_invoices")
    appointment = relationship("Appointment", back_populates="billing_invoices")
    created_by_user = relationship("User", back_populates="billing_invoices")

    def __repr__(self):
        return f"<BillingInvoice {self.invoice_number}>"


class AuditLog(Base):
    """Audit Log model"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50), nullable=False)  # create, update, delete, login
    table_name = Column(String(100))
    record_id = Column(Integer)
    old_values = Column(JSONB)  # JSON of old values
    new_values = Column(JSONB)  # JSON of new values
    ip_address = Column(String(50))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} - {self.table_name}>"
