import os
import io
import logging
from dotenv import load_dotenv
from difflib import SequenceMatcher
import PyPDF2
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
from openai import OpenAI
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables and configure the OpenAI client.
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
client.api_key = api_key

def call_llm_combined(extracted_text: str) -> str:
    """
    Call the LLM to clean up and deduce the intended text from combined OCR and native extraction.
    The LLM fixes misrecognized characters, broken words, formatting issues, and outputs only the corrected version.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"""
I have extracted the following text from a document that contains both typed text and handwritten content.
The extraction includes native PDF text (which is generally accurate for typed parts) as well as OCR results from image-rendered pages.
The OCR output, however, may include errors like misrecognized characters, broken words, and formatting issues.
Your task is to deduce the intended meaning of the document and produce a corrected, clean version that accurately reflects the original content.
Do not include any commentary or additional explanation—only provide the corrected text.

Extracted Text:
{extracted_text}

Corrected Version:
"""}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        raise

def deduplicate_overlap(native_text: str, ocr_text: str) -> str:
    """
    Deduplicate overlapping text between native extraction and OCR output.
    If both texts share a significant overlap, the duplicate portion is removed from the OCR output before concatenation.
    """
    if not native_text:
        return ocr_text.strip()
    if not ocr_text:
        return native_text.strip()

    native_text = native_text.strip()
    ocr_text = ocr_text.strip()

    if native_text == ocr_text:
        return native_text

    ratio = SequenceMatcher(None, native_text, ocr_text).ratio()
    if ratio > 0.7:
        return native_text if len(native_text) > len(ocr_text) else ocr_text

    def longest_common_substring(s1, s2):
        m = [[0] * (1 + len(s2)) for _ in range(1 + len(s1))]
        longest, x_longest = 0, 0
        for x in range(1, 1 + len(s1)):
            for y in range(1, 1 + len(s2)):
                if s1[x - 1] == s2[y - 1]:
                    m[x][y] = m[x - 1][y - 1] + 1
                    if m[x][y] > longest:
                        longest = m[x][y]
                        x_longest = x
                else:
                    m[x][y] = 0
        return s1[x_longest - longest: x_longest]

    lcs = longest_common_substring(native_text, ocr_text)
    if len(lcs) > 20:
        if ocr_text.startswith(lcs):
            ocr_text = ocr_text[len(lcs):].strip()
        elif ocr_text.endswith(lcs):
            ocr_text = ocr_text[:-len(lcs)].strip()
    
    combined = native_text
    if ocr_text:
        combined += "\n" + ocr_text
    return combined

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