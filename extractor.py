import pdf2image
import pytesseract
from PIL import Image
import os
import config  # Import the config module


def extract_text_from_pdf(pdf_path, poppler_path):
    """Extracts text from a PDF file using OCR."""

    # Set Tesseract path from config, but only if it's not empty
    if config.TESSERACT_PATH:
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
    #No need for the else condition

    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if not pdf_path.lower().endswith(".pdf"):
            raise ValueError(f"Invalid file type. Expected a PDF file: {pdf_path}")

        images = pdf2image.convert_from_path(pdf_path, poppler_path=poppler_path)
        text = "\n".join(pytesseract.image_to_string(img) for img in images)
        return text.strip()

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except pdf2image.exceptions.PDFInfoNotInstalledError:
        print("Error: PDFInfoNotInstalledError. Ensure Poppler is correctly installed.")
        return None
    except pdf2image.exceptions.PDFPageCountError:
        print("Error: PDFPageCountError. Could not determine PDF page count.")
        return None
    except pdf2image.exceptions.PDFSyntaxError:
        print("Error: PDFSyntaxError. The PDF file may be corrupted.")
        return None
    except pytesseract.TesseractNotFoundError:
        print("Error: TesseractNotFoundError. Ensure Tesseract OCR is installed and the path is set in config.py or system PATH.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None