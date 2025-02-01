import PyPDF2
from dotenv import load_dotenv
import os
from openai import OpenAI
import pytesseract
from PIL import Image

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
client.api_key = api_key

def call_llm(extracted_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""
             I have extracted the following text from a PDF document. Please review it and correct any grammatical errors or awkward phrasing. Here is the text:

             {extracted_text}

             Please provide the corrected version. Your response should ONLY give me the corrected version as a string, nothing else. Dont wrap the response inside a double quote.
             """}
        ]
    )
    return response.choices[0].message.content

def call_llm_ocr(extracted_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""
            I have extracted the following text using OCR from an image of a document. The OCR output contains various errors such as misrecognized characters, broken words, incorrect punctuation, and formatting issues. Your task is to carefully analyze the OCR text, deduce what the original text likely intended to say, and produce a corrected version that accurately conveys the intended meaning and structure. Do not include any commentary—only provide the cleaned-up text.

            OCR Text:
            {extracted_text}

            Corrected Version:
            """}
        ]
    )
    return response.choices[0].message.content

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return ' '.join(text.split()).strip()

def perform_ocr(image_path: str) -> str:
    """
    Perform OCR on a given PIL Image using Tesseract.

    Args:
        image (PIL.Image.Image): The image to perform OCR on.

    Returns:
        str: The text extracted from the image.
    """
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

# extracted_text = extract_text_from_pdf('./data/Random.pdf')
# print(extracted_text)
#res = call_llm(extracted_text)

output = perform_ocr('./data/HandWritten.png')
res = call_llm_ocr(output)
print(res)


