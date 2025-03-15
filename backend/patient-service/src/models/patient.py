from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Date, Boolean, Integer, Float, ForeignKey, Text, Enum, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class Gender(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"

class BloodType(enum.Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "Unknown"

# Association tables for many-to-many relationships
patient_allergies = Table(
    'patient_allergies',
    Base.metadata,
    Column('patient_id', UUID(as_uuid=True), ForeignKey('patients.id')),
    Column('allergy_id', UUID(as_uuid=True), ForeignKey('allergies.id'))
)

patient_conditions = Table(
    'patient_conditions',
    Base.metadata,
    Column('patient_id', UUID(as_uuid=True), ForeignKey('patients.id')),
    Column('condition_id', UUID(as_uuid=True), ForeignKey('conditions.id'))
)

patient_medications = Table(
    'patient_medications',
    Base.metadata,
    Column('patient_id', UUID(as_uuid=True), ForeignKey('patients.id')),
    Column('medication_id', UUID(as_uuid=True), ForeignKey('medications.id'))
)

class Patient(Base):
    """Patient model for storing basic patient information."""
    __tablename__ = 'patients'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    mrn = Column(String(20), unique=True, nullable=False, index=True, comment="Medical Record Number")
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False, index=True)
    gender = Column(Enum(Gender), nullable=False)
    blood_type = Column(Enum(BloodType), default=BloodType.UNKNOWN)
    
    # Contact information
    email = Column(String(255))
    phone_number = Column(String(20))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    
    # Emergency contact
    emergency_contact_name = Column(String(200))
    emergency_contact_relationship = Column(String(100))
    emergency_contact_phone = Column(String(20))
    
    # Insurance information
    insurance_provider = Column(String(200))
    insurance_policy_number = Column(String(100))
    insurance_group_number = Column(String(100))
    
    # Additional fields
    height_cm = Column(Float)
    weight_kg = Column(Float)
    primary_care_physician = Column(String(200))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Additional structured data can be stored here
    patient_metadata = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_visit_date = Column(DateTime)
    
    # Relationships
    allergies = relationship("Allergy", secondary=patient_allergies, back_populates="patients")
    conditions = relationship("Condition", secondary=patient_conditions, back_populates="patients")
    medications = relationship("Medication", secondary=patient_medications, back_populates="patients")
    lab_results = relationship("LabResult", back_populates="patient", cascade="all, delete-orphan")
    visits = relationship("Visit", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}, MRN: {self.mrn}>"
    
    def to_dict(self):
        """Convert patient object to dictionary."""
        return {
            "id": str(self.id),
            "mrn": self.mrn,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender.value if self.gender else None,
            "blood_type": self.blood_type.value if self.blood_type else None,
            "email": self.email,
            "phone_number": self.phone_number,
            "address": {
                "line1": self.address_line1,
                "line2": self.address_line2,
                "city": self.city,
                "state": self.state,
                "postal_code": self.postal_code,
                "country": self.country
            },
            "emergency_contact": {
                "name": self.emergency_contact_name,
                "relationship": self.emergency_contact_relationship,
                "phone": self.emergency_contact_phone
            },
            "insurance": {
                "provider": self.insurance_provider,
                "policy_number": self.insurance_policy_number,
                "group_number": self.insurance_group_number
            },
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "primary_care_physician": self.primary_care_physician,
            "notes": self.notes,
            "is_active": self.is_active,
            "metadata": self.patient_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_visit_date": self.last_visit_date.isoformat() if self.last_visit_date else None,
            # Only include IDs for relationships to avoid circular references
            "allergies": [str(a.id) for a in self.allergies] if self.allergies else [],
            "conditions": [str(c.id) for c in self.conditions] if self.conditions else [],
            "medications": [str(m.id) for m in self.medications] if self.medications else []
        }

class Allergy(Base):
    """Model for patient allergies."""
    __tablename__ = 'allergies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    severity = Column(String(50))  # Mild, Moderate, Severe
    reaction = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patients = relationship("Patient", secondary=patient_allergies, back_populates="allergies")
    
    def __repr__(self):
        return f"<Allergy {self.name}>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "severity": self.severity,
            "reaction": self.reaction,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Condition(Base):
    """Model for patient medical conditions."""
    __tablename__ = 'conditions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(50))  # Active, Resolved, etc.
    onset_date = Column(Date)
    resolution_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ICD-10 code (International Classification of Diseases)
    icd_code = Column(String(20), index=True)
    
    # Relationships
    patients = relationship("Patient", secondary=patient_conditions, back_populates="conditions")
    
    def __repr__(self):
        return f"<Condition {self.name}>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "icd_code": self.icd_code,
            "onset_date": self.onset_date.isoformat() if self.onset_date else None,
            "resolution_date": self.resolution_date.isoformat() if self.resolution_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Medication(Base):
    """Model for medications patients are taking."""
    __tablename__ = 'medications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(200), nullable=False, index=True)
    dosage = Column(String(100))
    frequency = Column(String(100))
    instructions = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    prescribing_doctor = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional details
    ndc_code = Column(String(20), index=True)  # National Drug Code
    form = Column(String(50))  # Tablet, Liquid, etc.
    
    # Relationships
    patients = relationship("Patient", secondary=patient_medications, back_populates="medications")
    
    def __repr__(self):
        return f"<Medication {self.name}>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "instructions": self.instructions,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "prescribing_doctor": self.prescribing_doctor,
            "ndc_code": self.ndc_code,
            "form": self.form,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class LabResult(Base):
    """Model for patient lab results."""
    __tablename__ = 'lab_results'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'), nullable=False)
    test_name = Column(String(200), nullable=False, index=True)
    test_date = Column(DateTime, nullable=False)
    result_value = Column(String(100), nullable=False)
    unit = Column(String(50))
    reference_range = Column(String(100))
    abnormal_flag = Column(Boolean, default=False)
    status = Column(String(50), default="Final")  # Preliminary, Final, etc.
    performing_lab = Column(String(200))
    ordering_provider = Column(String(200))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # LOINC code (Logical Observation Identifiers Names and Codes)
    loinc_code = Column(String(20), index=True)
    
    # Additional structured data can be stored here
    lab_metadata = Column(JSONB, default={})
    
    # Relationships
    patient = relationship("Patient", back_populates="lab_results")
    
    def __repr__(self):
        return f"<LabResult {self.test_name} for patient {self.patient_id}>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "patient_id": str(self.patient_id),
            "test_name": self.test_name,
            "test_date": self.test_date.isoformat() if self.test_date else None,
            "result_value": self.result_value,
            "unit": self.unit,
            "reference_range": self.reference_range,
            "abnormal_flag": self.abnormal_flag,
            "status": self.status,
            "performing_lab": self.performing_lab,
            "ordering_provider": self.ordering_provider,
            "notes": self.notes,
            "loinc_code": self.loinc_code,
            "metadata": self.lab_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Visit(Base):
    """Model for patient visits/encounters."""
    __tablename__ = 'visits'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'), nullable=False)
    visit_date = Column(DateTime, nullable=False, index=True)
    provider_name = Column(String(200), nullable=False)
    visit_type = Column(String(100), nullable=False)  # Office visit, ER, etc.
    chief_complaint = Column(Text)
    diagnosis = Column(Text)
    treatment_plan = Column(Text)
    follow_up_instructions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Vital signs
    temperature = Column(Float)
    heart_rate = Column(Integer)
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    respiratory_rate = Column(Integer)
    oxygen_saturation = Column(Float)
    
    # Additional structured data can be stored here
    visit_metadata = Column(JSONB, default={})
    
    # Relationships
    patient = relationship("Patient", back_populates="visits")
    
    def __repr__(self):
        return f"<Visit {self.visit_date} for patient {self.patient_id}>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "patient_id": str(self.patient_id),
            "visit_date": self.visit_date.isoformat() if self.visit_date else None,
            "provider_name": self.provider_name,
            "visit_type": self.visit_type,
            "chief_complaint": self.chief_complaint,
            "diagnosis": self.diagnosis,
            "treatment_plan": self.treatment_plan,
            "follow_up_instructions": self.follow_up_instructions,
            "vital_signs": {
                "temperature": self.temperature,
                "heart_rate": self.heart_rate,
                "blood_pressure": f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}" 
                    if self.blood_pressure_systolic and self.blood_pressure_diastolic else None,
                "respiratory_rate": self.respiratory_rate,
                "oxygen_saturation": self.oxygen_saturation
            },
            "visit_metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }