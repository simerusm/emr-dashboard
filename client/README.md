# EMR Analyzer

## Overview

The EMR Analyzer is a production-grade application designed to process Electronic Medical Records (EMR) from PDFs and images. It utilizes Optical Character Recognition (OCR) to extract text and employs a Language Model (LLM) to clean and enhance the extracted content.

## Features

- **Text Extraction**: Extracts text from various file formats, including PDFs and images.
- **OCR Integration**: Uses Tesseract OCR for accurate text recognition from images.
- **LLM Cleanup**: Processes extracted text through a Language Model to suggest improvements and corrections.
- **User-Friendly Interface**: Provides an intuitive interface for users to upload files and view results.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Node.js (for the client-side application)
- Required Python packages (listed in `requirements.txt`)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/emr-analyzer.git
   cd emr-analyzer
   ```

2. **Set up the backend**:
   - Navigate to the backend directory:
     ```bash
     cd backend
     ```
   - Install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Set up the client**:
   - Navigate to the client directory:
     ```bash
     cd client
     ```
   - Install the required Node.js packages:
     ```bash
     npm install
     ```

4. **Configure environment variables**:
   - Create a `.env` file in the backend directory and set the necessary environment variables (e.g., API keys, upload paths).

### Running the Application

1. **Start the backend server**:
   ```bash
   cd backend
   python src/main.py path/to/your/input_file.pdf
   ```

2. **Start the client application**:
   ```bash
   cd client
   npm run dev
   ```

3. **Access the application**:
   Open your browser and navigate to `http://localhost:3000` to access the EMR Analyzer.

## Usage

- Upload your EMR document (PDF or image) to get recommendations and improvements.
- The application will extract the text, process it, and display the cleaned version along with suggested changes.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text recognition.
- [Next.js](https://nextjs.org/) for the frontend framework.
- [Flask](https://flask.palletsprojects.com/) for the backend framework.
