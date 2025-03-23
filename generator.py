import google.generativeai as genai
import config
import re
import os
import time
import pandas as pd
from google.api_core.exceptions import ResourceExhausted
import extractor

def generate_with_retry(model, prompt, retries=99, delay=2):
    """Retries the generation request if rate-limited or fails."""
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except ResourceExhausted as e:
            if attempt < retries - 1:
                print(f"Rate limit exceeded, retrying... ({attempt + 1}/{retries})")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print("Maximum retries reached. Unable to complete the request.")
                raise e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None


def generate_mcqs(text, num_questions):
    genai.configure(api_key=config.API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')  # gemini-2.0-pro-exp-02-05 ; gemini-2.0-flash

    with open("rules.txt", "r") as f:
        rules = f.read()

    prompt = f"""rules.txt:{rules}

prompt:You are a medical exam question generator. Your task is to create Multiple-Choice Questions (MCQs) from the provided `#text_chunk` of lecture material, strictly following the guidelines in the attached `rules.txt` file. Focus on clinical reasoning, accuracy, and adherence to medical exam standards (e.g., USMLE).  

**Output Format:**  
Generate questions in the following structure. *Include all components below for each question*:  

1. **Unique Question ID**: Use the format `QID:[RANDOMTIMESTAMP]-[COUNTER]` (e.g., `QID:0000000000-1`); is in **bold**.  
2. **Question Text**: Phrased as a clinical vignette or direct question; is in **bold**.  
3. **Five Answer Choices**: Labeled `a)` to `e)`, homogeneous and plausible; ARE NOT in **bold**.  
4. **Correct Answer**: letter **and** content of the correct choice; is in **bold**.  

**Example:**  
**QID:1713989294-1**  
**A 32-year-old woman with a history of asthma presents with sudden-onset dyspnea and wheezing after exposure to pollen. Her chest X-ray shows hyperinflated lungs. Which of the following is the most appropriate immediate treatment?**  
a) Oral corticosteroids  
b) Intravenous antibiotics  
c) Subcutaneous epinephrine  
d) Inhaled albuterol
e) Supplemental oxygen via nasal cannula  

**Correct Answer: d) Inhaled albuterol**  

**QID:1713989294-2**  
**Which cytokine is primarily responsible for the pathogenesis of rheumatoid arthritis?** 
a) Interleukin-1 (IL-1)  
b) Tumor necrosis factor-alpha (TNF-a)
c) Interferon-gamma (IFN-g)  
d) Interleukin-6 (IL-6)  
e) Interleukin-17 (IL-17)  

**Correct Answer: b) Tumor necrosis factor-alpha (TNF-a)**  

- NEVER REPLY WITH YOUR OWN SELF LIKE "Introductions or Conclusions e.g. Certaily? Here you go...."; YOUR RESPONSE SHOULD BE THE ABOVE FORMATING WITH NO EXTRAS.

Based of the above instructions **and** the rules.txt, now generate {num_questions} MCQs from the provided lecture content:
Here is the `#text_chunk`:
{text}
"""
    # Use the retry function here
    return generate_with_retry(model, prompt)

def chunk_text(text, token_limit):
    # (This function remains the same)
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk.split()) + len(sentence.split()) <= token_limit:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def calculate_num_questions(text, words_per_question):
    # (This function remains the same)
    word_count = len(text.split())
    num_questions = int((word_count / words_per_question) * 10)
    return max(1, num_questions)

def verify_and_correct_mcqs(mcq_text):
    """Verifies and corrects the generated MCQs."""
    genai.configure(api_key=config.API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')

    with open("rules.txt", "r") as f:
        rules = f.read()

    prompt = f"""rules.txt:{rules}

prompt:You are a medical exam question verifier and corrector. Your task is to:

1.  Analyze the following Multiple-Choice Questions (MCQs) for any violations of the rules provided above.
2.  If any violations are found, correct the questions to comply with the rules.
3.  Return *only* the corrected and verified MCQs in the original format. Do *not* include any explanations or error messages.

**Output Format:**  
Generate questions in the following structure. *Include all components below for each question*:  

1. **Unique Question ID**: Use the format `QID:[RANDOMTIMESTAMP]-[COUNTER]` (e.g., `QID:0000000000-1`); is in **bold**.  
2. **Question Text**: Phrased as a clinical vignette or direct question; is in **bold**.  
3. **Five Answer Choices**: Labeled `a)` to `e)`, homogeneous and plausible; ARE NOT in **bold**.  
4. **Correct Answer**: letter **and** content of the correct choice; is in **bold**.  

**Example:**  
**QID:1713989294-1**  
**A 32-year-old woman with a history of asthma presents with sudden-onset dyspnea and wheezing after exposure to pollen. Her chest X-ray shows hyperinflated lungs. Which of the following is the most appropriate immediate treatment?**  
a) Oral corticosteroids  
b) Intravenous antibiotics  
c) Subcutaneous epinephrine  
d) Inhaled albuterol
e) Supplemental oxygen via nasal cannula  

**Correct Answer: d) Inhaled albuterol**  

**QID:1713989294-2**  
**Which cytokine is primarily responsible for the pathogenesis of rheumatoid arthritis?** 
a) Interleukin-1 (IL-1)  
b) Tumor necrosis factor-alpha (TNF-a)
c) Interferon-gamma (IFN-g)  
d) Interleukin-6 (IL-6)  
e) Interleukin-17 (IL-17)  

**Correct Answer: b) Tumor necrosis factor-alpha (TNF-a)**

Here are the MCQs to verify and correct:

{mcq_text}
"""
    # Use the retry function and return the corrected MCQs
    return generate_with_retry(model, prompt)

def create_mcqs_and_save_to_csv(pdf_path, output_csv_path):
    """Extracts text, generates, verifies, corrects, and saves MCQs to CSV."""
    text = extractor.extract_text_from_pdf(pdf_path, config.POPPLER_PATH)
    if text is None:
        return False

    chunks = chunk_text(text, config.TOKEN_LIMIT)
    all_mcqs = []

    for chunk in chunks:
        num_questions = calculate_num_questions(chunk, config.WORDS_PER_QUESTION)
        mcq_text = generate_mcqs(chunk, num_questions)
        if mcq_text:
            all_mcqs.append(mcq_text)

    combined_mcq_text = "\n".join(all_mcqs)
    corrected_mcq_text = verify_and_correct_mcqs(combined_mcq_text)

    if corrected_mcq_text:
        # --- Updated CSV Formatting Logic ---
        mcq_pattern = re.compile(r'\*\*QID:(\d+-\d+)\*\*\s*(.*?)\*\*Correct Answer:\s*([a-e])\)\s*(.*?)\*\*', re.DOTALL)
        matches = mcq_pattern.findall(corrected_mcq_text)

        formatted_mcqs = []
        for qid, mcq_content, correct_letter, correct_answer in matches:
            # Remove ** from QID and MCQ content here
            clean_qid = qid.strip()
            clean_mcq_content = mcq_content.replace('**', '').strip() # Strip **
            formatted_mcqs.append({
                "QID": clean_qid,
                "MCQ": clean_mcq_content,
                "CorrectAnswer": f"{correct_letter}) {correct_answer.strip()}"
            })
        # --- End Updated CSV Formatting Logic ---

        if formatted_mcqs:
            df = pd.DataFrame(formatted_mcqs)
            df.to_csv(output_csv_path, index=False)
            return True
        else:
            print("No MCQs were generated or verified.")
            return False
    else:
        print("MCQ verification and correction failed.")
        return False