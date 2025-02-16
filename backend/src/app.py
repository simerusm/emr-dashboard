# src/main.py
import os
import logging
import argparse
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename

from .extractor.pdf_extractor import extract_text_from_pdf
from .extractor.image_extractor import extract_text_from_image
from .llm.llm_client import analyze_emr_sections
from config.settings import ALLOWED_EXTENSIONS, TEMP_UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = TEMP_UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(file_path: str) -> str:
    """
    Determines file type based on extension and routes extraction to the appropriate function.
    Supported file types:
      - PDF: Uses combined native text extraction and OCR.
      - Image files (.png, .jpg, .jpeg, etc.): Uses OCR.
    """
    ext = os.path.splitext(file_path)[1].lower()
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
    # Ensuring ImmutableMultiDict([...]) request contains elements
    if len(request.files) == 0:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logger.info(f"File saved to {file_path}")

        try:
            extracted_text = extract_text(file_path)
            analyzed_text = analyze_emr_sections(extracted_text)
            return analyzed_text
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