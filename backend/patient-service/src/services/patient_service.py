from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
import uuid
from sqlalchemy import func, or_, and_, not_, desc, asc, text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import cast
from sqlalchemy.dialects.postgresql import JSONB
from ..models.patient import patient_conditions, patient_medications, patient_allergies

from ..models.patient import Patient, Allergy, Condition, Medication, LabResult, Visit

class PatientService:
    """Service for handling patient data operations."""
    
    @staticmethod
    def create_patient(db_session: Session, patient_data: Dict) -> Patient:
        """Create a new patient."""
        # Generate MRN if not provided
        if not patient_data.get('mrn'):
            patient_data['mrn'] = PatientService._generate_mrn()
        
        # Create patient object
        patient = Patient(**patient_data)
        
        # Add to session and commit
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        
        return patient
    
    @staticmethod
    def get_patient_by_id(db_session: Session, patient_id: str) -> Optional[Patient]:
        """Get a patient by ID with all related data."""
        try:
            patient_uuid = uuid.UUID(patient_id)
            return db_session.query(Patient).options(
                joinedload(Patient.allergies),
                joinedload(Patient.conditions),
                joinedload(Patient.medications)
            ).filter(Patient.id == patient_uuid).first()
        except ValueError:
            return None
    
    @staticmethod
    def get_patient_by_mrn(db_session: Session, mrn: str) -> Optional[Patient]:
        """Get a patient by Medical Record Number."""
        return db_session.query(Patient).filter(Patient.mrn == mrn).first()
    
    @staticmethod
    def update_patient(db_session: Session, patient_id: str, patient_data: Dict) -> Optional[Patient]:
        """Update an existing patient."""
        try:
            patient_uuid = uuid.UUID(patient_id)
            patient = db_session.query(Patient).filter(Patient.id == patient_uuid).first()
            
            if not patient:
                return None
            
            # Update only the fields that are provided
            for key, value in patient_data.items():
                if hasattr(patient, key):
                    setattr(patient, key, value)
            
            # Update timestamp
            patient.updated_at = datetime.utcnow()
            
            db_session.commit()
            db_session.refresh(patient)
            
            return patient
        except ValueError:
            return None
    
    @staticmethod
    def delete_patient(db_session: Session, patient_id: str) -> bool:
        """Delete a patient (or mark as inactive)."""
        try:
            patient_uuid = uuid.UUID(patient_id)
            # In healthcare systems, actual deletion is usually avoided
            # Instead, mark the patient as inactive
            patient = db_session.query(Patient).filter(Patient.id == patient_uuid).first()
            
            if not patient:
                return False
            
            patient.is_active = False
            patient.updated_at = datetime.utcnow()
            
            db_session.commit()
            return True
        except ValueError:
            return False
    
    @staticmethod
    def search_patients(db_session: Session, search_params: Dict, page: int = 1, page_size: int = 20) -> Tuple[List[Patient], int]:
        """
        Search for patients based on various parameters with pagination.
        Returns a tuple of (patients, total_count).
        """
        # Start with a base query
        query = db_session.query(Patient)
        
        # Apply filters based on search parameters
        if search_params:
            filters = []
            
            # Basic filters
            if 'name' in search_params:
                name_term = f"%{search_params['name']}%"
                filters.append(or_(
                    Patient.first_name.ilike(name_term),
                    Patient.last_name.ilike(name_term),
                    func.concat(Patient.first_name, ' ', Patient.last_name).ilike(name_term)
                ))
            
            if 'mrn' in search_params:
                filters.append(Patient.mrn.ilike(f"%{search_params['mrn']}%"))
            
            if 'dob' in search_params:
                filters.append(Patient.date_of_birth == search_params['dob'])
            
            if 'gender' in search_params:
                filters.append(Patient.gender == search_params['gender'])
            
            if 'email' in search_params:
                filters.append(Patient.email.ilike(f"%{search_params['email']}%"))
            
            if 'phone' in search_params:
                filters.append(Patient.phone_number.ilike(f"%{search_params['phone']}%"))
            
            # Address filters
            if 'city' in search_params:
                filters.append(Patient.city.ilike(f"%{search_params['city']}%"))
            
            if 'state' in search_params:
                filters.append(Patient.state.ilike(f"%{search_params['state']}%"))
            
            if 'postal_code' in search_params:
                filters.append(Patient.postal_code.ilike(f"%{search_params['postal_code']}%"))
            
            # Active status filter
            if 'is_active' in search_params:
                filters.append(Patient.is_active == search_params['is_active'])
            
            # Advanced: JSONB filters for metadata
            if 'metadata' in search_params and isinstance(search_params['metadata'], dict):
                for key, value in search_params['metadata'].items():
                    # Add a filter for each metadata field
                    filters.append(Patient.metadata[key].astext == str(value))
            
            # Date range filters
            if 'created_after' in search_params:
                filters.append(Patient.created_at >= search_params['created_after'])
            
            if 'created_before' in search_params:
                filters.append(Patient.created_at <= search_params['created_before'])
            
            if 'updated_after' in search_params:
                filters.append(Patient.updated_at >= search_params['updated_after'])
            
            if 'updated_before' in search_params:
                filters.append(Patient.updated_at <= search_params['updated_before'])
            
            # Apply all filters to the query
            if filters:
                query = query.filter(and_(*filters))
        
        # Get total count before pagination for metadata
        total_count = query.count()
        
        # Apply sorting
        sort_field = search_params.get('sort_by', 'last_name')
        sort_dir = search_params.get('sort_dir', 'asc')
        
        # Validate sort field exists on Patient model
        if hasattr(Patient, sort_field):
            sort_attr = getattr(Patient, sort_field)
            query = query.order_by(asc(sort_attr) if sort_dir == 'asc' else desc(sort_attr))
        else:
            # Default to last_name, asc if invalid sort field
            query = query.order_by(Patient.last_name)
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        patients = query.all()
        
        return patients, total_count
    
    @staticmethod
    def get_all_patients(db_session: Session, page: int = 1, page_size: int = 20, include_inactive: bool = False) -> Tuple[List[Patient], int]:
        """Get all patients with pagination."""
        query = db_session.query(Patient)
        
        if not include_inactive:
            query = query.filter(Patient.is_active == True)
        
        total_count = query.count()
        
        patients = query.order_by(Patient.last_name).offset((page - 1) * page_size).limit(page_size).all()
        
        return patients, total_count
    
    @staticmethod
    def add_allergy(db_session: Session, patient_id: str, allergy_data: Dict) -> Optional[Allergy]:
        """Add an allergy to a patient."""
        try:
            patient_uuid = uuid.UUID(patient_id)
            patient = db_session.query(Patient).filter(Patient.id == patient_uuid).first()
            
            if not patient:
                return None
            
            allergy = Allergy(**allergy_data)
            db_session.add(allergy)
            
            patient.allergies.append(allergy)
            db_session.commit()
            
            return allergy
        except ValueError:
            return None
    
    @staticmethod
    def add_condition(db_session: Session, patient_id: str, condition_data: Dict) -> Optional[Condition]:
        """Add a medical condition to a patient."""
        try:
            patient_uuid = uuid.UUID(patient_id)
            patient = db_session.query(Patient).filter(Patient.id == patient_uuid).first()
            
            if not patient:
                return None
            
            condition = Condition(**condition_data)
            db_session.add(condition)
            
            patient.conditions.append(condition)
            db_session.commit()
            
            return condition
        except ValueError:
            return None
    
    @staticmethod
    def add_medication(db_session: Session, patient_id: str, medication_data: Dict) -> Optional[Medication]:
        """Add a medication to a patient."""
        try:
            patient_uuid = uuid.UUID(patient_id)
            patient = db_session.query(Patient).filter(Patient.id == patient_uuid).first()
            
            if not patient:
                return None
            
            medication = Medication(**medication_data)
            db_session.add(medication)
            
            patient.medications.append(medication)
            db_session.commit()
            
            return medication
        except ValueError:
            return None
    
    @staticmethod
    def add_lab_result(db_session: Session, patient_id: str, lab_result_data: Dict) -> Optional[LabResult]:
        """Add a lab result to a patient."""
        try:
            patient_uuid = uuid.UUID(patient_id)
            # Ensure the patient exists
            patient = db_session.query(Patient).filter(Patient.id == patient_uuid).first()
            
            if not patient:
                return None
            
            # Add patient_id to the lab result data
            lab_result_data['patient_id'] = patient_uuid
            
            lab_result = LabResult(**lab_result_data)
            db_session.add(lab_result)
            db_session.commit()
            
            return lab_result
        except ValueError:
            return None
    
    @staticmethod
    def add_visit(db_session: Session, patient_id: str, visit_data: Dict) -> Optional[Visit]:
        """Add a visit/encounter to a patient."""
        try:
            patient_uuid = uuid.UUID(patient_id)
            # Ensure the patient exists
            patient = db_session.query(Patient).filter(Patient.id == patient_uuid).first()
            
            if not patient:
                return None
            
            # Add patient_id to the visit data
            visit_data['patient_id'] = patient_uuid
            
            visit = Visit(**visit_data)
            db_session.add(visit)
            db_session.commit()
            
            # Update the patient's last visit date
            patient.last_visit_date = visit.visit_date
            db_session.commit()
            
            return visit
        except ValueError:
            return None
    
    @staticmethod
    def get_patient_lab_results(db_session: Session, patient_id: str, page: int = 1, page_size: int = 20) -> Tuple[List[LabResult], int]:
        """Get lab results for a patient with pagination."""
        try:
            patient_uuid = uuid.UUID(patient_id)
            
            query = db_session.query(LabResult).filter(LabResult.patient_id == patient_uuid)
            total_count = query.count()
            
            lab_results = query.order_by(desc(LabResult.test_date)).offset((page - 1) * page_size).limit(page_size).all()
            
            return lab_results, total_count
        except ValueError:
            return [], 0
    
    @staticmethod
    def get_patient_visits(db_session: Session, patient_id: str, page: int = 1, page_size: int = 20) -> Tuple[List[Visit], int]:
        """Get visits for a patient with pagination."""
        try:
            patient_uuid = uuid.UUID(patient_id)
            
            query = db_session.query(Visit).filter(Visit.patient_id == patient_uuid)
            total_count = query.count()
            
            visits = query.order_by(desc(Visit.visit_date)).offset((page - 1) * page_size).limit(page_size).all()
            
            return visits, total_count
        except ValueError:
            return [], 0
    
    @staticmethod
    def advanced_search(db_session: Session, query_params: Dict, page: int = 1, page_size: int = 20) -> Tuple[List[Patient], int]:
        """
        Advanced search with complex conditions and full-text search capabilities.
        Uses PostgreSQL-specific features for optimized searching.
        """
        # Start with a base query
        query = db_session.query(Patient)
        
        # Full-text search if search_text is provided
        if 'search_text' in query_params and query_params['search_text']:
            search_term = query_params['search_text']
            # Use PostgreSQL's to_tsquery for full-text search
            text_search = func.to_tsvector('english', 
                func.coalesce(Patient.first_name, '') + ' ' + 
                func.coalesce(Patient.last_name, '') + ' ' + 
                func.coalesce(Patient.mrn, '') + ' ' + 
                func.coalesce(Patient.address_line1, '') + ' ' + 
                func.coalesce(Patient.city, '') + ' ' + 
                func.coalesce(Patient.state, '')
            ).op('@@')(func.plainto_tsquery('english', search_term))
            
            query = query.filter(text_search)
        
        # Age range search
        if 'min_age' in query_params and 'max_age' in query_params:
            min_age = int(query_params['min_age'])
            max_age = int(query_params['max_age'])
            
            # Calculate date ranges for the ages
            min_date = datetime.now().date().replace(year=datetime.now().year - max_age - 1)
            max_date = datetime.now().date().replace(year=datetime.now().year - min_age)
            
            query = query.filter(Patient.date_of_birth.between(min_date, max_date))
        
        # Filter by conditions (if the patient has any of the specified conditions)
        if 'conditions' in query_params and query_params['conditions']:
            condition_list = query_params['conditions'].split(',')
            condition_subquery = db_session.query(Patient.id).join(
                patient_conditions, Patient.id == patient_conditions.c.patient_id
            ).join(
                Condition, Condition.id == patient_conditions.c.condition_id
            ).filter(
                Condition.name.in_(condition_list)
            ).subquery()
            
            query = query.filter(Patient.id.in_(condition_subquery))
        
        # Filter by medications
        if 'medications' in query_params and query_params['medications']:
            medication_list = query_params['medications'].split(',')
            medication_subquery = db_session.query(Patient.id).join(
                patient_medications, Patient.id == patient_medications.c.patient_id
            ).join(
                Medication, Medication.id == patient_medications.c.medication_id
            ).filter(
                Medication.name.in_(medication_list)
            ).subquery()
            
            query = query.filter(Patient.id.in_(medication_subquery))
        
        # Filter by allergies
        if 'allergies' in query_params and query_params['allergies']:
            allergy_list = query_params['allergies'].split(',')
            allergy_subquery = db_session.query(Patient.id).join(
                patient_allergies, Patient.id == patient_allergies.c.patient_id
            ).join(
                Allergy, Allergy.id == patient_allergies.c.allergy_id
            ).filter(
                Allergy.name.in_(allergy_list)
            ).subquery()
            
            query = query.filter(Patient.id.in_(allergy_subquery))
        
        # Filter by last visit date range
        if 'last_visit_after' in query_params:
            query = query.filter(Patient.last_visit_date >= query_params['last_visit_after'])
        
        if 'last_visit_before' in query_params:
            query = query.filter(Patient.last_visit_date <= query_params['last_visit_before'])
        
        # Add more complex filters as needed
        
        # Get total count for pagination metadata
        total_count = query.count()
        
        # Apply sorting
        sort_field = query_params.get('sort_by', 'last_name')
        sort_dir = query_params.get('sort_dir', 'asc')
        
        if hasattr(Patient, sort_field):
            sort_attr = getattr(Patient, sort_field)
            query = query.order_by(asc(sort_attr) if sort_dir == 'asc' else desc(sort_attr))
        else:
            query = query.order_by(Patient.last_name)
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        patients = query.all()
        
        return patients, total_count
    
    @staticmethod
    def _generate_mrn() -> str:
        """Generate a unique Medical Record Number."""
        # This is a simplified example - in production, follow your organization's MRN format
        # and ensure uniqueness
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_suffix = str(uuid.uuid4())[:4]
        return f"MRN-{timestamp}-{random_suffix}"
    
    @staticmethod
    def bulk_import_patients(db_session: Session, patients_data: List[Dict]) -> Tuple[int, List[str]]:
        """
        Bulk import patients from a list of patient data dictionaries.
        Returns a tuple of (number of successful imports, list of errors).
        """
        successful_imports = 0
        errors = []
        
        for i, patient_data in enumerate(patients_data):
            try:
                # Generate MRN if not provided
                if not patient_data.get('mrn'):
                    patient_data['mrn'] = PatientService._generate_mrn()
                
                patient = Patient(**patient_data)
                db_session.add(patient)
                successful_imports += 1
            except Exception as e:
                errors.append(f"Error importing patient at index {i}: {str(e)}")
        
        # Commit all successful imports
        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            errors.append(f"Transaction failed: {str(e)}")
            return 0, errors
        
        return successful_imports, errors