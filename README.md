# MedSense-AI
AI-powered tool for generating medical MCQs and summaries from lecture PDFs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

MedSense AI is a Python application that streamlines the creation of medical Multiple-Choice Questions (MCQs) from lecture PDFs. It utilizes Google's Gemini Pro API for intelligent question generation and verification, producing formatted output in both CSV and DOCX formats.  This tool is designed to assist medical students and educators in preparing for exams like the USMLE.

## Features

*   **PDF Text Extraction:** Converts PDF lecture slides to images and uses OCR (via `pytesseract`) to accurately extract the text content.
*   **Gemini Pro API Integration:** Leverages the power of the Gemini Pro API to generate MCQs based on the extracted text, adhering to a customizable set of rules defined in `rules.txt`.
*   **Automated MCQ Generation:** Intelligently chunks the extracted text and dynamically determines the number of MCQs to generate per chunk, based on configurable parameters.
*   **MCQ Verification and Correction:** Employs a second Gemini Pro API call to verify the generated MCQs against the specified rules and *automatically correct* any identified violations, ensuring higher quality questions.
*   **CSV Output:** Produces a well-structured CSV file containing the generated MCQs, with the following columns:
    *   `QID`: Unique question ID (e.g., `QID:1714008490-1`).
    *   `MCQ`: The complete question stem and answer choices (with correct formatting, but *without* Markdown bolding syntax in the CSV itself).
    *   `CorrectAnswer`: The correct answer choice, including the letter and text (e.g., "c) 1 in 600 births").
*   **DOCX Output (Templated):** Generates a professionally formatted Word document (`.docx`) from the CSV data, using a user-provided template (`mcq_template_1.docx`).  The template supports:
    *   A cover page with the lecture title (automatically populated).
    *   An introduction page with a customizable Arabic description.
    *   Styled MCQs (font, size, bolding, spacing) defined by Word styles within the template.
*   **Configurable:** Uses a `config.py` file to store API keys, file paths (including Tesseract and Poppler), token limits, and other settings, making the application adaptable to different environments.
*   **Error Handling:** Includes robust error handling for file operations, API calls, PDF processing issues, and template rendering.
*   **Retry Mechanism:** Implements an exponential backoff retry mechanism for Gemini API calls to gracefully handle rate limits and transient network errors.

## Prerequisites

*   **Python 3.7+:** Ensure you have a compatible Python version installed.
*   **Tesseract OCR:**
    *   Download and install Tesseract OCR from: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
    *   Add the Tesseract installation directory to your system's `PATH` environment variable *or* specify the full path to `tesseract.exe` in the `config.py` file (using the `TESSERACT_PATH` variable).
