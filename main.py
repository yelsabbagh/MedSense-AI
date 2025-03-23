import extractor
import generator
import converter
import config
import os
import glob

def main():
    input_dir = "input"
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found. Please create it.")
        return

    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in '{input_dir}'.")
        return

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path}")
        try:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            csv_path = os.path.join(config.OUTPUT_DIR, f"{base_name}_mcqs.csv")
            docx_path = os.path.join(config.OUTPUT_DIR, f"{base_name}_mcqs.docx")  # Single DOCX output
            template_path = os.path.join("templates", "mcq_template_1.docx") # Single template


            # Generate MCQs and save directly to CSV
            if generator.create_mcqs_and_save_to_csv(pdf_path, csv_path):
                print(f"MCQs generated and saved to: {csv_path}")

                # Convert CSV to DOCX using the template
                converter.csv_to_docx(csv_path, template_path, docx_path, base_name) # Pass base_name
                print(f"DOCX file created: {docx_path}")

            else:
                print(f"Failed to generate MCQs for {pdf_path}.")

        except Exception as e:
            print(f"An error occurred while processing {pdf_path}: {e}")

if __name__ == "__main__":
    main()