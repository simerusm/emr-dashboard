# Auth Service Microservice Setup

## Prerequisites
- Ensure you have Python 3.6 or higher installed.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>/auth-service
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Microservice**:
   ```bash
   python -m src.app
   ```

5. **Run the Test Cases**:
   ```bash
   python -m unittest discover -s tests -p "*.py"
   ```

## Notes
- Make sure to set up your environment variables as needed before running the service.
