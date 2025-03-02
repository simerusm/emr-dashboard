import io
import logging
import PyPDF2
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
from ..processor.deduplication import deduplicate_overlap

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a PDF document. For each page, it first attempts to use native text extraction.
    Then, it renders the page as an image and performs OCR. The two outputs are deduplicated before concatenation.
    """
    final_text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            doc = fitz.open(pdf_path)
            total_pages = len(reader.pages)
            logger.info(f"Processing PDF with {total_pages} pages.")
            
            for page_num in range(total_pages):
                native_text = reader.pages[page_num].extract_text() or ""
                page_fitz = doc.load_page(page_num)
                zoom = 2
                mat = fitz.Matrix(zoom, zoom)
                pix = page_fitz.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_bytes))
                ocr_text = pytesseract.image_to_string(image)
                combined = deduplicate_overlap(native_text, ocr_text)
                final_text += combined + "\n\n"
            doc.close()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise
    return ' '.join(final_text.split()).strip()