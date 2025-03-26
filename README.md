# MedSense AI: AI-Powered Medical Learning Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

MedSense AI is a Python application designed to streamline medical education by transforming lecture text into diverse, high-quality study materials. Starting primarily from structured Markdown (`.md`) files extracted from lectures, it leverages Google's Gemini API for intelligent content generation and refinement. The tool automates the creation of Multiple-Choice Questions (MCQs), concise Summaries, high-fidelity Remakes, and structured Mind Maps, assisting students and educators in efficient learning and content review.

The core workflow involves processing `.md` input, utilizing AI for initial generation, performing AI-driven verification/correction for enhanced reliability (for MCQs, Summaries, Remakes), converting generated content (often via JSON or Markdown intermediates) into final formats, and applying sophisticated styling using Pandoc and `python-docx` before merging with presentation templates using `docxtpl`.

## Core Features & Workflow Emphasis

MedSense AI offers several powerful generation capabilities:

1.  **MCQ Generation:**
    *   **Input:** Lecture text (`.md`), `rules.txt` (custom guidelines).
    *   **AI Process:** Text chunking -> Gemini generates MCQs based on rules -> Gemini **verifies/corrects** generated MCQs against rules.
    *   **Processing:** Corrected text parsed -> Formatted into Markdown table.
    *   **Output:**
        *   `.csv` file containing questions and answers.
        *   Styled `.docx` file using `mcq_template.docx`, featuring:
            *   Table format (Question | Answer).
            *   Specific styling via `python-docx`: Poppins font, table borders, **rows set to not break across pages**, **header row repetition disabled**, question stem bolding fixed, line breaks within questions handled.

2.  **Summary Generation:**
    *   **Input:** Lecture text (`.md`).
    *   **AI Process:** Gemini generates a high-yield summary structured as **JSON** (sections with type: paragraph, list, or table) -> Gemini **verifies/corrects** the JSON for accuracy, conciseness, and structure against the original text.
    *   **Processing:** Verified JSON converted to a Markdown string (using H2 headings, paragraphs, lists, and `| Key Point | Details |` tables).
    *   **Output:**
        *   Styled `.docx` file using `summary_template.docx`, featuring:
            *   Content structure derived from JSON (headings, paragraphs, lists, tables).
            *   Styling via `python-docx`: Poppins font, table borders, LTR alignment.

3.  **Remake Generation:**
    *   **Input:** Lecture text (`.md`).
    *   **AI Process:** Gemini reconstructs lecture content with **high fidelity** into a structured **JSON** (sections containing `content` list of `{"key_point": ..., "details": ...}` pairs) -> Gemini **verifies/corrects** the JSON for fidelity, completeness, and structure against the original text.
    *   **Processing:** Verified JSON converted to a Markdown string (using H2 headings and `| Key Point | Details |` tables for each section). Line breaks in details preserved using `<br>`.
    *   **Output:**
        *   Styled `.docx` file using `remake_template.docx`, featuring:
            *   Table-based structure for high fidelity content presentation.
            *   Styling via `python-docx`: Poppins font, table borders, LTR alignment, bolding for "Key Point" column.

4.  **Mind Map Generation:**
    *   **Input:** Lecture text (`.md`).
    *   **AI Process:** Gemini generates a hierarchical structure as **JSON** (nodes with `title`, `children`, and optional `hint` for table structure).
    *   **Processing:** Python script parses the JSON, recursively builds the detailed `content.json` required by XMind, applies styling presets based on topic level and hints, generates `manifest.json` and `metadata.json`.
    *   **Output:**
        *   `.xmind` file (packaged ZIP archive) containing the generated `content.json` and other necessary files.
        *   *Note:* Styling and structure (including `treetable` layout based on hints) are applied programmatically. Output appearance depends on Gemini's structure and the defined Python style constants.

**Other Key Features:**

