import logging
import os
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
client.api_key = api_key

def call_llm_emr(extracted_text: str) -> str:
    """
    Call the LLM to deduce the intended text from the combined extraction,
    with special instructions for clinical reports. The LLM should fix
    grammatical errors, improve clarity, and ensure medical terminology remains accurate.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": "You are an expert medical editor."},
            {"role": "user", "content": f"""
I have extracted the following text from an electronic medical record (EMR) that contains both typed text and handwritten notes. Please improve the grammar, clarity, and overall presentation while preserving the clinical meaning and medical terminology. Provide only the corrected version without any commentary.

Extracted Text:
{extracted_text}

Corrected Version:
"""}
        ]
    )
    return response.choices[0].message.content

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