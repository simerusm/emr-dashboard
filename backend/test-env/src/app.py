import os
import logging
import argparse
import uuid
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS

from .extractor.pdf_extractor import extract_text_from_pdf
from .extractor.image_extractor import extract_text_from_image
from .llm.llm_client import analyze_emr_sections
from config.settings import ALLOWED_EXTENSIONS, TEMP_UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['UPLOAD_FOLDER'] = TEMP_UPLOAD_FOLDER

def allowed_file(filename):
    file_ext = os.path.splitext(filename)[1].lower()
    return file_ext in ALLOWED_EXTENSIONS

def extract_text(file_path: str, ext: str) -> str:
    """
    Determines file type based on extension and routes extraction to the appropriate function.
    Supported file types:
      - PDF: Uses combined native text extraction and OCR.
      - Image files (.png, .jpg, .jpeg, etc.): Uses OCR.
    """
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in ALLOWED_EXTENSIONS:
        return extract_text_from_image(file_path)
    else:
        error_msg = f"Unsupported file format: {ext}"
        logger.error(error_msg)
        raise ValueError(error_msg)

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyzes uploaded EMR documents (PDF or images) and returns structured analysis.

    Request:
    - Method: POST
    - Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
    - Body: {
        file: File (PDF or image)
    }

    Response:
    - Success (200):
        {
            "fileId": string,
            "data": [
                {
                    "title": "...",
                    "content": [
                        {
                            "original": "...",
                            "suggested": "...",
                            "reason": "..."
                        },
                        "..."
                    ]
                },
                {
                    "title": "...",
                    "content": [
                        "..."
                    ]
                },
                ...
            ]
        }
    - Error (400/500):
        {
            "error": string (error message)
        }
    """

    # Ensuring ImmutableMultiDict([...]) request contains elements
    if len(request.files) == 0:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        fileId = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1].lower()

        filename = secure_filename(fileId + ext)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logger.info(f"File saved to {file_path}")

        try:
            extracted_text = extract_text(file_path, ext)
            analyzed_text = analyze_emr_sections(extracted_text)

            response = {
                'fileId': fileId,
                'data': analyzed_text
            }
            return jsonify(response), 200
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Unsupported file format'}), 400

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the EMR Analyzer Flask App")
    parser.add_argument('--host', default='127.0.0.1', help='Host address')
    parser.add_argument('--port', default=5003, type=int, help='Port number')
    args = parser.parse_args()
    
    app.run(host=args.host, port=args.port, debug=True)