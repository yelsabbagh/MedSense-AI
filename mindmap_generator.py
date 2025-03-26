# mindmap_generator.py

import google.generativeai as genai
import config
import os
import time
import json
import uuid
import zipfile
import traceback
from google.api_core.exceptions import ResourceExhausted

# --- System Instruction ---
SYSTEM_INSTRUCTION_MINDMAP = """You are an expert AI assistant specializing in structuring text content into hierarchical mind maps. Analyze the input text and generate a detailed JSON representation suitable for creating a mind map, focusing on logical hierarchy and key information."""

# --- DETAILED Styling Constants (Derived from your example content.json) ---

# Style for the Central Topic (Root)
ROOT_STYLE_PROPS = {
    "fo:font-family": "NeverMind", "fo:font-size": "28pt", "fo:font-weight": "600",
    "fo:color": "#ffffff", "svg:fill": "#046562", "shape-class": "org.xmind.topicShape.roundedRect",
    "line-color": "#046562", "border-line-width": "0pt"
}

# Style for Main Topics (Level 1 attached to root) - Teal Fill
MAIN_TOPIC_STYLE_PROPS = {
    "fo:font-family": "NeverMind", "fo:font-size": "24pt", "fo:font-weight": "600", # Increased size from example
    "fo:color": "#FFFFFFFF", "svg:fill": "#06AFA9", "shape-class": "org.xmind.topicShape.roundedRect",
    "line-color": "#046562", "border-line-width": "2", "border-line-color": "#046562", # Added border like example
    "line-class": "org.xmind.branchConnection.roundedElbow", # Elbow connection
    "border-line-pattern": "handdrawn-solid" # Example pattern
}

# Style for Level 2 Subtopics (e.g., under 'Triad') - Teal Fill like Level 1
SUB_TOPIC_L2_STYLE_PROPS = {
    "fo:font-family": "NeverMind", "fo:font-size": "20pt", "fo:font-weight": "700",
    "fo:color": "#046562", "svg:fill": "#A6FEF500", # Transparent Light Teal? Or solid #A6FEF5? Let's try solid
    "shape-class": "org.xmind.topicShape.roundedRect",
    "line-color": "#046562", "border-line-width": "2", "border-line-color": "#046562",
    "line-class": "org.xmind.branchConnection.roundedfold", # Fold connection
    "border-line-pattern": "dash"
}

# Style for Level 3+ Subtopics - Alternating Colors (Example had Greenish fill too)
SUB_TOPIC_L3_STYLE_A_PROPS = { # Light Teal transparent fill
    "fo:font-family": "NeverMind", "fo:font-size": "18pt", "fo:font-weight": "700",
    "fo:color": "#046562", "svg:fill": "#A6FEF500", # Transparent Light Teal
    "shape-class": "org.xmind.topicShape.roundedRect",
    "line-color": "#046562", "border-line-width": "2", "border-line-color": "#046562",
    "line-class": "org.xmind.branchConnection.roundedfold",
    "border-line-pattern": "dash"
}
SUB_TOPIC_L3_STYLE_B_PROPS = { # Light Greenish transparent fill
    "fo:font-family": "NeverMind", "fo:font-size": "18pt", "fo:font-weight": "700",
    "fo:color": "#046562", "svg:fill": "#2CD55166", # Transparent Light Greenish
    "shape-class": "org.xmind.topicShape.roundedRect",
    "line-color": "#046562", "border-line-width": "2", "border-line-color": "#046562",
    "line-class": "org.xmind.branchConnection.roundedfold",
    "border-line-pattern": "dash"
}

# Style for Table Header (e.g., 'Type 1' under 'Types')
TABLE_HEADER_STYLE_PROPS = {
    "fo:font-family": "NeverMind", "fo:font-size": "24pt", "fo:font-weight": "600",
    "fo:color": "#000000FF", "svg:fill": "#06AFA94D", # Semi-transparent Teal
    "shape-class": "org.xmind.topicShape.roundedRect",
    "line-color": "#046562", "border-line-width": "2", "border-line-color": "#046562",
    "line-class": "org.xmind.branchConnection.roundedfold",
    "border-line-pattern": "handdrawn-solid"
}

