# --- START OF FILE main.py ---

import mcq_generator
import mindmap_generator # Import the updated mindmap generator
import summary_generator
import remake_generator
import config
import os
import glob
import traceback # Keep for detailed error logging

def main():
    # --- Directory Setup ---
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)
        print(f"Created output directory: {config.OUTPUT_DIR}")

    # Ensure the source directory for Markdown files exists
    if not os.path.exists(config.EXTRACTED_TEXT_DIR):
        print(f"Error: Extracted text directory '{config.EXTRACTED_TEXT_DIR}' not found.")
        print("Please create this directory and place your source .md files in it, or enable RUN_EXTRACTION in config.py if starting from PDFs.")
        return

    # --- Optional PDF Extraction Step ---
    if config.RUN_EXTRACTION:
        print("\n--- Starting Optional PDF Extraction ---")
        import extractor # Import only if needed
        if not os.path.exists(config.INPUT_PDF_DIR):
            print(f"Error: Input PDF directory '{config.INPUT_PDF_DIR}' not found, but RUN_EXTRACTION is True.")
            print("Please create this directory and place input PDFs there, or set RUN_EXTRACTION to False.")
            # Optionally decide whether to stop or continue without extraction
            # return # Stop if PDF input is mandatory when RUN_EXTRACTION is True
        else:
            pdf_files = glob.glob(os.path.join(config.INPUT_PDF_DIR, "*.pdf"))
            if not pdf_files:
                print(f"No PDF files found in '{config.INPUT_PDF_DIR}'. Skipping extraction step.")
            else:
                print(f"Found {len(pdf_files)} PDF(s) for extraction...")
                extraction_success_count = 0
                extraction_fail_count = 0
                for pdf_path in pdf_files:
                    pdf_base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                    output_md_path = os.path.join(config.EXTRACTED_TEXT_DIR, f"{pdf_base_name}_extracted.md")

                    # Simple check to avoid re-extracting if MD exists
                    if os.path.exists(output_md_path):
                        print(f"Skipping extraction for '{pdf_base_name}.pdf' as '{os.path.basename(output_md_path)}' already exists.")
                        continue

                    print(f"Extracting text from '{pdf_path}'...")
                    extracted_content = extractor.extract_text_from_pdf(pdf_path, config.POPPLER_PATH)

                    if extracted_content is not None:
                        try:
                            os.makedirs(config.EXTRACTED_TEXT_DIR, exist_ok=True)
                            with open(output_md_path, "w", encoding="utf-8") as f:
                                f.write(extracted_content)
                            print(f"Extracted text saved to '{output_md_path}'")
                            extraction_success_count += 1
                        except IOError as e:
                            print(f"Error saving extracted text to '{output_md_path}': {e}")
                            extraction_fail_count += 1
                    else:
                        print(f"Failed to extract text from '{pdf_path}'.")
                        extraction_fail_count += 1

                print(f"--- PDF Extraction Complete: {extraction_success_count} succeeded, {extraction_fail_count} failed ---")
                if extraction_fail_count > 0:
                    print("Review errors above. Subsequent steps will proceed using existing/successfully extracted .md files.")

    # --- Find Markdown Files in the extraction directory ---
    print(f"\n--- Searching for Markdown files in: {config.EXTRACTED_TEXT_DIR} ---")
    md_files = glob.glob(os.path.join(config.EXTRACTED_TEXT_DIR, "*.md"))

    if not md_files:
        print(f"No Markdown (.md) files found in '{config.EXTRACTED_TEXT_DIR}'. Nothing to process.")
        return
    else:
         print(f"Found {len(md_files)} Markdown file(s) to process.")


    # --- Process Each Markdown File ---
    for md_path in md_files:
        print(f"\n--- Processing: {os.path.basename(md_path)} ---")
        try:
            # Derive base name (remove _extracted suffix if present)
            base_name = os.path.splitext(os.path.basename(md_path))[0]
            if base_name.endswith("_extracted"):
                base_name = base_name[:-10] # Remove the suffix
            print(f"Using base name for output: {base_name}")

            # --- Generate MCQs (if enabled) ---
            if config.GENERATE_MCQS:
                print("\nAttempting MCQ Generation...")
                mcq_csv_path = os.path.join(config.OUTPUT_DIR, f"{base_name}_mcqs.csv")
                mcq_template_path = config.MCQ_TEMPLATE_PATH
                mcq_docx_output_path = os.path.join(config.OUTPUT_DIR, f"{base_name}_mcqs.docx")

                if not os.path.exists(mcq_template_path):
                     print(f"  ERROR: MCQ template not found at '{mcq_template_path}'. Skipping MCQ generation.")
                else:
                    # Call the MCQ generator function
                    success = mcq_generator.create_mcqs_and_process(
                        md_path=md_path,
                        output_csv_path=mcq_csv_path,
                        output_docx_path=mcq_docx_output_path,
                        template_path=mcq_template_path,
                    # Pass the cleaned base_name
                    )
                    if success:
                        print(f"  MCQ Generation completed successfully for '{base_name}'.")
                    else:
                        print(f"  MCQ Generation failed for '{base_name}'. See logs above.")

            # --- Generate Summary (if enabled) ---
            if config.GENERATE_SUMMARY:
                print("Attempting Summary Generation...")
                summary_docx_path = os.path.join(config.OUTPUT_DIR, f"{base_name}_summary.docx")
                summary_template_path = config.SUMMARY_TEMPLATE_PATH
                if not os.path.exists(summary_template_path):
                    print(f"Error: Summary template not found at '{summary_template_path}'. Skipping Summary generation.")
                else:
                    # OLD LINE: Passing 4 arguments
                    # if summary_generator.create_summary(md_path, summary_docx_path, summary_template_path, base_name):

                    # NEW LINE: Passing only 3 arguments
                    if summary_generator.create_summary(md_path, summary_docx_path, summary_template_path):
                        # Success message is now likely inside create_summary
                        print(f"Summary generation process completed for {md_path}.") # Keep confirmation here
                    else:
                        print(f"Failed to generate summary for {md_path}.")
            
            # --- Generate Remake (if enabled) ---
            if config.GENERATE_REMAKE:
                print("\nAttempting Remake Generation...")
                remake_docx_path = os.path.join(config.OUTPUT_DIR, f"{base_name}_remake.docx")
                remake_template_path = config.REMAKE_TEMPLATE_PATH

                if not os.path.exists(remake_template_path):
                     print(f"  ERROR: Remake template not found at '{remake_template_path}'. Skipping Remake generation.")
                else:
                    # Call the remake generator function
                    if remake_generator.create_remake(md_path, remake_docx_path, remake_template_path): # Pass base_name
                        print(f"  Remake generation completed successfully for '{base_name}'.")
                    else:
                        print(f"  Remake generation failed for '{base_name}'. See logs above.")

            # --- Generate Mind Map (if enabled) ---
            if config.GENERATE_MINDMAP:
                print("\nAttempting Mind Map Generation...")
                xmind_path = os.path.join(config.OUTPUT_DIR, f"{base_name}_mindmap.xmind")

                # --- Call the UPDATED mindmap_generator using the ACTUAL md_path ---
                # The new generator handles reading MD and creating the XMind file
                if mindmap_generator.create_mind_map(md_path, xmind_path):
                    print(f"  Mind map generated successfully: {xmind_path}")
                else:
                    # Errors are logged within the mindmap_generator function
                    print(f"  Mind map generation failed for '{base_name}'. See logs above.")

        except Exception as e:
            print(f"\n!!! An CRITICAL error occurred while processing '{os.path.basename(md_path)}': {e} !!!")
            # Print detailed traceback for debugging critical errors
            traceback.print_exc()
            print(f"--- Skipping further processing for '{os.path.basename(md_path)}' due to error ---")
            continue # Move to the next file

    print("\n--- All Processing Complete ---")

# Corrected block at the end of main.py

if __name__ == "__main__":
    # Check for API Key early - REMOVED the overly strict "AIzaSy" check
    if not config.API_KEY in config.API_KEY:
         print("\n--- FATAL ERROR ---")
         print("Google AI API Key (API_KEY) in config.py is missing or still contains 'YOUR_API_KEY'.")
         print("Please obtain a valid API key from Google AI Studio (https://makersuite.google.com/app/apikey) and update config.py.")
         print("Ensure the key is pasted correctly within the quotes.")
         print("-------------------\n")
    else:
        print("Starting MedSense AI processing...")
        # Optional: Add more setup checks here if needed (e.g., Poppler/Tesseract if RUN_EXTRACTION is True)
        main()