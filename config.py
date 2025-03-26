# config.py

import os # Added for path joining

# --- General Settings ---
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
POPPLER_PATH = r"C:\Program Files\poppler\Library\bin"  # Replace with your Poppler bin directory
TESSERACT_PATH = r"C:\Users\admin\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"  # Replace with your Tesseract path

# --- Directory Setup ---
# Define base directories relative to the project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # Assumes config.py is in the root

INPUT_PDF_DIR = os.path.join(PROJECT_ROOT, "input")      # NEW: Directory for input PDFs
EXTRACTED_TEXT_DIR = os.path.join(PROJECT_ROOT, "extracted_text") # Directory for generated .md files
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")             # Directory for final output files
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "templates")         # Directory for template files

# --- File Paths ---
# Template file paths (now using TEMPLATE_DIR)
MCQ_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "mcq_template.docx") # Renamed
SUMMARY_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "summary_template.docx")
REMAKE_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "remake_template.docx")

# Rules file path
RULES_TXT_PATH = os.path.join(PROJECT_ROOT, "rules.txt")

# --- Feature Toggles ---
# Set these to True or False to enable/disable specific generation steps
RUN_EXTRACTION = True      # NEW: Enable/Disable PDF text extraction step in main.py
GENERATE_MCQS = True       # Enable/Disable MCQ generation
GENERATE_SUMMARY = True   # Enable/Disable Summary generation
GENERATE_MINDMAP = True   # Enable/Disable Mind Map generation (Needs update for .md input)
GENERATE_REMAKE = True    # Enable/Disable Remake generation

# --- MCQ Generation Settings ---
TOKEN_LIMIT = 3000         # Max tokens per chunk for Gemini API calls. Adjust based on model limits/needs.
# Approximate number of words in the source text used to generate one MCQ.
# A lower value means more MCQs will be generated for the same amount of text.
WORDS_PER_QUESTION = 100   # Updated comment

# --- Mind Map Generation ---
# Note: mindmap_generator.py still needs updating to accept .md input directly.
# If GENERATE_MINDMAP is True, it will likely fail or use dummy paths as before.

# --- Gemini API Settings ---
# Choose your Gemini model. Check Google AI documentation for available models.
# Examples: 'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest', 'gemini-1.0-pro'
GEMINI_MODEL = 'gemini-2.0-flash'

# Configuration for the generation process
# Refer to Google AI API documentation for details on these parameters.
generation_config = {
    "temperature": 0.8, # Slightly lower for more deterministic generation, adjust as needed
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192, # Check model limits, 8192 is common for flash/pro
    "response_mime_type": "text/plain",
}

# Safety settings - adjust based on your content and risk tolerance
# Refer to Google AI API documentation for details.
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# --- Pandoc Settings ---
# Optional: Specify pandoc path if not in system PATH
# PANDOC_PATH = '/usr/local/bin/pandoc' # Example for macOS/Linux
PANDOC_PATH = None # Set to None to rely on system PATH

# Ensure output directories exist (can also be done in main.py)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
if not os.path.exists(EXTRACTED_TEXT_DIR):
    os.makedirs(EXTRACTED_TEXT_DIR)
if not os.path.exists(INPUT_PDF_DIR) and RUN_EXTRACTION:
     print(f"Warning: Input PDF directory '{INPUT_PDF_DIR}' not found. PDF extraction may fail.")
     # os.makedirs(INPUT_PDF_DIR) # Optionally create it