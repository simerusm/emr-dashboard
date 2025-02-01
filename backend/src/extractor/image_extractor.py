import pytesseract
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_image(image_path: str) -> str:
    """
    Extracts text from an image file using OCR.
    """
    try:
        logger.info(f"Processing image file: {image_path}")
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from image {image_path}: {e}")
        raise