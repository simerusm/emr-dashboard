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

def analyze_emr_sections(extracted_text: str) -> str:
    """
    Analyze the given EMR text and separate it into sections by title. For each section, 
    the LLM must extract the title and content, identify areas for improvement, and generate suggestions.
    
    Output format:
    
    [
      {
        "title": "Section Title",
        "content": [
          "Plain text content",
          {
            "original": "Original snippet",
            "suggested": "Improved snippet",
            "reason": "Explanation of the improvement"
          },
          "More text content"
        ]
      },
      ... (other sections)
    ]
    """
    prompt = f"""
            You are a precise medical document analyzer. Your task is to parse the following electronic medical record (EMR) text, separate it into its respective sections, and generate improvements within each section. For each section, identify the section title (e.g., "Patient Information", "Chief Complaint", "Medical History", "Assessment and Plan", BUT NOT LIMITED TO THESE ONLY, USE YOUR OWN JUDGEMENT TO ASSIGN ACCURATE TITLES) and extract its content.

            Within each section's content, if there are parts that require improvement, create an object with three keys:
            - "original": the original text snippet,
            - "suggested": the improved version,
            - "reason": a brief explanation of why the change is recommended.

            If a portion of the text does not need improvement, output it as a plain string in the array.

            Output a JSON array of objects, where each object represents a section with the following keys:
            - "title": the section title,
            - "content": an array that may include both strings and objects (as described above).

            The output must be a JSON array of objects in the following format exactly:
    
            [
                {{
                    "title": "Section Title",
                    "content": [
                    "Plain text content",
                    {{
                        "original": "Original snippet",
                        "suggested": "Improved snippet",
                        "reason": "Explanation of the improvement"
                    }},
                    "More text content"
                    ]
                }},
                ... (other sections)
            ]
            
            The LLM must output only valid JSON (parseable) with no additional commentary.

            Here is the extracted text:
            {extracted_text}

            Output:
            """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "developer", "content": "You are a precise medical document analyzer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling LLM for section analysis: {e}")
        raise