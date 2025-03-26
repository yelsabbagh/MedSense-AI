# extractor.py

import time
import pdf2image
import pytesseract
from PIL import Image # Make sure Pillow is installed: pip install Pillow
import os
import config
import traceback # Import traceback for detailed error logging

def extract_text_from_pdf(pdf_path, poppler_path):
    """
    Extracts text from a PDF file using pdf2image (Poppler) at 300 DPI
    and Tesseract OCR.

    Args:
        pdf_path (str): The path to the input PDF file.
        poppler_path (str): The path to the Poppler bin directory.

    Returns:
        str: The extracted text from all pages, separated by page breaks,
             or None if a critical error occurred.
    """
    print(f"\n--- Starting Extraction for: {os.path.basename(pdf_path)} ---")

    # --- Tesseract Path Configuration ---
    # Set Tesseract path from config, but only if it's not empty and exists
    tesseract_found = False
    if hasattr(config, 'TESSERACT_PATH') and config.TESSERACT_PATH:
        if os.path.exists(config.TESSERACT_PATH):
            try:
                pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
                # Optional: Check if tesseract command works
                # version = pytesseract.get_tesseract_version()
                # print(f"Extractor: Using Tesseract {version} at: {config.TESSERACT_PATH}")
                print(f"Extractor: Using Tesseract configured at: {config.TESSERACT_PATH}")
                tesseract_found = True
            except Exception as tess_err:
                 print(f"Extractor: Warning - Error accessing configured Tesseract ({config.TESSERACT_PATH}): {tess_err}")
                 print("Extractor: Will rely on Tesseract being in system PATH.")
        else:
            print(f"Extractor: Warning - Tesseract path in config not found: {config.TESSERACT_PATH}")
            print("Extractor: Will rely on Tesseract being in system PATH.")
    else:
        print("Extractor: TESSERACT_PATH not set in config. Will rely on Tesseract being in system PATH.")

    # Attempt to use system PATH Tesseract if not configured or config failed
    if not tesseract_found:
        try:
            # This will raise TesseractNotFoundError if not in PATH
            version = pytesseract.get_tesseract_version()
            print(f"Extractor: Found Tesseract {version} in system PATH.")
            tesseract_found = True
        except pytesseract.TesseractNotFoundError:
            print("Extractor: Error - Tesseract not found in config path OR system PATH.")
            print("Extractor: Please install Tesseract and set config.TESSERACT_PATH or add it to your system's PATH.")
            return None
        except Exception as e:
            print(f"Extractor: Warning - Unexpected error checking Tesseract in PATH: {e}")
            # Continue, assuming it might still work if the check failed weirdly

    # --- Poppler Path Validation ---
    if not poppler_path or not os.path.isdir(poppler_path):
         print(f"Extractor: Error - Poppler path is invalid or not specified in config: {poppler_path}")
         print("Extractor: Please ensure config.POPPLER_PATH points to the Poppler 'bin' directory.")
         return None

    try:
        # --- Input Validation ---
        if not os.path.exists(pdf_path):
            print(f"Extractor: Error - PDF file not found: {pdf_path}")
            return None # Return None instead of raising FileNotFoundError here
        if not pdf_path.lower().endswith(".pdf"):
             print(f"Extractor: Error - Invalid file type. Expected a PDF file: {pdf_path}")
             return None # Return None instead of raising ValueError

        print(f"Extractor: Processing '{os.path.basename(pdf_path)}'...")
        print(f"Extractor: Converting PDF to images at 300 DPI using Poppler from '{poppler_path}'...")

        # --- Convert PDF pages to images at 300 DPI ---
        # Use grayscale=True for potentially better OCR on standard text docs
        images = pdf2image.convert_from_path(
            pdf_path,
            dpi=300,
            poppler_path=poppler_path,
            fmt='png',
            grayscale=True,
            thread_count=4 # Use multiple threads for conversion if possible
        )
        num_pages = len(images)
        if num_pages == 0:
             print("Extractor: Warning - PDF conversion resulted in 0 images. PDF might be empty or corrupted.")
             return "" # Return empty string for empty PDF

        print(f"Extractor: Generated {num_pages} images. Starting Tesseract OCR...")

        # --- Perform OCR on each image ---
        text_parts = []
        total_ocr_time = 0
        for i, img in enumerate(images):
            page_num = i + 1
            print(f"Extractor:  - OCR on page {page_num}/{num_pages}...")
            start_time = time.time()
            page_text = ""
            try:
                # Specify language ('eng') for potentially better accuracy
                # Timeout can prevent hanging on problematic pages
                page_text = pytesseract.image_to_string(img, lang='eng', timeout=120) # 120 second timeout per page
                text_parts.append(page_text.strip())
            except RuntimeError as timeout_error:
                print(f"Extractor:    ERROR - Tesseract timed out on page {page_num}: {timeout_error}")
                text_parts.append(f"[ERROR: Tesseract OCR Timed Out on page {page_num}]")
            except pytesseract.TesseractError as ocr_err:
                 print(f"Extractor:    ERROR during Tesseract OCR on page {page_num}: {ocr_err}")
                 text_parts.append(f"[ERROR: Tesseract OCR Failed on page {page_num}]")
            except Exception as e:
                 print(f"Extractor:    UNEXPECTED ERROR during OCR on page {page_num}: {e}")
                 traceback.print_exc()
                 text_parts.append(f"[ERROR: Unexpected failure on page {page_num}]")
            finally:
                 # --- IMPORTANT: Close the image object to free memory ---
                 img.close()
                 end_time = time.time()
                 page_time = end_time - start_time
                 total_ocr_time += page_time
                 print(f"Extractor:    Page {page_num} finished in {page_time:.2f}s")


        avg_time = total_ocr_time / num_pages if num_pages > 0 else 0
        print(f"Extractor: Tesseract OCR finished for all pages.")
        print(f"Extractor: Total OCR time: {total_ocr_time:.2f}s (Avg: {avg_time:.2f}s/page)")

        # --- Join text with clear page breaks ---
        full_text = "\n\n--- Page Break ---\n\n".join(text_parts)
        print(f"--- Extraction Complete for: {os.path.basename(pdf_path)} ---")
        return full_text.strip()

    # --- Error Handling specific to libraries ---
    except pdf2image.exceptions.PDFInfoNotInstalledError:
        print(f"Extractor: Error - PDFInfoNotInstalledError. Poppler tools might be missing or not in the specified path: {poppler_path}")
        print("Extractor: Ensure Poppler is correctly installed and config.POPPLER_PATH is valid.")
        return None
    except pdf2image.exceptions.PDFPageCountError:
        print(f"Extractor: Error - PDFPageCountError. Could not determine PDF page count (PDF might be corrupted or password-protected): {pdf_path}")
        return None
    except pdf2image.exceptions.PDFSyntaxError:
        print(f"Extractor: Error - PDFSyntaxError. The PDF file may be corrupted or invalid: {pdf_path}")
        return None
    # TesseractNotFoundError should be caught earlier now
    # except pytesseract.TesseractNotFoundError:
    #     print("Extractor: Error - TesseractNotFoundError...") # Handled above
    #     return None
    except FileNotFoundError as e: # Catch specific file errors if paths are wrong mid-process
        print(f"Extractor: Error - File operation failed: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        # Catch any other unexpected exceptions during the process
        print(f"Extractor: An unexpected error occurred in extract_text_from_pdf: {e}")
        traceback.print_exc() # Print detailed traceback for debugging
        return None

# --- Example Usage (Optional, for testing extractor directly) ---
# if __name__ == "__main__":
#     # Make sure config.py is importable and paths are set
#     pdf_to_process = "path/to/your/test_document.pdf" # Example input path
#     output_md_path = "output/test_document_extracted.md" # Example output MD path
#     poppler_install_path = config.POPPLER_PATH # Get from config
#
#     print("Starting extraction test...")
#     extracted_content = extract_text_from_pdf(pdf_to_process, poppler_install_path)
#
#     if extracted_content is not None:
#         print("\n--- EXTRACTION SUCCESSFUL ---")
#         # Save to MD file
#         os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
#         try:
#             with open(output_md_path, "w", encoding="utf-8") as f:
#                 f.write(extracted_content)
#             print(f"Output saved to {output_md_path}")
#         except IOError as e:
#             print(f"Error saving extracted text to file: {e}")
#     else:
#         print("\n--- EXTRACTION FAILED ---")