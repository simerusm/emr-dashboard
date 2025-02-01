from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import os

# ----------- Creating an image that simulates handwritten text -----------

def create_handwritten_image(text: str, output_path: str, width: int = 600, height: int = 200):
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Attempt to load a handwriting-style font. Adjust the font path as needed.
    try:
        font = ImageFont.truetype("ComicSansMS.ttf", size=24)
    except IOError:
        print("Handwriting font not found. Using default font.")
        font = ImageFont.load_default()
    
    draw.text((10, 10), text, fill="black", font=font)
    
    image.save(output_path)
    print(f"Handwritten image saved to {output_path}")

handwritten_text = (
    "This is handwritten text.\n"
    "It simulates a note written by hand.\n"
    "Please review and interpret accordingly."
)
handwritten_image_path = "./data/handwritten.png"
create_handwritten_image(handwritten_text, handwritten_image_path)


# ----------- Creating a PDF that includes both the handwritten image and typed text -----------

def create_combined_pdf(handwritten_image: str, typed_text: str, output_pdf: str):
    pdf = FPDF()
    pdf.add_page()
    
    # Add the handwritten image at the top of the first page.
    # Adjust x, y, and width (w) as needed.
    pdf.image(handwritten_image, x=10, y=10, w=pdf.w - 20)
    
    # Move the cursor below the image.
    # This value might need to be adjusted based on your image height.
    pdf.ln(45)
    
    pdf.set_font("Arial", size=12)
    
    # Write the typed text using multi_cell so text wraps correctly.
    pdf.multi_cell(0, 10, typed_text)
    
    # Save the PDF to disk.
    pdf.output(output_pdf)
    print(f"PDF created: {output_pdf}")

# Example typed text
typed_text = (
    "This is actual typed text.\n"
    "It appears clear and formatted normally.\n\n"
    "You can include detailed explanations, structured information, and other content here."
)

output_pdf_filename = "./data/combined_document.pdf"
create_combined_pdf(handwritten_image_path, typed_text, output_pdf_filename)