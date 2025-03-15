from typing import Dict, List, Tuple, Any, Union
import re
from datetime import datetime, date

def validate_patient_data(data: Dict, is_update: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate patient data.
    Returns a tuple of (is_valid, errors).
    """
    errors = []
    
    # For updates, we don't need to validate all fields
    if not is_update:
        # Required fields
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'gender']
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                errors.append(f"{field} is required")
    
    # Validate first_name if provided
    if 'first_name' in data and (not isinstance(data['first_name'], str) or len(data['first_name']) > 100):
        errors.append("first_name must be a string with maximum length of 100 characters")
    
    # Validate last_name if provided
    if 'last_name' in data and (not isinstance(data['last_name'], str) or len(data['last_name']) > 100):
        errors.append("last_name must be a string with maximum length of 100 characters")
    
    # Validate date_of_birth if provided
    if 'date_of_birth' in data:
        if isinstance(data['date_of_birth'], str):
            try:
                # Attempt to parse the date
                parsed_date = datetime.fromisoformat(data['date_of_birth'].replace('Z', '+00:00')).date()
                
                # Check if date is in the future
                if parsed_date > datetime.now().date():
                    errors.append("date_of_birth cannot be in the future")
                    
                # Check if date is unreasonably old (older than ~150 years)
                min_date = datetime.now().date().replace(year=datetime.now().year - 150)
                if parsed_date < min_date:
                    errors.append("date_of_birth is unreasonably old")
            except ValueError:
                errors.append("date_of_birth must be in ISO format (YYYY-MM-DD)")
        elif isinstance(data['date_of_birth'], date):
            # If it's already a date object, just check the range
            if data['date_of_birth'] > datetime.now().date():
                errors.append("date_of_birth cannot be in the future")
                
            min_date = datetime.now().date().replace(year=datetime.now().year - 150)
            if data['date_of_birth'] < min_date:
                errors.append("date_of_birth is unreasonably old")
        else:
            errors.append("date_of_birth must be a string in ISO format or a date object")
    
    # Validate gender if provided
    if 'gender' in data:
        valid_genders = ['MALE', 'FEMALE', 'OTHER', 'UNKNOWN']
        if data['gender'] not in valid_genders:
            errors.append(f"gender must be one of: {', '.join(valid_genders)}")
    
    # Validate mrn if provided
    if 'mrn' in data and data['mrn']:
        if not isinstance(data['mrn'], str) or len(data['mrn']) > 20:
            errors.append("mrn must be a string with maximum length of 20 characters")
    
    # Validate blood_type if provided
    if 'blood_type' in data and data['blood_type']:
        valid_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown']
        if data['blood_type'] not in valid_blood_types:
            errors.append(f"blood_type must be one of: {', '.join(valid_blood_types)}")
    
    # Validate email if provided
    if 'email' in data and data['email']:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        if not re.match(email_pattern, data['email']):
            errors.append("email is not in a valid format")
    
    # Validate phone_number if provided
    if 'phone_number' in data and data['phone_number']:
        # Simple validation for phone number (can be enhanced based on requirements)
        phone_pattern = r'^\+?[0-9]{8,15}'
        if not re.match(phone_pattern, data['phone_number'].replace(' ', '').replace('-', '')):
            errors.append("phone_number is not in a valid format")
    
    # Validate height_cm if provided
    if 'height_cm' in data and data['height_cm'] is not None:
        try:
            height = float(data['height_cm'])
            if height <= 0 or height > 300:  # Reasonable range for human height in cm
                errors.append("height_cm must be a positive number less than 300")
        except (ValueError, TypeError):
            errors.append("height_cm must be a number")
    
    # Validate weight_kg if provided
    if 'weight_kg' in data and data['weight_kg'] is not None:
        try:
            weight = float(data['weight_kg'])
            if weight <= 0 or weight > 700:  # Reasonable range for human weight in kg
                errors.append("weight_kg must be a positive number less than 700")
        except (ValueError, TypeError):
            errors.append("weight_kg must be a number")
    
    # Validate metadata if provided
    if 'metadata' in data and data['metadata'] is not None:
        if not isinstance(data['metadata'], dict):
            errors.append("metadata must be a JSON object")
    
    # Return validation result
    return len(errors) == 0, errors

def validate_lab_result(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate lab result data.
    Returns a tuple of (is_valid, errors).
    """
    errors = []
    
    # Required fields
    required_fields = ['test_name', 'test_date', 'result_value']
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            errors.append(f"{field} is required")
    
    # Validate test_name if provided
    if 'test_name' in data and (not isinstance(data['test_name'], str) or len(data['test_name']) > 200):
        errors.append("test_name must be a string with maximum length of 200 characters")
    
    # Validate test_date if provided
    if 'test_date' in data:
        if isinstance(data['test_date'], str):
            try:
                # Attempt to parse the datetime
                parsed_date = datetime.fromisoformat(data['test_date'].replace('Z', '+00:00'))
                
                # Check if date is in the future
                if parsed_date > datetime.now():
                    errors.append("test_date cannot be in the future")
            except ValueError:
                errors.append("test_date must be in ISO format (YYYY-MM-DDTHH:MM:SS)")
        elif isinstance(data['test_date'], datetime):
            # If it's already a datetime object, just check if it's in the future
            if data['test_date'] > datetime.now():
                errors.append("test_date cannot be in the future")
        else:
            errors.append("test_date must be a string in ISO format or a datetime object")
    
    # Validate result_value if provided
    if 'result_value' in data and (not isinstance(data['result_value'], str) or len(data['result_value']) > 100):
        errors.append("result_value must be a string with maximum length of 100 characters")
    
    # Validate unit if provided
    if 'unit' in data and data['unit'] and (not isinstance(data['unit'], str) or len(data['unit']) > 50):
        errors.append("unit must be a string with maximum length of 50 characters")
    
    # Validate reference_range if provided
    if 'reference_range' in data and data['reference_range'] and (not isinstance(data['reference_range'], str) or len(data['reference_range']) > 100):
        errors.append("reference_range must be a string with maximum length of 100 characters")
    
    # Validate abnormal_flag if provided
    if 'abnormal_flag' in data and not isinstance(data['abnormal_flag'], bool):
        errors.append("abnormal_flag must be a boolean")
    
    # Validate status if provided
    if 'status' in data and data['status'] and (not isinstance(data['status'], str) or len(data['status']) > 50):
        errors.append("status must be a string with maximum length of 50 characters")
    
    # Validate performing_lab if provided
    if 'performing_lab' in data and data['performing_lab'] and (not isinstance(data['performing_lab'], str) or len(data['performing_lab']) > 200):
        errors.append("performing_lab must be a string with maximum length of 200 characters")
    
    # Validate ordering_provider if provided
    if 'ordering_provider' in data and data['ordering_provider'] and (not isinstance(data['ordering_provider'], str) or len(data['ordering_provider']) > 200):
        errors.append("ordering_provider must be a string with maximum length of 200 characters")
    
    # Validate loinc_code if provided
    if 'loinc_code' in data and data['loinc_code'] and (not isinstance(data['loinc_code'], str) or len(data['loinc_code']) > 20):
        errors.append("loinc_code must be a string with maximum length of 20 characters")
    
    # Validate metadata if provided
    if 'metadata' in data and data['metadata'] is not None:
        if not isinstance(data['metadata'], dict):
            errors.append("metadata must be a JSON object")
    
    # Return validation result
    return len(errors) == 0, errors

def validate_visit(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate visit/encounter data.
    Returns a tuple of (is_valid, errors).
    """
    errors = []
    
    # Required fields
    required_fields = ['visit_date', 'provider_name', 'visit_type']
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            errors.append(f"{field} is required")
    
    # Validate visit_date if provided
    if 'visit_date' in data:
        if isinstance(data['visit_date'], str):
            try:
                # Attempt to parse the datetime
                parsed_date = datetime.fromisoformat(data['visit_date'].replace('Z', '+00:00'))
                
                # Check if date is too far in the future (e.g., more than 1 year)
                max_future_date = datetime.now().replace(year=datetime.now().year + 1)
                if parsed_date > max_future_date:
                    errors.append("visit_date is too far in the future (more than 1 year ahead)")
            except ValueError:
                errors.append("visit_date must be in ISO format (YYYY-MM-DDTHH:MM:SS)")
        elif isinstance(data['visit_date'], datetime):
            # If it's already a datetime object, just check if it's too far in the future
            max_future_date = datetime.now().replace(year=datetime.now().year + 1)
            if data['visit_date'] > max_future_date:
                errors.append("visit_date is too far in the future (more than 1 year ahead)")
        else:
            errors.append("visit_date must be a string in ISO format or a datetime object")
    
    # Validate provider_name if provided
    if 'provider_name' in data and (not isinstance(data['provider_name'], str) or len(data['provider_name']) > 200):
        errors.append("provider_name must be a string with maximum length of 200 characters")
    
    # Validate visit_type if provided
    if 'visit_type' in data and (not isinstance(data['visit_type'], str) or len(data['visit_type']) > 100):
        errors.append("visit_type must be a string with maximum length of 100 characters")
    
    # Validate chief_complaint if provided
    if 'chief_complaint' in data and data['chief_complaint'] and not isinstance(data['chief_complaint'], str):
        errors.append("chief_complaint must be a string")
    
    # Validate diagnosis if provided
    if 'diagnosis' in data and data['diagnosis'] and not isinstance(data['diagnosis'], str):
        errors.append("diagnosis must be a string")
    
    # Validate treatment_plan if provided
    if 'treatment_plan' in data and data['treatment_plan'] and not isinstance(data['treatment_plan'], str):
        errors.append("treatment_plan must be a string")
    
    # Validate follow_up_instructions if provided
    if 'follow_up_instructions' in data and data['follow_up_instructions'] and not isinstance(data['follow_up_instructions'], str):
        errors.append("follow_up_instructions must be a string")
    
    # Validate vital signs if provided
    vital_sign_fields = ['temperature', 'heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic', 'respiratory_rate', 'oxygen_saturation']
    for field in vital_sign_fields:
        if field in data and data[field] is not None:
            try:
                value = float(data[field])
                
                # Validate ranges for each vital sign
                if field == 'temperature' and (value < 30 or value > 45):  # Celsius
                    errors.append("temperature must be between 30 and 45 degrees Celsius")
                elif field == 'heart_rate' and (value < 20 or value > 300):
                    errors.append("heart_rate must be between 20 and 300 beats per minute")
                elif field == 'blood_pressure_systolic' and (value < 50 or value > 250):
                    errors.append("blood_pressure_systolic must be between 50 and 250 mmHg")
                elif field == 'blood_pressure_diastolic' and (value < 20 or value > 150):
                    errors.append("blood_pressure_diastolic must be between 20 and 150 mmHg")
                elif field == 'respiratory_rate' and (value < 4 or value > 60):
                    errors.append("respiratory_rate must be between 4 and 60 breaths per minute")
                elif field == 'oxygen_saturation' and (value < 50 or value > 100):
                    errors.append("oxygen_saturation must be between 50 and 100 percent")
            except (ValueError, TypeError):
                errors.append(f"{field} must be a number")
    
    # Validate metadata if provided
    if 'metadata' in data and data['metadata'] is not None:
        if not isinstance(data['metadata'], dict):
            errors.append("metadata must be a JSON object")
    
    # Return validation result
    return len(errors) == 0, errors

def validate_allergy(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate allergy data.
    Returns a tuple of (is_valid, errors).
    """
    errors = []
    
    # Required fields
    required_fields = ['name']
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            errors.append(f"{field} is required")
    
    # Validate name if provided
    if 'name' in data and (not isinstance(data['name'], str) or len(data['name']) > 200):
        errors.append("name must be a string with maximum length of 200 characters")
    
    # Validate description if provided
    if 'description' in data and data['description'] and not isinstance(data['description'], str):
        errors.append("description must be a string")
    
    # Validate severity if provided
    if 'severity' in data and data['severity']:
        if not isinstance(data['severity'], str) or len(data['severity']) > 50:
            errors.append("severity must be a string with maximum length of 50 characters")
        
        valid_severities = ['Mild', 'Moderate', 'Severe']
        if data['severity'] not in valid_severities:
            errors.append(f"severity must be one of: {', '.join(valid_severities)}")
    
    # Validate reaction if provided
    if 'reaction' in data and data['reaction'] and not isinstance(data['reaction'], str):
        errors.append("reaction must be a string")
    
    # Return validation result
    return len(errors) == 0, errors

def validate_condition(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate medical condition data.
    Returns a tuple of (is_valid, errors).
    """
    errors = []
    
    # Required fields
    required_fields = ['name']
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            errors.append(f"{field} is required")
    
    # Validate name if provided
    if 'name' in data and (not isinstance(data['name'], str) or len(data['name']) > 200):
        errors.append("name must be a string with maximum length of 200 characters")
    
    # Validate description if provided
    if 'description' in data and data['description'] and not isinstance(data['description'], str):
        errors.append("description must be a string")
    
    # Validate status if provided
    if 'status' in data and data['status']:
        if not isinstance(data['status'], str) or len(data['status']) > 50:
            errors.append("status must be a string with maximum length of 50 characters")
        
        valid_statuses = ['Active', 'Resolved', 'Inactive', 'Recurrent', 'Chronic']
        if data['status'] not in valid_statuses:
            errors.append(f"status must be one of: {', '.join(valid_statuses)}")
    
    # Validate dates if provided
    date_fields = ['onset_date', 'resolution_date']
    for field in date_fields:
        if field in data and data[field]:
            if isinstance(data[field], str):
                try:
                    # Attempt to parse the date
                    parsed_date = datetime.fromisoformat(data[field].replace('Z', '+00:00')).date()
                    
                    # Check if date is too far in the future (e.g., more than 1 year)
                    max_future_date = datetime.now().date().replace(year=datetime.now().year + 1)
                    if parsed_date > max_future_date:
                        errors.append(f"{field} is too far in the future (more than 1 year ahead)")
                except ValueError:
                    errors.append(f"{field} must be in ISO format (YYYY-MM-DD)")
            elif isinstance(data[field], date):
                # If it's already a date object, just check if it's too far in the future
                max_future_date = datetime.now().date().replace(year=datetime.now().year + 1)
                if data[field] > max_future_date:
                    errors.append(f"{field} is too far in the future (more than 1 year ahead)")
            else:
                errors.append(f"{field} must be a string in ISO format or a date object")
    
    # Validate ICD code if provided
    if 'icd_code' in data and data['icd_code']:
        if not isinstance(data['icd_code'], str) or len(data['icd_code']) > 20:
            errors.append("icd_code must be a string with maximum length of 20 characters")
        
        # Simple pattern validation for ICD-10 codes
        icd10_pattern = r'^[A-Z][0-9][0-9AB](\.[0-9]{1,3})?'
        if not re.match(icd10_pattern, data['icd_code']):
            errors.append("icd_code should follow the ICD-10 format (e.g., A01.1)")
    
    # Return validation result
    return len(errors) == 0, errors

def validate_medication(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate medication data.
    Returns a tuple of (is_valid, errors).
    """
    errors = []
    
    # Required fields
    required_fields = ['name']
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            errors.append(f"{field} is required")
    
    # Validate name if provided
    if 'name' in data and (not isinstance(data['name'], str) or len(data['name']) > 200):
        errors.append("name must be a string with maximum length of 200 characters")
    
    # Validate dosage if provided
    if 'dosage' in data and data['dosage'] and (not isinstance(data['dosage'], str) or len(data['dosage']) > 100):
        errors.append("dosage must be a string with maximum length of 100 characters")
    
    # Validate frequency if provided
    if 'frequency' in data and data['frequency'] and (not isinstance(data['frequency'], str) or len(data['frequency']) > 100):
        errors.append("frequency must be a string with maximum length of 100 characters")
    
    # Validate instructions if provided
    if 'instructions' in data and data['instructions'] and not isinstance(data['instructions'], str):
        errors.append("instructions must be a string")
    
    # Validate dates if provided
    date_fields = ['start_date', 'end_date']
    for field in date_fields:
        if field in data and data[field]:
            if isinstance(data[field], str):
                try:
                    # Attempt to parse the date
                    parsed_date = datetime.fromisoformat(data[field].replace('Z', '+00:00')).date()
                    
                    # If it's end_date, make sure it's not before start_date
                    if field == 'end_date' and 'start_date' in data and data['start_date']:
                        if isinstance(data['start_date'], str):
                            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')).date()
                        elif isinstance(data['start_date'], date):
                            start_date = data['start_date']
                        else:
                            # Skip this check if start_date is invalid format
                            continue
                        
                        if parsed_date < start_date:
                            errors.append("end_date cannot be before start_date")
                except ValueError:
                    errors.append(f"{field} must be in ISO format (YYYY-MM-DD)")
            elif isinstance(data[field], date):
                # If it's already a date object
                if field == 'end_date' and 'start_date' in data and isinstance(data['start_date'], date):
                    if data[field] < data['start_date']:
                        errors.append("end_date cannot be before start_date")
            else:
                errors.append(f"{field} must be a string in ISO format or a date object")
    
    # Validate prescribing_doctor if provided
    if 'prescribing_doctor' in data and data['prescribing_doctor'] and (not isinstance(data['prescribing_doctor'], str) or len(data['prescribing_doctor']) > 200):
        errors.append("prescribing_doctor must be a string with maximum length of 200 characters")
    
    # Validate NDC code if provided
    if 'ndc_code' in data and data['ndc_code']:
        if not isinstance(data['ndc_code'], str) or len(data['ndc_code']) > 20:
            errors.append("ndc_code must be a string with maximum length of 20 characters")
        
        # Simple pattern validation for NDC codes
        ndc_pattern = r'^[0-9]{5}-[0-9]{4}-[0-9]{2}$|^[0-9]{5}-[0-9]{3}-[0-9]{2}$|^[0-9]{11}'
        if not re.match(ndc_pattern, data['ndc_code'].replace('-', '')):
            errors.append("ndc_code should follow a valid NDC format")
    
    # Validate form if provided
    if 'form' in data and data['form']:
        if not isinstance(data['form'], str) or len(data['form']) > 50:
            errors.append("form must be a string with maximum length of 50 characters")
        
        valid_forms = ['Tablet', 'Capsule', 'Liquid', 'Injection', 'Cream', 'Ointment', 'Gel', 'Patch', 'Inhalation', 'Other']
        if data['form'] not in valid_forms:
            errors.append(f"form must be one of: {', '.join(valid_forms)}")
    
    # Return validation result
    return len(errors) == 0, errors