from flask import Blueprint, request, jsonify, current_app
import json
from datetime import datetime

from ..utils.db import get_db_session, close_db_session
from ..services.patient_service import PatientService
from ..utils.validation import validate_patient_data, validate_lab_result, validate_visit, validate_allergy, validate_condition, validate_medication

# Create blueprint
patient_bp = Blueprint('patient', __name__, url_prefix='/api/v1/patients')

@patient_bp.route('', methods=['POST'])
def create_patient():
    """Create a new patient."""
    data = request.get_json()
    
    # Validate patient data
    is_valid, errors = validate_patient_data(data)
    if not is_valid:
        return jsonify({"errors": errors}), 400
    
    # Handle date fields
    if 'date_of_birth' in data and isinstance(data['date_of_birth'], str):
        try:
            data['date_of_birth'] = datetime.fromisoformat(data['date_of_birth'].replace('Z', '+00:00')).date()
        except ValueError:
            return jsonify({"error": "Invalid date_of_birth format. Use ISO format (YYYY-MM-DD)."}), 400
    
    db_session = get_db_session()
    try:
        # Check if patient with MRN already exists
        if 'mrn' in data and PatientService.get_patient_by_mrn(db_session, data['mrn']):
            return jsonify({"error": f"Patient with MRN {data['mrn']} already exists"}), 409
        
        patient = PatientService.create_patient(db_session, data)
        
        return jsonify({
            "message": "Patient created successfully",
            "patient": patient.to_dict()
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error creating patient: {str(e)}")
        return jsonify({"error": "An error occurred while creating the patient"}), 500
    finally:
        close_db_session()

@patient_bp.route('', methods=['GET'])
def get_patients():
    """Get all patients with pagination and filtering."""
    # Parse query parameters
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', current_app.config.get('DEFAULT_PAGE_SIZE'))), 
                   current_app.config.get('MAX_PAGE_SIZE'))
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    # Handle search parameters
    search_params = {}
    for key in request.args:
        if key not in ['page', 'page_size', 'include_inactive']:
            search_params[key] = request.args.get(key)
    
    db_session = get_db_session()
    try:
        # Use search if parameters are provided, otherwise get all
        if search_params:
            patients, total_count = PatientService.search_patients(db_session, search_params, page, page_size)
        else:
            patients, total_count = PatientService.get_all_patients(db_session, page, page_size, include_inactive)
        
        # Convert patients to dictionaries
        patient_list = [patient.to_dict() for patient in patients]
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        
        return jsonify({
            "patients": patient_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving patients: {str(e)}")
        return jsonify({"error": "An error occurred while retrieving patients"}), 500
    finally:
        close_db_session()

@patient_bp.route('/search', methods=['POST'])
def advanced_search():
    """Advanced search endpoint for complex queries."""
    data = request.get_json() or {}
    
    # Parse pagination parameters
    page = int(data.get('page', 1))
    page_size = min(int(data.get('page_size', current_app.config.get('DEFAULT_PAGE_SIZE'))), 
                   current_app.config.get('MAX_PAGE_SIZE'))
    
    # Extract search parameters
    query_params = {k: v for k, v in data.items() if k not in ['page', 'page_size']}
    
    db_session = get_db_session()
    try:
        patients, total_count = PatientService.advanced_search(db_session, query_params, page, page_size)
        
        # Convert patients to dictionaries
        patient_list = [patient.to_dict() for patient in patients]
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        
        return jsonify({
            "patients": patient_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in advanced search: {str(e)}")
        return jsonify({"error": "An error occurred during search"}), 500
    finally:
        close_db_session()

@patient_bp.route('/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a patient by ID."""
    db_session = get_db_session()
    try:
        patient = PatientService.get_patient_by_id(db_session, patient_id)
        
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        return jsonify({"patient": patient.to_dict()}), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving patient {patient_id}: {str(e)}")
        return jsonify({"error": "An error occurred while retrieving the patient"}), 500
    finally:
        close_db_session()

@patient_bp.route('/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update a patient."""
    data = request.get_json()
    
    # Validate patient data
    is_valid, errors = validate_patient_data(data, is_update=True)
    if not is_valid:
        return jsonify({"errors": errors}), 400
    
    # Handle date fields
    if 'date_of_birth' in data and isinstance(data['date_of_birth'], str):
        try:
            data['date_of_birth'] = datetime.fromisoformat(data['date_of_birth'].replace('Z', '+00:00')).date()
        except ValueError:
            return jsonify({"error": "Invalid date_of_birth format. Use ISO format (YYYY-MM-DD)."}), 400
    
    db_session = get_db_session()
    try:
        patient = PatientService.update_patient(db_session, patient_id, data)
        
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        return jsonify({
            "message": "Patient updated successfully",
            "patient": patient.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error updating patient {patient_id}: {str(e)}")
        return jsonify({"error": "An error occurred while updating the patient"}), 500
    finally:
        close_db_session()

@patient_bp.route('/<patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete (deactivate) a patient."""
    db_session = get_db_session()
    try:
        success = PatientService.delete_patient(db_session, patient_id)
        
        if not success:
            return jsonify({"error": "Patient not found"}), 404
        
        return jsonify({"message": "Patient deactivated successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Error deactivating patient {patient_id}: {str(e)}")
        return jsonify({"error": "An error occurred while deactivating the patient"}), 500
    finally:
        close_db_session()

@patient_bp.route('/<patient_id>/allergies', methods=['POST'])
def add_allergy(patient_id):
    """Add an allergy to a patient."""
    data = request.get_json()
    
    # Validate allergy data
    is_valid, errors = validate_allergy(data)
    if not is_valid:
        return jsonify({"errors": errors}), 400
    
    db_session = get_db_session()
    try:
        allergy = PatientService.add_allergy(db_session, patient_id, data)
        
        if not allergy:
            return jsonify({"error": "Patient not found"}), 404
        
        return jsonify({
            "message": "Allergy added successfully",
            "allergy": allergy.to_dict()
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error adding allergy to patient {patient_id}: {str(e)}")
        return jsonify({"error": "An error occurred while adding the allergy"}), 500
    finally:
        close_db_session()

@patient_bp.route('/<patient_id>/conditions', methods=['POST'])
def add_condition(patient_id):
    """Add a medical condition to a patient."""
    data = request.get_json()
    
    # Validate condition data
    is_valid, errors = validate_condition(data)
    if not is_valid:
        return jsonify({"errors": errors}), 400
    
    # Parse date fields
    for date_field in ['onset_date', 'resolution_date']:
        if date_field in data and isinstance(data[date_field], str):
            try:
                data[date_field] = datetime.fromisoformat(data[date_field].replace('Z', '+00:00')).date()
            except ValueError:
                return jsonify({"error": f"Invalid {date_field} format. Use ISO format (YYYY-MM-DD)."}), 400
    
    db_session = get_db_session()
    try:
        condition = PatientService.add_condition(db_session, patient_id, data)
        
        if not condition:
            return jsonify({"error": "Patient not found"}), 404
        
        return jsonify({
            "message": "Condition added successfully",
            "condition": condition.to_dict()
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error adding condition to patient {patient_id}: {str(e)}")
        return jsonify({"error": "An error occurred while adding the condition"}), 500
    finally:
        close_db_session()

@patient_bp.route('/<patient_id>/medications', methods=['POST'])
def add_medication(patient_id):
    """Add a medication to a patient."""
    data = request.get_json()
    
    # Validate medication data
    is_valid, errors = validate_medication(data)
    if not is_valid:
        return jsonify({"errors": errors}), 400
    
    # Parse date fields
    for date_field in ['start_date', 'end_date']:
        if date_field in data and isinstance(data[date_field], str):
            try:
                data[date_field] = datetime.fromisoformat(data[date_field].replace('Z', '+00:00')).date()
            except ValueError:
                return jsonify({"error": f"Invalid {date_field} format. Use ISO format (YYYY-MM-DD)."}), 400
    
    db_session = get_db_session()
    try:
        medication = PatientService.add_medication(db_session, patient_id, data)
        
        if not medication:
            return jsonify({"error": "Patient not found"}), 404
        
        return jsonify({
            "message": "Medication added successfully",
            "medication": medication.to_dict()
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error adding medication to patient {patient_id}: {str(e)}")
        return jsonify({"error": "An error occurred while adding the medication"}), 500
    finally:
        close_db_session()

@patient_bp.route('/<patient_id>/lab-results', methods=['POST'])
def add_lab_result(patient_id):
    """Add a lab result to a patient."""
    data = request.get_json()
    
    # Validate lab result data
    is_valid, errors = validate_lab_result(data)
    if not is_valid:
        return jsonify({"errors": errors}), 400
    
    # Parse date fields
    if 'test_date' in data and isinstance(data['test_date'], str):
        try:
            data['test_date'] = datetime.fromisoformat(data['test_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid test_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)."}), 400
    
    db_session = get_db_session()
    try:
        lab_result = PatientService.add_lab_result(db_session, patient_id, data)
        
        if not lab_result:
            return jsonify({"error": "Patient not found"}), 404
        
        return jsonify({
            "message": "Lab result added successfully",
            "lab_result": lab_result.to_dict()
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error adding lab result to patient {patient_id}: {str(e)}")
        return jsonify({"error": "An error occurred while adding the lab result"}), 500
    finally:
        close_db_session()

@patient_bp.route('/<patient_id>/lab-results', methods=['GET'])
def get_lab_results(patient_id):
    """Get lab results for a patient."""
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', current_app.config.get('DEFAULT_PAGE_SIZE'))), 
                   current_app.config.get('MAX_PAGE_SIZE'))
    
    db_session = get_db_session()
    try:
        lab_results, total_count = PatientService.get_patient_lab_results(db_session, patient_id, page, page_size)
        
        # Convert to dictionaries
        lab_results_list = [result.to_dict() for result in lab_results]
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        
        return jsonify({
            "lab_results": lab_results_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving lab results for patient {patient_id}: {str(e)}")
        return jsonify({"error": "An error occurred while retrieving lab results"}), 500
    finally:
        close_db_session()

@patient_bp.route('/<patient_id>/visits', methods=['POST'])
def add_visit(patient_id):
    """Add a visit/encounter to a patient."""
    data = request.get_json()
    
    # Validate visit data
    is_valid, errors = validate_visit(data)
    if not is_valid:
        return jsonify({"errors": errors}), 400
    
    # Parse date fields
    if 'visit_date' in data and isinstance(data['visit_date'], str):
        try:
            data['visit_date'] = datetime.fromisoformat(data['visit_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid visit_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)."}), 400
    
    db_session = get_db_session()
    try:
        visit = PatientService.add_visit(db_session, patient_id, data)
        
        if not visit:
            return jsonify({"error": "Patient not found"}), 404
        
        return jsonify({
            "message": "Visit added successfully",
            "visit": visit.to_dict()
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error adding visit to patient {patient_id}: {str(e)}")
        return jsonify({"error": "An error occurred while adding the visit"}), 500
    finally:
        close_db_session()

@patient_bp.route('/<patient_id>/visits', methods=['GET'])
def get_visits(patient_id):
    """Get visits for a patient."""
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', current_app.config.get('DEFAULT_PAGE_SIZE'))), 
                   current_app.config.get('MAX_PAGE_SIZE'))
    
    db_session = get_db_session()
    try:
        visits, total_count = PatientService.get_patient_visits(db_session, patient_id, page, page_size)
        
        # Convert to dictionaries
        visits_list = [visit.to_dict() for visit in visits]
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        
        return jsonify({
            "visits": visits_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving visits for patient {patient_id}: {str(e)}")
        return jsonify({"error": "An error occurred while retrieving visits"}), 500
    finally:
        close_db_session()

@patient_bp.route('/bulk-import', methods=['POST'])
def bulk_import():
    """Bulk import patients."""
    data = request.get_json()
    
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be an array of patient objects"}), 400
    
    # Validate each patient record
    for i, patient_data in enumerate(data):
        is_valid, errors = validate_patient_data(patient_data)
        if not is_valid:
            return jsonify({"error": f"Invalid patient data at index {i}", "errors": errors}), 400
        
        # Parse date of birth
        if 'date_of_birth' in patient_data and isinstance(patient_data['date_of_birth'], str):
            try:
                patient_data['date_of_birth'] = datetime.fromisoformat(patient_data['date_of_birth'].replace('Z', '+00:00')).date()
            except ValueError:
                return jsonify({"error": f"Invalid date_of_birth format at index {i}. Use ISO format (YYYY-MM-DD)."}), 400
    
    db_session = get_db_session()
    try:
        successful_imports, errors = PatientService.bulk_import_patients(db_session, data)
        
        response = {
            "message": f"Successfully imported {successful_imports} patients",
            "successful_imports": successful_imports,
            "total_records": len(data)
        }
        
        if errors:
            response["errors"] = errors
            
        status_code = 200 if successful_imports == len(data) else 207  # Partial success
        
        return jsonify(response), status_code
    except Exception as e:
        current_app.logger.error(f"Error during bulk import: {str(e)}")
        return jsonify({"error": "An error occurred during bulk import"}), 500
    finally:
        close_db_session()