# Style for Table Cells (e.g., 'ANA & ASMA' under 'Type 1') - Can alternate like L3
TABLE_CELL_STYLE_A_PROPS = SUB_TOPIC_L3_STYLE_A_PROPS # Reuse L3 Style A
TABLE_CELL_STYLE_B_PROPS = SUB_TOPIC_L3_STYLE_B_PROPS # Reuse L3 Style B

# Style for Detached Topics (Floating) - Example had different style
DETACHED_TOPIC_STYLE_PROPS = {
    "fo:font-family": "NeverMind","fo:font-size": "30pt","fo:font-weight": "600",
    "fo:color": "#ffffff","svg:fill": "#8EDDF9FF", # Light Blue fill
    "shape-class": "org.xmind.topicShape.roundedRect",
    "line-color": "#046562","border-line-color": "#00526BFF","border-line-width": "2",
    "border-line-pattern": "handdrawn-solid"
}

# --- Gemini API Call with Retry (Keep as before) ---
def generate_with_retry(prompt,system_instruction, retries=5, delay=5):
    # ... (No changes needed here) ...
    genai.configure(api_key=config.API_KEY)
    json_generation_config = config.generation_config.copy()
    json_generation_config["response_mime_type"] = "application/json"
    model = genai.GenerativeModel(
        model_name=config.GEMINI_MODEL,
        generation_config=json_generation_config,
        safety_settings=config.safety_settings,
        system_instruction=system_instruction
    )
    for attempt in range(retries):
        try:
            # ... (Rest of the retry logic) ...
            print(f"Mindmap Gen: Sending request to Gemini (attempt {attempt + 1})...")
            response = model.generate_content(prompt)
            print("Mindmap Gen: Received response from Gemini.")
            return response.text
        except ResourceExhausted as e:
            print(f"Mindmap Gen: Rate limit exceeded, retrying in {delay}s... ({attempt + 1}/{retries})")
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            print(f"Mindmap Gen: An unexpected error occurred during Gemini call: {e}")
            # ... (Error feedback logging) ...
            if attempt < retries - 1:
                print(f"Mindmap Gen: Retrying after error in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                print("Mindmap Gen: Maximum retries reached or fatal error.")
                traceback.print_exc()
                raise e
    print("Mindmap Gen: Max retries reached after ResourceExhausted errors.")
    return None

# --- UPDATED: Gemini Prompt to include Hint ---
def generate_mind_map_json_structure(text):
    """Asks Gemini to generate a DETAILED hierarchical JSON structure WITH HINTS."""
    print("Mindmap Gen: Preparing Gemini prompt for DETAILED JSON structure with HINTS...")
    prompt = f"""
Analyze the following medical text and generate a **detailed** and hierarchical mind map structure as a JSON object. Capture important nuances and supporting information.

**Rules for Content and Hierarchy:**
1.  **Central Topic:** Root object represents the overarching theme.
2.  **Main Branches:** Identify all relevant major sections/concepts.
3.  **Sub-Branches & Depth:** Include supporting details, examples, classifications, mechanisms, data points, etc., aiming for 2-4 levels of depth where text provides detail.
4.  **Completeness:** Represent core info and supporting details comprehensively.
5.  **Conciseness:** Use concise but specific phrases for titles (3-10 words).
6.  **Logical Flow:** Structure children logically.

**Rules for Output Format:**
1.  Each JSON object (node) MUST have:
    *   `"title"`: The concise string.
    *   `"children"`: An array of child JSON objects (`[]` if none).
    *   **(Optional Hint):** If a node represents a clear comparison or distinct classification (like comparing Type 1 vs Type 2, or different drug classes side-by-side), add a field `"hint": "comparison_table"` to that node's JSON object. Do **not** add hints for simple lists or standard subtopics.
2.  Output **ONLY** the JSON object (`{{...}}`). No extra text or markdown.

**Example with Hint:**
```json
{{
  "title": "Autoimmune Hepatitis (AIH)",
  "children": [
    {{ "title": "Triad", "children": [...] }},
    {{ "title": "Epidemiology", "children": [...] }},
    {{
      "title": "Types of AIH",
      "hint": "comparison_table", // Hint added here
      "children": [
        {{
          "title": "Type 1",
          "children": [
            {{"title": "Antibodies: ANA & ASMA", "children": []}},
            {{"title": "Severity: Mild-Moderate", "children": []}},
            {{"title": "Prognosis: Generally Good", "children": []}}
          ]
        }},
        {{
          "title": "Type 2",
          "children": [
            {{"title": "Antibodies: LKM-1 & LC-1", "children": []}},
            {{"title": "Severity: Often Severe", "children": []}},
            {{"title": "Prognosis: Poorer, relapse common", "children": []}}
          ]
        }}
      ]
    }}
  ]
}}
```

**Input Text:**
---
{text}
---

**Generate the detailed JSON structure with hints:**
"""
    try:
        json_string = generate_with_retry(prompt, SYSTEM_INSTRUCTION_MINDMAP)
        if json_string:
            print("Mindmap Gen: Parsing Gemini JSON response...")
            # Clean potential markdown formatting
            if json_string.strip().startswith("```json"):
                 json_string = json_string.strip()[7:-3].strip()
            elif json_string.strip().startswith("```"):
                 json_string = json_string.strip()[3:-3].strip()

            data = json.loads(json_string)
            print("Mindmap Gen: JSON structure parsed successfully.")
            return data
        else:
            print("Mindmap Gen: Failed to get response from Gemini.")
            return None
    except json.JSONDecodeError as e:
        print(f"Mindmap Gen: ERROR - Failed to decode JSON response from Gemini: {e}")
        print("--- Gemini Response Text (raw) ---")
        print(json_string)
        print("----------------------------------")
        return None
    except Exception as e:
        print(f"Mindmap Gen: An unexpected error occurred generating/parsing structure: {e}")
        traceback.print_exc()
        return None


# --- UPDATED: Recursive function to build XMind topic JSON with advanced styling/structure ---
def build_topic_json(node_data, level=0, parent_structure=None, sibling_index=0):
    """
    Recursively builds the XMind topic JSON structure.
    Applies styling and structureClass based on level, hints, and parent structure.
    """
    topic_id = str(uuid.uuid4())
    style_id = str(uuid.uuid4()) # Each topic gets a unique style ID

    # --- Determine Style and Structure ---
    style_props = {}
    structure_class = "org.xmind.ui.logic.right" # Default

    # Get hint if present
    hint = node_data.get("hint")

    is_table_header = parent_structure == "org.xmind.ui.treetable"
    is_table_cell = parent_structure == "org.xmind.ui.treetable.toptitle"

    if level == 0:
        style_props = ROOT_STYLE_PROPS.copy()
        structure_class = "org.xmind.ui.logic.right" # Root usually logic right/left/map
    elif is_table_header:
         style_props = TABLE_HEADER_STYLE_PROPS.copy()
         structure_class = "org.xmind.ui.treetable.toptitle" # Children of treetable are toptitles
    elif is_table_cell:
         # Alternate styles for table cells
         style_props = (TABLE_CELL_STYLE_A_PROPS if sibling_index % 2 == 0 else TABLE_CELL_STYLE_B_PROPS).copy()
         structure_class = "org.xmind.ui.logic.right" # Cells branch normally
    elif level == 1:
        style_props = MAIN_TOPIC_STYLE_PROPS.copy()
        # Check hint for potential table structure
        if hint == "comparison_table":
            structure_class = "org.xmind.ui.treetable"
            print(f"Mindmap Build: Applying 'treetable' structure to '{node_data.get('title')}' based on hint.")
        else:
            # Default Level 1 structure (can change based on preference)
             structure_class = "org.xmind.ui.tree.right" # Tree structure for main branches usually looks good
    elif level == 2:
        # Using a specific style like the example's 'Triad' subtopics
        style_props = SUB_TOPIC_L2_STYLE_PROPS.copy()
        structure_class = "org.xmind.ui.logic.right" # Default for L2
        # Could add hint check here too if needed
    else: # Level 3+
        # Alternate styles for deeper levels
        style_props = (SUB_TOPIC_L3_STYLE_A_PROPS if sibling_index % 2 == 0 else SUB_TOPIC_L3_STYLE_B_PROPS).copy()
        structure_class = "org.xmind.ui.logic.right" # Default deeper

    # --- Build Topic ---
    topic = {
        "id": topic_id,
        "class": "topic",
        "title": node_data.get("title", "Untitled"),
        "structureClass": structure_class,
        # Style object is always present
        "style": {
            "id": style_id,
            "properties": style_props
        }
        # We'll add children below
    }

    # --- Recursively Build Children ---
    if "children" in node_data and node_data["children"]:
        topic["children"] = {"attached": []} # Use 'attached' based on example
        for i, child_node in enumerate(node_data["children"]):
            child_topic = build_topic_json(
                child_node,
                level + 1,
                parent_structure=structure_class, # Pass current structure to child
                sibling_index=i # Pass sibling index for alternating styles
            )
            topic["children"]["attached"].append(child_topic)

    return topic


# --- Main function to create the XMind file (Minor change for root structure) ---
def create_mind_map(input_md_path, output_xmind_path):
    """Creates an XMind file (.xmind v8 format) from a Markdown file."""
    print(f"\n--- Starting Mind Map Generation for: {input_md_path} ---")
    try:
        # ... (Read MD text - same as before) ...
        print(f"Mindmap Gen: Reading text from '{input_md_path}'...")
        if not os.path.exists(input_md_path):
             print(f"Mindmap Gen: ERROR - Input Markdown file not found: {input_md_path}")
             return False
        with open(input_md_path, 'r', encoding='utf-8') as f:
            text = f.read()
        if not text.strip():
             print("Mindmap Gen: Warning - Input Markdown file is empty.")
             return False
        print("Mindmap Gen: Text read successfully.")

        # ... (Generate structure with hints - same as before) ...
        print("Mindmap Gen: Generating DETAILED mind map structure with HINTS via Gemini...")
        simplified_structure = generate_mind_map_json_structure(text)
        if simplified_structure is None:
            print("Mindmap Gen: ERROR - Failed to generate detailed mind map structure.")
            return False
        print("Mindmap Gen: Gemini structure generation successful.")

        # ... (Build full content.json using the UPDATED build_topic_json) ...
        print("Mindmap Gen: Building XMind content.json structure...")
        root_topic_json = build_topic_json(simplified_structure, level=0) # Call updated function
        print("Mindmap Gen: content.json structure built.")

        # Prepare sheet and final content data
        sheet_id = str(uuid.uuid4())
        content_json_data = [{
            "id": sheet_id,
            "class": "sheet",
            "title": os.path.splitext(os.path.basename(input_md_path))[0].replace("_extracted",""), # Use filename as title
            "rootTopic": root_topic_json,
            # Add theme reference if needed - borrowing from example
            "theme": {
                 "map":{"id":"08d5d6cc-bb40-42ee-a37e-7a36f529c9e2","properties":{"svg:fill":"#c4fff9","color-list":"#ffffff #c4fff9 #9ceaef #68d8d6 #06AFA9 #046562"}},
                 # Defining other theme parts might ensure consistency if needed
                 "centralTopic":{"id":"cb26246d-38a9-4850-893c-dfb0dd9692e9"},
                 "mainTopic":{"id":"5928d82d-4697-4a7f-850f-cf05458d085f"},
                 "subTopic":{"id":"59bffa34-f626-4d3f-b529-8316cf1706af"},
             }
        }]

        # ... (Create manifest.json - same as before) ...
        manifest_data = {"file-entries": {"content.json": {}, "metadata.json": {}}}

        # ... (Create metadata.json - same as before) ...
        metadata_data = {"creator": {"name": "MedSenseAI_Generator", "version": "1.2"}}

        # ... (Create the .xmind (ZIP) file - same as before) ...
        print(f"Mindmap Gen: Creating XMind file: '{output_xmind_path}'...")
        os.makedirs(os.path.dirname(output_xmind_path), exist_ok=True)
        with zipfile.ZipFile(output_xmind_path, 'w', zipfile.ZIP_DEFLATED) as xmind_zip:
            xmind_zip.writestr('content.json', json.dumps(content_json_data, indent=2).encode('utf-8'))
            xmind_zip.writestr('manifest.json', json.dumps(manifest_data, indent=2).encode('utf-8'))
            xmind_zip.writestr('metadata.json', json.dumps(metadata_data, indent=2).encode('utf-8'))

        print(f"Mindmap Gen: XMind file created successfully: {output_xmind_path}")
        print(f"--- Mind Map Generation Complete for: {input_md_path} ---")
        return True

    except Exception as e:
        print(f"Mindmap Gen: An CRITICAL error occurred during mind map creation: {e}")
        traceback.print_exc()
        return False

# --- Example Usage (Keep as before) ---
# if __name__ == "__main__":
#     # ... (Test code) ...
