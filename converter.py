import pandas as pd
from docxtpl import DocxTemplate
import re
import os

def csv_to_docx(csv_path, template_path, output_docx_path, lecture_name):
    """Converts a CSV to DOCX using a DocxTemplate."""
    try:
        df = pd.read_csv(csv_path)
        doc = DocxTemplate(template_path)

        # Prepare context data for the template
        context = {
            'lecture_name': lecture_name,
            'mcqs': []  # List to hold MCQ data
        }

        for _, row in df.iterrows():
             # Extract Answer Options, and question
            mcq_lines = row['MCQ'].split('\n')
            question_stem = []
            answer_choices = {} # Use dict

            in_answers = False
            for line in mcq_lines:
                line = line.strip()
                if not line:  # Skip empty lines
                   continue
                if line.startswith(('a)', 'b)', 'c)', 'd)', 'e)')):
                    in_answers = True
                    # Use regex to associate option letter with content
                    match = re.match(r'([a-e])\)\s*(.*)', line)
                    if match:
                        letter, content = match.groups()
                        answer_choices[letter] = content.strip()
                elif in_answers: #Handles edge cases
                  match = re.match(r'([a-e])\)\s*(.*)', line)
                  if match:
                    letter, content = match.groups()
                    answer_choices[letter] = content.strip()
                else:
                    question_stem.append(line)

            # Add question data to context
            mcq_data = {
                'qid': row['QID'],
                'question': ' '.join(question_stem),
                'a': answer_choices.get('a', ''),  # Get answer 'a', default to empty string if not found
                'b': answer_choices.get('b', ''),
                'c': answer_choices.get('c', ''),
                'd': answer_choices.get('d', ''),
                'e': answer_choices.get('e', ''),
                'correct_answer': f"Correct Answer: {row['CorrectAnswer']}"
            }
            context['mcqs'].append(mcq_data)

        doc.render(context)  # Render the template with the context
        doc.save(output_docx_path)

    except FileNotFoundError:
        print(f"Error: CSV file or template file not found.")
    except Exception as e:
        print(f"An error occurred during CSV to DOCX conversion: {e}")