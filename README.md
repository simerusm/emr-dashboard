# EMR Analyzer

## Overview

The EMR Analyzer is a comprehensive application designed to process Electronic Medical Records (EMR) from various formats, including PDFs and images. The application leverages Optical Character Recognition (OCR) to extract text and utilizes a Language Model (LLM) to clean and enhance the extracted content. This project consists of a frontend built with Next.js and a backend powered by Flask.

## Features

- **Text Extraction**: Extracts text from PDFs and images using OCR.
- **LLM Processing**: Processes extracted text to suggest improvements and corrections.
- **User-Friendly Interface**: Intuitive interface for users to upload files and view results.
- **Responsive Design**: Works seamlessly on various devices and screen sizes.

## Architecture

The project is divided into two main parts:

### Frontend

- **Framework**: Built with [Next.js](https://nextjs.org/), a React framework for server-rendered applications.
- **Components**: Modular components for file upload, analysis display, and user interaction.
- **Styling**: Utilizes Tailwind CSS for responsive and modern UI design.
- **Routing**: Client-side routing for smooth navigation between pages.

### Backend

- **Framework**: Developed using [Flask](https://flask.palletsprojects.com/), a lightweight WSGI web application framework.
- **OCR Integration**: Uses [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text extraction from images.
- **LLM Integration**: Processes extracted text through a Language Model for suggestions and corrections.
- **API Endpoints**: RESTful API endpoints for file uploads and text processing.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Node.js (for the frontend)
- Required Python packages (listed in `requirements.txt`)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/simerusm/agentic-analyzer/
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

3. **Set up the frontend**:
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
   python src/main.py
   ```

2. **Start the frontend application**:
   ```bash
   cd client
   npm run dev
   ```

3. **Access the application**:
   Open your browser and navigate to `http://localhost:3000` to access the EMR Analyzer.

## Usage

- Upload your EMR document (PDF or image) to get recommendations and improvements.
- The application will extract the text, process it, and display the cleaned version along with suggested changes.
