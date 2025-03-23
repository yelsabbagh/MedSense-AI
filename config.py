# config.py
API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your actual API key
POPPLER_PATH = r"C:\Program Files\poppler\Library\bin"  # Replace with your Poppler bin directory
TESSERACT_PATH = r"C:\Users\admin\AppData\Local\Programs\Tesseract-OCR\tesseract.exe" # Add Tesseract path
TOKEN_LIMIT = 3000  # Maximum number of tokens per text chunk sent to the Gemini API.
WORDS_PER_QUESTION = 300  # The smaller the number, the more the generated MCQs.
OUTPUT_DIR = "output"