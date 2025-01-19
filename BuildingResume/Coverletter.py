import os
import json
import subprocess
import logging
import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader, Template
from pylatexenc.latexencode import utf8tolatex  # Safe LaTeX encoding
import re
from jsonschema import validate, ValidationError
from typing import Any, Dict, List, Union

# File paths
TEX_TEMPLATE_PATH = "templates/cover_letter_template.tex"
OUTPUT_TEX_PATH = "output/generated_cover_letter.tex"
OUTPUT_PDF_PATH = "output/generated_cover_letter.pdf"

# Configure Logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("cover_letter_generation.log"),  # Log to a file
        logging.StreamHandler()  # Also log to console
    ]
)


# Configure Google Gemini API
def configure_gemini_api():
    """Configures Google Gemini API with the API key from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("Google Gemini API key not found in environment variables.")
        raise EnvironmentError("Google Gemini API key is missing.")
    genai.configure(api_key=api_key)
    logging.info("Google Gemini API configured successfully.")


###############################################################################
# **📜 Define JSON Schemas**
###############################################################################
# Schema for Job Themes
job_themes_schema = {
    "type": "object",
    "properties": {
        "key_themes": {
            "type": "array",
            "items": {"type": "string"}
        },
        "responsibilities": {
            "type": "array",
            "items": {"type": "string"}
        },
        "required_skills": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["key_themes", "responsibilities", "required_skills"]
}

# Schema for Final Cover Letter
cover_letter_schema = {
    "type": "object",
    "properties": {
        "applicant_name": {"type": "string"},
        "applicant_email": {"type": "string", "format": "email"},
        "applicant_phone": {"type": "string"},
        "company_name": {"type": "string"},
        "company_location": {"type": "string"},
        "job_title": {"type": "string"},
        "cover_letter_content": {"type": "string"},
    },
    "required": [
        "applicant_name",
        "applicant_email",
        "applicant_phone",
        "company_name",
        "company_location",
        "job_title",
        "cover_letter_content",
    ]
}


###############################################################################
# **🔧 Extract and Validate JSON from AI Response**
###############################################################################
def extract_and_validate_json(text, schema):
    """Extracts and validates JSON from the AI response using the provided schema."""
    try:
        json_match = re.search(r"\{[\s\S]*\}", text, re.DOTALL)  # Match valid JSON block
        if json_match:
            extracted_text = json_match.group(0)
            logging.info("✅ Extracted Raw JSON:\n%s", extracted_text)
            extracted_json = json.loads(extracted_text)  # Ensure valid JSON

            # Validate against the schema
            validate(instance=extracted_json, schema=schema)
            logging.info("✅ JSON Schema validation passed.")

            return extracted_json
        else:
            logging.error("❌ No valid JSON found in AI response.")
            return None
    except json.JSONDecodeError as e:
        logging.error(f"❌ JSON Decoding Failed: {e}\nRaw Response:\n{text}")
        return None
    except ValidationError as e:
        logging.error(f"❌ JSON Schema Validation Failed: {e.message}\nJSON:\n{extracted_text}")
        return None


###############################################################################
# **🔒 Safe LaTeX Character Escaping**
###############################################################################
def escape_latex(s: str) -> str:
    """Escapes LaTeX special characters in a string."""
    return utf8tolatex(s)


def escape_context(context_dict):
    """Recursively escapes all strings in the dictionary for LaTeX compatibility, excluding cover_letter_content."""
    escaped_context = {}
    for key, value in context_dict.items():
        if key == "cover_letter_content":
            # Replace double newlines with two manual line breaks
            formatted_content = value.replace("\n\n", " \\\\ \n").replace("\n", " \\\\ \n")
            escaped_context[key] = formatted_content
        elif isinstance(value, list):
            escaped_context[key] = [
                escape_latex(item) if isinstance(item, str) else escape_context(item) if isinstance(item, dict) else item
                for item in value
            ]
        elif isinstance(value, dict):
            escaped_context[key] = escape_context(value)
        elif isinstance(value, str):
            escaped_context[key] = escape_latex(value)
        else:
            escaped_context[key] = value
    return escaped_context


# def escape_latex(text: str) -> str:
#     """Escapes LaTeX special characters in a string."""
#     # Define LaTeX special characters
#     special_chars = {
#         '&': r'\&',
#         '%': r'\%',
#         '$': r'\$',
#         '#': r'\#',
#         '_': r'\_',
#         '{': r'\{',
#         '}': r'\}',
#         '~': r'\textasciitilde{}',
#         '^': r'\textasciicircum{}',
#         '\\': r'\textbackslash{}',
#     }
#     # Use regex to replace each special character
#     regex = re.compile('|'.join(re.escape(key) for key in special_chars.keys()))
#     return regex.sub(lambda match: special_chars[match.group()], text)
#
#
# def format_cover_letter(content: str) -> str:
#     """
#     Formats the cover letter content by replacing newlines with LaTeX line breaks.
#     Double newlines are treated as paragraph breaks.
#     """
#     # First, escape LaTeX characters
#     escaped_content = escape_latex(content)
#     # Replace double newlines with paragraph breaks
#     escaped_content = re.sub(r'\n{2,}', r'\\\newline\newline ', escaped_content)
#     # Replace single newlines with line breaks
#     escaped_content = re.sub(r'(?<!\\)\\newline', r'\\\\ \n', escaped_content)
#     return escaped_content
#
#
# def escape_context(
#         context_dict: Dict[str, Any],
#         special_keys: List[str] = None
# ) -> Dict[str, Any]:
#     """
#     Recursively escapes all strings in the dictionary for LaTeX compatibility,
#     handling special keys differently if specified.
#
#     Args:
#         context_dict: The input dictionary to process.
#         special_keys: List of keys that require special handling.
#
#     Returns:
#         A new dictionary with escaped strings.
#     """
#     if special_keys is None:
#         special_keys = ["cover_letter_content"]
#
#     def _escape(value: Any) -> Any:
#         if isinstance(value, str):
#             return escape_latex(value)
#         elif isinstance(value, dict):
#             return escape_context(value, special_keys)
#         elif isinstance(value, list):
#             return [_escape(item) for item in value]
#         else:
#             return value
#
#     escaped = {}
#     for key, value in context_dict.items():
#         if key in special_keys and isinstance(value, str):
#             if key == "cover_letter_content":
#                 escaped[key] = format_cover_letter(value)
#             else:
#                 # Handle other special keys if needed
#                 escaped[key] = _escape(value)
#         else:
#             escaped[key] = _escape(value)
#     return escaped