*   **Markdown Input:** Primarily processes `.md` files from the `extracted_text/` directory.
*   **Optional PDF Extraction:** Includes `extractor.py` (using Poppler & Tesseract) to convert PDFs in `input/` to `.md` files in `extracted_text/` (controlled by `RUN_EXTRACTION` flag).
*   **AI Verification:** Employs secondary Gemini calls for MCQs, Summaries, and Remakes to enhance accuracy and adherence to instructions.
*   **Advanced DOCX Generation & Styling:** Utilizes a robust pipeline:
    1.  AI generates structured content (JSON or text).
    2.  Python converts to Markdown (often involving tables).
    3.  `pypandoc` converts Markdown to a base DOCX.
    4.  `python-docx` applies detailed styling (fonts, table borders, table row properties, LTR, bolding, etc.).
    5.  `docxtpl` merges the styled content DOCX with a cover/intro page template (`.docx`), incorporating context like `lecture_name`.
*   **Configurable:** Centralized settings in `config.py` (API keys, paths, feature toggles, generation parameters, directories).
*   **Error Handling & Retries:** Includes robust error handling and exponential backoff for Gemini API calls.

## Prerequisites

*   **Python 3.7+:** Ensure a compatible Python version is installed.
*   **Pandoc:** Required by `pypandoc`. Download and install from [https://pandoc.org/installing.html](https://pandoc.org/installing.html). Ensure it's added to your system's PATH or configure `PANDOC_PATH` in `config.py`.
*   **Tesseract OCR:** (Required *only* if `RUN_EXTRACTION` is `True` for PDF input)
    *   Download and install: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
    *   Add the installation directory to your system's `PATH` *or* set the full executable path in `TESSERACT_PATH` in `config.py`.
*   **Poppler:** (Required *only* if `RUN_EXTRACTION` is `True` for PDF input)
    *   Download pre-built binaries (e.g., for Windows: [https://github.com/oschwartz10612/poppler-windows/releases/](https://github.com/oschwartz10612/poppler-windows/releases/)). Install via package manager on Linux/macOS.
    *   Extract and set `POPPLER_PATH` in `config.py` to the Poppler `bin` directory (e.g., `r"C:\Program Files\poppler\Library\bin"`).
*   **Google AI Studio API Key:**
    *   Obtain from Google AI Studio: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
    *   Set the `API_KEY` variable in `config.py`.
*   **Python Packages:** Install required packages. Ensure `pypandoc`, `lxml`, and `xmind` are included.

    ```bash
    # Ensure requirements.txt contains:
    # google-generativeai
    # pdf2image
    # pytesseract
    # pandas
    # python-docx
    # docxtpl
    # xmind # For mindmap generation
    # pypandoc # For markdown to docx conversion
    # lxml # Often needed by python-docx/docxtpl

    pip install -r requirements.txt
    ```

## Installation

1.  **Clone the Repository:**
    ```bash
    git clone <YOUR_REPOSITORY_URL> # Replace with your repository URL
    cd <PROJECT_DIRECTORY_NAME>
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Create Directories:** Ensure the following directories exist in your project root:
    *   `input/` (Optional: for input PDFs if `RUN_EXTRACTION=True`)
    *   `extracted_text/` (**Required**: Place input `.md` files here, or output location for PDF extraction)
    *   `output/` (**Required**: For generated `.csv`, `.docx`, `.xmind` files)
    *   `templates/` (**Required**: For `.docx` templates)

## Configuration (`config.py`)

*   Open `config.py` and carefully set the following:
    *   `API_KEY`: Your Google AI Studio API key (**Required**).
    *   `POPPLER_PATH`: (Required if `RUN_EXTRACTION=True`) Full path to your Poppler `bin` directory.
    *   `TESSERACT_PATH`: (Required if `RUN_EXTRACTION=True`) Full path to your `tesseract.exe` (or command).
    *   `PANDOC_PATH`: (Optional) Full path to your Pandoc executable if not in system PATH. Set to `None` to rely on PATH.
    *   `INPUT_PDF_DIR`, `EXTRACTED_TEXT_DIR`, `OUTPUT_DIR`, `TEMPLATE_DIR`: Verify or adjust directory paths. Relative paths based on the project root are recommended.
    *   **Feature Toggles:** Set `True` or `False` for `RUN_EXTRACTION`, `GENERATE_MCQS`, `GENERATE_SUMMARY`, `GENERATE_MINDMAP`, `GENERATE_REMAKE`.
    *   Review other settings like `GEMINI_MODEL`, `generation_config`, `safety_settings`, `TOKEN_LIMIT`, `WORDS_PER_QUESTION`.

## Usage Workflow

1.  **Prepare Input `.md` Files:** Place your lecture text files (UTF-8 encoded) as `.md` files inside the `extracted_text/` directory (e.g., `lecture1_extracted.md`).
    *   *(Optional PDF Input)*: If starting from PDFs, place them in `input/` (or the configured `INPUT_PDF_DIR`) and set `RUN_EXTRACTION = True` in `config.py`. Running the script will first attempt to convert these PDFs to `.md` files in `extracted_text/`.
2.  **Prepare Templates:** Ensure the required `.docx` template files exist in the `templates/` directory:
    *   `mcq_template.docx`
    *   `summary_template.docx`
    *   `remake_template.docx`
    *(See "DOCX Template Format" below for details)*
3.  **Configure Features:** Edit `config.py` and set the feature toggles (`GENERATE_...`) to `True` for the outputs you want to create.
4.  **Define MCQ Rules (Optional):** If `GENERATE_MCQS` is `True`, ensure `rules.txt` exists in the project root with your desired MCQ generation guidelines.
5.  **Run the Script:** Open a terminal or command prompt in the project's root directory and run:
    ```bash
    python main.py
    ```
6.  **Check Output:** Generated files (`.csv`, `.docx`, `.xmind`) will be saved in the `output/` directory, named according to the input `.md` file's base name (e.g., `output/lecture1_mcqs.docx`, `output/lecture1_summary.docx`).

## DOCX Template Format (`templates/*.docx`)

The `.docx` files in the `templates/` directory serve primarily as cover pages or introductory sections.

*   **Placeholder:** All templates (`mcq_template.docx`, `summary_template.docx`, `remake_template.docx`) MUST include the Jinja2-style placeholder `{{ lecture_name }}` where you want the lecture title (derived automatically from the input filename) to appear.
*   **Content:** Design the cover page, headers, footers, and any introductory text directly within the template file.
*   **Merging Process:** The script performs the following steps:
    1.  Renders the `.docx` template using `docxtpl`, filling in `{{ lecture_name }}`.
    2.  Generates the main content (MCQs, Summary, Remake) via AI and Python processing, resulting in a Markdown string.
    3.  Uses `pypandoc` to convert the Markdown string into a temporary, unstyled DOCX file.
    4.  Applies detailed styling (fonts, table properties, alignment, etc.) to this temporary content DOCX using `python-docx`.
    5.  Appends the fully styled content (usually after a page break) to the rendered template document.
    6.  Saves the combined document as the final output file.

## Project Structure

```
MedSense-AI/
├── input/               <- (Optional) Place input .pdf files here if RUN_EXTRACTION=True
├── extracted_text/      <- Place input .md files here (or output from PDF extraction)
├── output/              <- Generated .csv, .docx, .xmind files
├── templates/           <- Place .docx templates here
│   ├── mcq_template.docx
│   ├── summary_template.docx
│   └── remake_template.docx
├── config.py            <- Configuration (API key, paths, toggles, Gemini params)
├── extractor.py         <- PDF text extraction (optional, uses Poppler/Tesseract)
├── mcq_generator.py     <- MCQ generation, verification, styling, DOCX creation
├── summary_generator.py <- Summary generation (JSON), verification, MD conversion, styling, DOCX creation
├── remake_generator.py  <- Remake generation (JSON), verification, MD conversion, styling, DOCX creation
├── mindmap_generator.py <- Mind Map generation (JSON), XMind packaging
├── main.py              <- Main execution script orchestrating the process
├── requirements.txt     <- Python package dependencies
├── rules.txt            <- (Optional) MCQ generation rules for AI
└── README.md            <- This file
└── LICENSE              <- MIT License file (Add one if you haven't!)
```

## Contributing

(Contributions are welcome. Please follow standard fork-and-pull-request procedures. Consider adding tests for new features.)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.