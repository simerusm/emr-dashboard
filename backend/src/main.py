import os
import logging
import argparse
from .extractor.image_extractor import extract_text_from_image
from .extractor.pdf_extractor import extract_text_from_pdf
from .llm.llm_client import call_llm_combined

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]:
        return extract_text_from_image(file_path)
    else:
        error_msg = f"Unsupported file format: {ext}"
        logger.error(error_msg)
        raise ValueError(error_msg)

if __name__ == "__main__":
    # Configure command-line argument parsing for file_path.
    parser = argparse.ArgumentParser(
        description="Production Grade Analyzer for PDFs and Images with OCR and LLM cleanup."
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="Path to the input file (PDF or image)."
    )
    args = parser.parse_args()
    file_path = args.file_path
    
    try:
        # Extract text based on file type.
        extracted_text = extract_text(file_path)
        logger.info("Extracted Combined Text:")
        print(extracted_text)
        
        # Use the LLM to deduce and clean the intended content.
        cleaned_text = call_llm_combined(extracted_text)
        logger.info("Cleaned Corrected Version:")
        print(cleaned_text)
    except Exception as e:
        logger.error(f"An error occurred during processing: {e}")