###############################################################################
# **📥 Load JSON Data**
###############################################################################
def load_json(file_path):
    """Loads JSON data from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"File {file_path} not found.")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in {file_path}.")
        return {}


###############################################################################
# **📥 Load Job Description Text**
###############################################################################
def load_text(file_path):
    """Loads text data from a file (Job Description)."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"File {file_path} not found.")
        return "Job description not available."


###############################################################################
# **🤖 Generate Job Themes using Google Gemini**
###############################################################################
def extract_job_themes(job_description):
    """Sends job description to Gemini API to extract key themes."""
    prompt = f"""
    You are an AI assistant specializing in analyzing job descriptions.

    Extract the key themes, responsibilities, and required skills from the following job description.

    **Job Description:**
    {job_description}

    **Output Format (JSON Only, No Additional Text):**
    {{
        "key_themes": ["Theme1", "Theme2", "..."],
        "responsibilities": ["Responsibility1", "Responsibility2", "..."],
        "required_skills": ["Skill1", "Skill2", "..."]
    }}
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        logging.debug("Complete AI Response Object: %s", response)

        if response and response.candidates:
            if not response.candidates[0].content.parts:
                logging.error("❌ AI response has no content parts.")
                return {}
            response_text = response.candidates[0].content.parts[0].text.strip()
            logging.info("✅ Raw AI Response for Job Themes:\n%s", response_text)

            job_themes_json = extract_and_validate_json(response_text, job_themes_schema)
            if job_themes_json:
                return job_themes_json
            else:
                logging.error("❌ AI returned invalid JSON for job themes.")
                return {}
        else:
            logging.error("❌ AI did not return any candidates for job themes.")
            return {}
    except Exception as e:
        logging.error("Error in AI response processing for job themes: %s", e)
        return {}


###############################################################################
# **🤖 Generate Cover Letter JSON using Google Gemini**
###############################################################################
def generate_final_cover_letter(applicant_info, job_description, job_themes):
    """Generates the final cover letter content using applicant info and job themes."""
    prompt = f"""
    You are an AI assistant specializing in generating professional cover letters.

    Given an applicant's information, a full job description, and the key themes extracted from it, **write a compelling and customized cover letter** that includes:

    1. **Applicant's name and contact information** at the top.
    2. **A proper salutation** (e.g., "Dear Hiring Manager" or a specific person's name if available).
    3. **A strong opening paragraph** expressing interest in the role.
    4. **A body section** highlighting relevant experience, skills, and how they align with the job requirements.
    5. **A closing paragraph** expressing enthusiasm and availability for an interview.
    6. **A proper sign-off with the applicant's name**.

    **Applicant Information:**
    {json.dumps(applicant_info, indent=4)}

    **Job Description:**
    {job_description}

    **Extracted Job Themes:**
    {json.dumps(job_themes, indent=4)}

    **Output Format (JSON Only, No Additional Text):**
    {{
        "applicant_name": "{applicant_info.get('name', '')}",
        "applicant_email": "{applicant_info.get('email', '')}",
        "applicant_phone": "{applicant_info.get('phone', '')}",
        "company_name": "{applicant_info.get('company', 'Company Name')}",
        "company_location": "{applicant_info.get('location', 'Location')}",
        "job_title": "{applicant_info.get('job_title', 'Job Title')}",
        "cover_letter_content": "GENERATE COVER LETTER HERE"
    }}

    **Instructions:**
    - Ensure that all newline characters in "cover_letter_content" are represented as `\\n`.
    - Escape all double quotes within the content.
    - The entire JSON should be a single line without actual line breaks.
    """

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        logging.debug("Complete AI Response Object: %s", response)

        # Ensure the response contains valid content
        if response and response.candidates:
            if not response.candidates[0].content.parts:
                logging.error("❌ AI response has no content parts.")
                return {}

            response_text = response.candidates[0].content.parts[0].text.strip()
            logging.info("✅ Raw AI Response for Cover Letter:\n%s", response_text)

            # Extract JSON
            cover_letter_json = extract_and_validate_json(response_text, cover_letter_schema)
            if cover_letter_json:
                # Check if placeholder was replaced
                if cover_letter_json.get("cover_letter_content") == "GENERATE COVER LETTER HERE":
                    logging.error("❌ AI did not generate cover letter content.")
                    return {}
                return cover_letter_json
            else:
                logging.error("❌ AI returned invalid JSON for cover letter.")
                return {}
        else:
            logging.error("❌ AI did not return any candidates for cover letter.")
            return {}
    except Exception as e:
        logging.error("Error in AI response processing for cover letter: %s", e)
        return {}



###############################################################################
# **📝 Generate LaTeX Cover Letter File**
###############################################################################
def generate_tex(cover_letter_data):
    """Generates a LaTeX file for the cover letter using Jinja2 templating."""
    try:
        # Set up Jinja2 environment with custom delimiters to avoid conflicts with LaTeX
        env = Environment(
            loader=FileSystemLoader(os.path.dirname(TEX_TEMPLATE_PATH)),
            block_start_string='<%',
            block_end_string='%>',
            variable_start_string='<<',
            variable_end_string='>>',
            autoescape=False  # Handle escaping manually
        )
        tex_template = env.get_template(os.path.basename(TEX_TEMPLATE_PATH))

        # Escape LaTeX special characters, excluding cover_letter_content
        escaped_data = escape_context(cover_letter_data)

        # Render the LaTeX template with the AI-generated data
        rendered_tex = tex_template.render(escaped_data)

        # Log the rendered LaTeX content for debugging
        logging.debug("Rendered LaTeX Content:\n%s", rendered_tex)

        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)

        # Write LaTeX content to a file
        with open(OUTPUT_TEX_PATH, "w", encoding="utf-8") as output_file:
            output_file.write(rendered_tex)

        logging.info("✅ LaTeX file generated successfully.")
    except Exception as e:
        logging.error("Error generating LaTeX file: %s", e)


###############################################################################
# **📄 Compile LaTeX to PDF**
###############################################################################
def compile_tex_to_pdf():
    """Compiles the LaTeX file to PDF using pdflatex."""
    try:
        command = ["pdflatex", "-interaction=nonstopmode", "-output-directory=output", OUTPUT_TEX_PATH]
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logging.info("✅ Cover letter successfully generated: %s", OUTPUT_PDF_PATH)
    except subprocess.CalledProcessError as e:
        logging.error("❌ LaTeX compilation failed.")
        logging.error("Return Code: %s", e.returncode)
        logging.error("Stdout: %s", e.stdout.decode('utf-8'))
        logging.error("Stderr: %s", e.stderr.decode('utf-8'))


###############################################################################
# **🔄 Main Function**
###############################################################################
def main():
    configure_gemini_api()

    applicant_info = load_json("data/applicant.json")
    job_description = load_text("data/job_description.txt")

    if not applicant_info:
        logging.error("Applicant information is missing or invalid.")
        return

    if not job_description:
        logging.error("Job description is missing or invalid.")
        return

    # Step 1: Extract Job Themes
    job_themes = extract_job_themes(job_description)
    if not job_themes:
        logging.error("Job themes extraction failed.")
        return

    # Step 2: Generate Final Cover Letter Content
    cover_letter_data = generate_final_cover_letter(applicant_info, job_description, job_themes)
    if not cover_letter_data:
        logging.error("Cover letter generation failed.")
        return

    # Step 3: Generate LaTeX and Compile to PDF
    generate_tex(cover_letter_data)
    compile_tex_to_pdf()


if __name__ == "__main__":
    main()
