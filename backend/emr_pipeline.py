import os
import io
from dotenv import load_dotenv
import PyPDF2
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
client.api_key = api_key

def call_llm_combined(extracted_text: str) -> str:
    """
    Call the LLM to clean up and deduce the intended text from a combined OCR and native extraction.
    The prompt instructs the LLM to fix misrecognized characters, broken words, formatting errors, 
    and to output only the corrected version.
    """
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

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    For each page in the PDF, this function attempts to extract native text.
    It then renders the page as an image and performs OCR to capture any handwritten or image-based text.
    The outputs are concatenated to form a combined text, which is then cleaned and returned.
    """
    final_text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        doc = fitz.open(pdf_path)
        total_pages = len(reader.pages)
        
        for page_num in range(total_pages):
            # Extract native text using PyPDF2
            native_text = reader.pages[page_num].extract_text() or ""
            
            # Render page as image using PyMuPDF for OCR processing
            page_fitz = doc.load_page(page_num)
            zoom = 2  # Adjust zoom factor for higher resolution if needed
            mat = fitz.Matrix(zoom, zoom)
            pix = page_fitz.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            
            # Perform OCR on the image
            ocr_text = pytesseract.image_to_string(image)
            
            # Combine native and OCR text.
            # Here we simply concatenate them, but you could add more logic to deduplicate overlaps.
            if native_text and ocr_text:
                combined = native_text.strip() + "\n" + ocr_text.strip()
            elif native_text:
                combined = native_text.strip()
            else:
                combined = ocr_text.strip()
                
            final_text += combined + "\n\n"
        doc.close()
    
    # Clean-up whitespace and return
    return ' '.join(final_text.split()).strip()

if __name__ == "__main__":
    pdf_path = './data/combined_document.pdf'
    
    # Extract text from the document
    extracted_text = extract_text_from_pdf(pdf_path)
    print("Extracted Combined Text:")
    print(extracted_text)
    
    # Use the LLM to deduce and clean the intended content
    cleaned_text = call_llm_combined(extracted_text)
    print("\nCleaned Corrected Version:")
    print(cleaned_text)