*   **Poppler:**
    *   Download pre-built Windows binaries from: [https://github.com/oschwartz10612/poppler-windows/releases/](https://github.com/oschwartz10612/poppler-windows/releases/)
    *   Extract the ZIP file and set the `POPPLER_PATH` in `config.py` to the `bin` directory within the extracted folder (e.g., `r"C:\Program Files\poppler\Library\bin"`).
*   **Google AI Studio API Key:**
    *   Obtain a Gemini API key from Google AI Studio: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
    *   Set the `API_KEY` variable in `config.py` to your API key.
*   **Python Packages:** Install the required packages using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

## Installation

1.  **Clone the Repository:**

    ```bash
    git clone <YOUR_REPOSITORY_URL>  # Replace with your repository URL
    cd MedSense-AI
    ```

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure `config.py`:**
    *   Create a `config.py` file in the project root directory (if it doesn't exist).
    *   Add the following settings, replacing the placeholder values with your actual values:

        ```python
        API_KEY = "YOUR_GEMINI_API_KEY"  # Your Google AI Studio API key
        POPPLER_PATH = r"C:\path\to\your\poppler\bin"  # Path to Poppler's bin directory
        TESSERACT_PATH = r"C:\path\to\tesseract.exe"  # Path to tesseract.exe (or leave empty if in PATH)
        TOKEN_LIMIT = 3000  # Maximum tokens per Gemini API request chunk
        WORDS_PER_QUESTION = 100  # Approximate words per question (adjust for density)
        OUTPUT_DIR = "output"  # Directory to save output files
        ```

## Usage

1.  **Prepare the DOCX Template (`mcq_template_1.docx`):**
    *   Create a Word document named `mcq_template_1.docx` and place it in the `templates/` directory.
    *   **Page 1 (Cover Page):** Design your cover page. Include the placeholder `{{lecture_name}}` (either in a text box or a regular paragraph) where you want the lecture title to appear.
    *   **Page 2 (Description):** Add the Arabic description (provided in previous responses), making sure it's formatted correctly (right-to-left alignment, appropriate Arabic font).  The description can also include the `{{lecture_name}}` placeholder.
    *   **Page 3 Onwards (MCQs):** Add the following `docxtpl` loop *exactly* as shown:

        ```docx
        {% for mcq in mcqs %}
        {{ mcq.qid }}
        {{ mcq.question }}
        a) {{ mcq.a }}
        b) {{ mcq.b }}
        c) {{ mcq.c }}
        d) {{ mcq.d }}
        e) {{ mcq.e }}

        {{ mcq.correct_answer }}
        {% endfor %}
        ```
    *   **Crucially:** Create Word styles named `MCQ_QID`, `MCQ_Question`, `MCQ_Answer`, and `MCQ_Correct`. Apply these styles to the corresponding placeholders *within* the loop (e.g., select `{{ mcq.qid }}` and apply the `MCQ_QID` style). Format these styles as desired (bolding, font, size, spacing). *Do not* apply the `Normal` style within the loop.
    *   **Last Page (Thank You):** Add a thank you message.

2.  **Add PDF Lectures:** Place the PDF lecture files you want to process in the `input/` directory.

3.  **Define Rules (`rules.txt`):** Create a `rules.txt` file in the project root directory. This file should contain the rules for MCQ generation and verification, one rule per line. Be as specific as possible.  Example:

    ```
    - Questions must assess clinical reasoning and application of knowledge.
    - Avoid "all of the above" and "none of the above" answer choices.
    - Answer choices should be homogeneous (similar length and style).
    - Distractors (incorrect answers) should be plausible and address common misconceptions.
    - Questions should be relevant to medical exam standards (e.g., USMLE).
    - Avoid ambiguous or tricky wording.
    - Each question should have 5 answer choices.
    - The correct answer must be clearly indicated.
    - Focus on clinically relevant scenarios.
    - Use clear and concise language.
    - Ensure questions are independent and do not rely on information from other questions.
    ```

4.  **Run the Script:**

    ```bash
    python main.py
    ```

    The script will:
    *   Process each PDF file in the `input/` directory.
    *   Extract text using OCR.
    *   Generate MCQs using the Gemini Pro API.
    *   Verify and correct the MCQs using a second Gemini API call.
    *   Create a CSV file (`output/<pdf_name>_mcqs.csv`) with the generated MCQs.
    *   Create a DOCX file (`output/<pdf_name>_mcqs.docx`) using the `mcq_template_1.docx` template.

## Project Structure


MedSense-AI/
├── input/ <- Place PDF lectures here
├── output/ <- Generated CSV and DOCX files
├── templates/ <- Place your DOCX template here
│ └── mcq_template_1.docx
├── config.py <- Configuration settings
├── converter.py <- Handles CSV to DOCX conversion
├── extractor.py <- Handles PDF text extraction
├── generator.py <- Handles MCQ generation, verification, correction, and CSV creation
├── main.py <- Main script
├── requirements.txt <- Lists required Python packages
├── rules.txt <- MCQ generation and verification rules
└── tests/ <- (Optional) Unit tests
└── LICENSE <- Project License

## Contributing

(Optional: Add guidelines for contributing to your project.)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
