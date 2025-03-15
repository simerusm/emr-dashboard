# Patient Data Service

A comprehensive microservice for managing patient medical records, part of the EMR Copilot system. This service provides a REST API for storing and retrieving patient information, medical history, lab results, visits, and more.

## Features

- **Patient Management**: Create, retrieve, update, and search for patient records
- **Medical Data Tracking**: Store allergies, conditions, medications, lab results, and visits
- **Advanced Search**: Search patients by various criteria with pagination
- **Data Validation**: Comprehensive validation of all input data
- **PostgreSQL Database**: Persistent storage with proper relations between entities
- **Dockerized**: Easy deployment using Docker and Docker Compose

## API Endpoints

### Health Check

```bash
# Check if the service is running
curl -X GET http://localhost:5002/health
```

### Patient Management

```bash
# Create a new patient
curl -X POST http://localhost:5002/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1980-01-15",
    "gender": "MALE",
    "phone_number": "555-123-4567",
    "email": "john.doe@example.com",
    "address_line1": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345"
  }'

# Retrieve all patients (with pagination)
curl -X GET http://localhost:5002/api/v1/patients

# Get a specific patient
curl -X GET http://localhost:5002/api/v1/patients/{patient_id}

# Update a patient
curl -X PUT http://localhost:5002/api/v1/patients/{patient_id} \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "555-987-6543",
    "email": "john.updated@example.com"
  }'
```

### Medical Data

```bash
# Add an allergy
curl -X POST http://localhost:5002/api/v1/patients/{patient_id}/allergies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Penicillin",
    "severity": "Severe",
    "reaction": "Rash and difficulty breathing"
  }'

# Add a medical condition
curl -X POST http://localhost:5002/api/v1/patients/{patient_id}/conditions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hypertension",
    "status": "Active",
    "onset_date": "2019-05-10",
    "icd_code": "I10"
  }'

# Add a medication
curl -X POST http://localhost:5002/api/v1/patients/{patient_id}/medications \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lisinopril",
    "dosage": "10mg",
    "frequency": "Once daily",
    "start_date": "2019-06-01"
  }'

# Add a lab result
curl -X POST http://localhost:5002/api/v1/patients/{patient_id}/lab-results \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "Comprehensive Metabolic Panel",
    "test_date": "2023-03-15T09:30:00",
    "result_value": "Normal",
    "unit": "mg/dL",
    "performing_lab": "Quest Diagnostics"
  }'

# Add a visit
curl -X POST http://localhost:5002/api/v1/patients/{patient_id}/visits \
  -H "Content-Type: application/json" \
  -d '{
    "visit_date": "2023-03-15T10:00:00",
    "provider_name": "Dr. Smith",
    "visit_type": "Office Visit",
    "chief_complaint": "Annual checkup",
    "temperature": 37.0,
    "heart_rate": 72,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80
  }'
```

### Search Functionality

```bash
# Basic search
curl -X POST http://localhost:5002/api/v1/patients/search \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Doe",
    "sort_by": "last_name",
    "sort_dir": "asc"
  }'

# Advanced search
curl -X POST http://localhost:5002/api/v1/patients/search \
  -H "Content-Type: application/json" \
  -d '{
    "search_text": "hypertension",
    "min_age": 40,
    "max_age": 60,
    "conditions": "Hypertension",
    "medications": "Lisinopril"
  }'
```

## Deployment

### Prerequisites

- Docker and Docker Compose installed
- PostgreSQL (automatically deployed via Docker Compose)
- Redis (automatically deployed via Docker Compose)

### Setup and Run

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd patient-service
   ```

2. Start the services using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. The service will be available at:
   ```
   http://localhost:5002
   ```

4. To stop the services:
   ```bash
   docker-compose down
   ```

## Database Validation

You can connect directly to the PostgreSQL database to verify data integrity:

```bash
# Connect to PostgreSQL in the Docker container
docker exec -it patient-service-postgres-1 psql -U postgres -d patient_data_db

# Once connected, run SQL queries
SELECT COUNT(*) FROM patients;
SELECT * FROM patients LIMIT 5;

# Check relationships
SELECT p.first_name, p.last_name, l.test_name, l.result_value
FROM patients p
JOIN lab_results l ON p.id = l.patient_id
LIMIT 10;
```

## Error Handling

The service provides detailed error responses for various scenarios:

- Missing required fields
- Invalid date formats
- Invalid patient IDs
- Data validation errors

Example error response:
```json
{
  "error": "Bad Request",
  "message": "Invalid date_of_birth format. Use ISO format (YYYY-MM-DD).",
  "request_id": "e1d74ecf-d898-4ce0-a247-7731a75df8f9"
}
```

## Performance Testing

You can test the service performance using Apache Bench:

```bash
# Install Apache Bench if needed
apt-get install apache2-utils

# Test 1000 requests with 10 concurrent connections to the health endpoint
ab -n 1000 -c 10 http://localhost:5002/health

# Test POST with a JSON payload (save the JSON to a file first)
echo '{"name":"Test"}' > test_search.json
ab -n 100 -c 5 -p test_search.json -T 'application/json' http://localhost:5002/api/v1/patients/search
```

## Integration with Auth Service

If you have integrated with the auth service:

```bash
# First get a token from auth-service
TOKEN=$(curl -s -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"AdminPassword123!"}' \
  | jq -r '.access_token')

# Then use the token with patient-service
curl -X GET http://localhost:5002/api/v1/patients \
  -H "Authorization: Bearer $TOKEN"
```

## Data Persistence

All data is persisted in PostgreSQL volumes, ensuring it remains intact across Docker container restarts. Data is only removed if volumes are explicitly deleted.