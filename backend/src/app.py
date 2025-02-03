# src/main.py
import os
import logging
import argparse
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename

# Import your modular functions.
from extractor.pdf_extractor import extract_text_from_pdf
from extractor.image_extractor import extract_text_from_image
from llm.llm_client import call_llm_combined
from config.settings import ALLOWED_EXTENSIONS, TEMP_UPLOAD_FOLDER

# Configure logging.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask app.
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = TEMP_UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Ensure the file was submitted.
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logger.info(f"File saved to {file_path}")

        # Determine extraction method based on file extension.
        ext = filename.rsplit('.', 1)[1].lower()
        try:
            if ext == 'pdf':
                extracted_text = extract_text_from_pdf(file_path)
            else:  # Assume image file for allowed extensions.
                extracted_text = extract_text_from_image(file_path)

            # Call LLM for improved text.
            cleaned_text = call_llm_combined(extracted_text)
            
            os.remove(file_path)
            
            # Return a JSON response. You could also render a template showing a side-by-side comparison.
            return jsonify({
                'original_text': extracted_text,
                'cleaned_text': cleaned_text
            })
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