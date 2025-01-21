import google.generativeai as genai
import PyPDF2
import re
import spacy
from nltk.stem import PorterStemmer
import json


def configure_gemini_api():
    """
    Configures the Google Gemini API using the API key from environment variables.
    """
    api_key = "PUT YOUR API KEY HERE"
    if not api_key:
        print("Google Gemini API key not found. Please set the 'GOOGLE_GEMINI_API_KEY' environment variable.")
        raise EnvironmentError("GOOGLE_GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    print("Google Gemini API configured successfully.")

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """

    if not pdf_path:  # Check if the path is empty or None
        return None

    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return ""


# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Mapping of month abbreviations to full names
month_mapping = {
    "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April",
    "May": "May", "Jun": "June", "Jul": "July", "Aug": "August",
    "Sep": "September", "Oct": "October", "Nov": "November", "Dec": "December"
}

def normalize_months(text):
    """
    Normalizes abbreviated month names to their full forms.
    """
    pattern = r'\b(' + '|'.join(month_mapping.keys()) + r')\b'
    return re.sub(pattern, lambda x: month_mapping[x.group()], text)

def clean_text(text):
    """
    Cleans text using spaCy, removing stopwords, special characters, and normalizing specific terms to base forms.
    Retains the original verb forms unless specified in the stemming process.
    """
    # Initialize the stemmer
    stemmer = PorterStemmer()

    # 1) Normalize month abbreviations
    text = normalize_months(text)

    # 2) Remove URLs
    text = re.sub(r"http\S+", "", text)  # Remove http/https links
    text = re.sub(r"www\.\S+", "", text)  # Remove www. links

    # 3) Remove unwanted terms (LinkedIn, GitHub, etc.)
    text = re.sub(r"\b(linkedin|github|envel|obile|alt)\b[a-z]*", "", text, flags=re.IGNORECASE)

    # 4) Extract emails & phone numbers
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone_numbers = re.findall(r"\+?\d[\d -]{7,}\d", text)

    # Temporarily replace emails and phone numbers with placeholders
    text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "EMAIL_PLACEHOLDER", text)
    text = re.sub(r"\+?\d[\d -]{7,}\d", "PHONE_PLACEHOLDER", text)

    # 5) Remove special characters (except placeholders)
    text = re.sub(r"[^a-zA-Z0-9\s@.]", " ", text)

    # Restore the actual emails & phone numbers
    for email in emails:
        text = text.replace("EMAIL_PLACEHOLDER", email, 1)
    for phone in phone_numbers:
        text = text.replace("PHONE_PLACEHOLDER", phone, 1)

    # 6) Process text with spaCy
    doc = nlp(text.lower())

    # Define custom stopwords
    custom_stopwords = {"e.g.", "key", "requirement", "s", "or", "a", "in"}

    filtered_tokens = []

    for token in doc:
        # Keep named entity tokens as-is
        if token.ent_type_:
            candidate = token.text
        else:
            # For all other tokens, use stemmer to normalize specific terms
            candidate = token.text if token.is_alpha else token.text

        # Filtering conditions:
        if token.is_stop:  # Remove stopwords
            continue
        if candidate in custom_stopwords:  # Remove custom stopwords
            continue
        if len(candidate) == 1:  # Remove single-letter tokens
            continue
        if not candidate.isalnum():  # Remove non-alphanumeric tokens
            continue

        # Apply stemming for further normalization
        candidate = stemmer.stem(candidate)

        filtered_tokens.append(candidate)

    # 7) Return the cleaned text
    return " ".join(filtered_tokens)

def score_resume_format(resume_text, formatting_rules):
    """Scores a resume based on defined formatting rules.

    Args:
        resume_text (str): The text content of the resume.
        formatting_rules (dict): A dictionary specifying formatting rules and weights.

    Returns:
        dict: A dictionary containing the formatting score, reasons, and individual rule scores.
    """

    score = 100  # Start with a perfect score
    reasons = []
    rule_scores = {}
    header_weight = 100/3 # Weight for each header

    for rule_name, rule_config in formatting_rules.items():
      rule_score = 0
      if rule_name == "section_headers":
          headers = rule_config["headers"]
          for header in headers:
            if header == "education":
              pattern = re.compile(rf"\b{header}\b", re.IGNORECASE)
              if not pattern.search(resume_text):
                score -= header_weight
                reasons.append(f"Missing required header: {header}")
              else:
                rule_score += header_weight
            elif "skills" in header.lower():
              pattern = re.compile(r"\b\w*skills\w*\b", re.IGNORECASE)
              if not pattern.search(resume_text):
                score -= header_weight
                reasons.append(f"Missing required header containing the word: 'skills'")
              else:
                rule_score += header_weight

            elif "experience" in header.lower():
              pattern = re.compile(r"\b\w*experience\w*\b", re.IGNORECASE)
              if not pattern.search(resume_text):
                score -= header_weight
                reasons.append(f"Missing required header containing the word: 'experience'")
              else:
                 rule_score += header_weight
      rule_scores[rule_name] = rule_score

    model = genai.GenerativeModel('gemini-pro')
    # prompt = f"check if they are following STAR method in {resume_text}"
    prompt = f"if they have followed STAR method in {resume_text}, say yes, if not say no. only say yes or no."
    response = model.generate_content(prompt)

    if resume_text and response and response.text:
        if response.text.lower() == "yes":
            star_score = 100
        else:
            star_score = 0

    total_score_formatting = (star_score + score) / 2
    total_score_formatting_normalized = max(0, min(100, total_score_formatting))  # Ensure score is between 0 and 100

    return {
      "total_score_formatting": total_score_formatting_normalized,
      "star_score": star_score,
      "heading_score": score,
      "missing_headings": reasons
    }

def analyze_resume(resume_text, job_description_text, formatting_rules):
    """
    Analyzes the alignment of a resume with a job description and its formatting.

    Args:
        resume_text (str): Text from the resume.
        job_description_text (str): Text from the job description.
        formatting_rules (dict): Rules for formatting scoring.

    Returns:
        dict: Analysis results, including score, matched keywords, and formatting information.
    """
    # Clean the texts
    resume_text_cleaned = clean_text(resume_text)



    # job_description_text = clean_text(job_description_text)

    # ------ Gemini Prompt to extract Keywords from the Job Description -------
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"find the key words in {job_description_text}. do not add additional words."
    response = model.generate_content(prompt)
    if response and response.text:
        job_keywords = set(clean_text(response.text).split())
    else:
        job_keywords = set(job_description_text.split())

    # print("job: ", job_keywords)
    resume_keywords = set(resume_text_cleaned.split())



    # Find matches
    matched_keywords = job_keywords & resume_keywords
    match_score = len(matched_keywords) / len(job_keywords) * 100 if job_keywords else 0

    # print("resume: ", resume_keywords)
    # Score the resume formatting
    formatting_score_data = score_resume_format(resume_text, formatting_rules)

    # Combine scores with weights (e.g., 70% match score, 30% formatting score)
    final_score = (0.70 * match_score) + (0.30 * formatting_score_data["total_score_formatting"])
    star_score = formatting_score_data["star_score"]
    heading_score = formatting_score_data["heading_score"]
    missing_headings = formatting_score_data["missing_headings"]

    if list(matched_keywords):
        model1 = genai.GenerativeModel('gemini-pro')
        prompt1 = f"{matched_keywords} contains the matched keywords in a resume. write a sentence for the user saying these words are matched. if the words have miss spelling problems, fix them and do not have duplicate words."
        response1 = model1.generate_content(prompt1)
        match_output = response1.text
    else:
        match_output = None


    missing_keywords = job_keywords - matched_keywords

    if list(missing_keywords):
        model2 = genai.GenerativeModel('gemini-pro')
        prompt2 = f"{missing_keywords} contains the missing words in a resume. write a sentence for the user saying these words are missing."
        response2 = model2.generate_content(prompt2)
        missing_output = response2.text
    else:
        missing_output = None


    return {
        "match_score": match_score,
        "matched_keywords": match_output,
        "missing_keywords": missing_output,
        "total_score_formatting": formatting_score_data["total_score_formatting"],
        "final_score": final_score,
        "star_score": star_score,
        "heading_score": heading_score,
        "missing_headings": missing_headings,
        "job_keywords": job_keywords,
        "resume_keywords": resume_keywords,

    }



def extract_resume_info(text):
    """
    Cleans text using spaCy, removing stopwords, special characters, bullet points,
    and normalizing with lemmatization. Retains numbers, normalizes months,
    removes URLs, and preserves named entities.
    """
    # Step 1: Normalize months
    text = normalize_months(text)

    # Step 2: Remove URLs
    text = re.sub(r"http\S+", "", text)  # Remove URLs starting with http or https
    text = re.sub(r"www\.\S+", "", text)  # Remove URLs starting with www

    # Step 3: Remove bullet points and unnecessary symbols
    text = re.sub(r"[\u2022•●▪♦❖▶■□]", "", text)  # Remove common bullet points
    text = re.sub(r"[^\w\s]", "", text)  # Remove special characters except spaces and word characters

    # Step 4: Process text with spaCy
    doc = nlp(text.lower())

    # Step 5: Filter tokens
    filtered_words = []
    for token in doc:
        # Keep named entities, numbers, or words that are not stopwords
        if token.ent_type_ or not token.is_stop or token.is_digit or token.text.isalnum():
            filtered_words.append(token.lemma_)  # Use lemma for normalization

    # Step 6: Return cleaned text
    return " ".join(filtered_words)

def parse_resume_to_json(text):
    # Helper function to extract specific fields from text
    def extract_field(pattern, text, default=""):
        """
        Extracts the first match for the given pattern from the text.
        """
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else default

    # Extract basic information
    name = extract_field(r"^(.*?)\n", text)
    location = ""
    phone = extract_field(r"(\+?\d[\d\s\-\(\)]+)", text)
    email = extract_field(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text)
    linkedin = extract_field(r"linkedin\S*(\S+)", text)
    github = extract_field(r"github\S*(\S+)", text)

    # Extract sections
    summary_pattern = r"education\n(.*?)technical skill"
    summary = re.findall(r"\u2022?(.*?)(?:\.|\n)", extract_field(summary_pattern, text))

    skills_pattern = r"technical skill\n(.*?)research experience"
    skills_text = extract_field(skills_pattern, text)
    skills = re.split(r",|\n|\s\u2022\s", skills_text)
    skills = [skill.strip() for skill in skills if skill.strip()]

    education_pattern = r"education\n(.*?)research experience"
    education_text = extract_field(education_pattern, text)
    education_entries = re.split(r"\n\n", education_text)

    education = []
    for entry in education_entries:
        institution = extract_field(r"^(.*?)\n", entry)
        degree = extract_field(r"degree\n(.*?)\n", entry)
        years = extract_field(r"\b(\d{4}\s*-\s*\d{4}|\d{4}\s*-\s*present|\d{4})\b", entry)
        location = extract_field(r",\s*(.*?)\n", entry)
        details = re.findall(r"\u2022\s*(.*?)\n", entry)
        education.append({
            "institution": institution,
            "degree": degree,
            "years": years,
            "location": location,
            "details": details
        })

    experience_pattern = r"research experience\n(.*?)additional activity"
    experience_text = extract_field(experience_pattern, text)
    experience_entries = re.split(r"\n\n", experience_text)

    experience = []
    for entry in experience_entries:
        position = extract_field(r"^(.*?)\n", entry)
        company = extract_field(r"\n\u2022\s*(.*?)\n", entry)
        years = extract_field(r"\b(\d{4}\s*-\s*\d{4}|\d{4}\s*-\s*present|\d{4})\b", entry)
        location = extract_field(r",\s*(.*?)\n", entry)
        details = re.findall(r"\u2022\s*(.*?)\n", entry)
        experience.append({
            "position": position,
            "company": company,
            "years": years,
            "location": location,
            "details": details
        })

    # Construct the JSON output
    resume_data = {
        "name": name,
        "location": location,
        "phone": phone,
        "email": email,
        "linkedin": linkedin,
        "github": github,
        "summary": summary,
        "skills": skills,
        "education": education,
        "experience": experience
    }

    return resume_data

def json_creater(info):

    desired_json= {
    "name": "",
    "location": "",
    "phone": "",
    "email": "",
    "linkedin": "",
    "github": "",
    "summary": ["", "", "", "", ""],
    "skills": ["", "", "", "", "", ""],
    "education": [
        {
        "institution": "",
        "degree": "",
        "years": "",
        "location": "",
        "details": [""]
        },
        {
        "institution": "",
        "degree": "",
        "years": "",
        "location": "",
        "details": ["", ""]
        }
    ],
    "experience": [
        {
        "position": "",
        "company": "",
        "years": "",
        "location": "",
        "details": ["", "", "", "", "", ""]
        },
        {
        "position": "",
        "company": "",
        "years": "",
        "location": "",
        "details": ["", "", ""]
        },
        {
        "position": "",
        "company": "",
        "years": "",
        "location": "",
        "details": ["", "", ""]
        }
    ]
    }

    model = genai.GenerativeModel('gemini-pro')
    prompt = f"{info} contains information of a resume. write it in the format of {desired_json}."
    response = model.generate_content(prompt)
    info_output = response.text
    print(info_output)
    return info_output

def main():
    """
    Main function to process resumes and job descriptions.
    """
    # Configure the Gemini API
    configure_gemini_api()

     # Define formatting rules
    formatting_rules = {
        "section_headers": {
            "headers": ["skills", "experience", "education"],
            "weight": 15,
        }
    }

    resume_text = None
    job_description_text = None
    while not resume_text:
        # Get inputs
        resume_path = input("Enter the path to the resume PDF: ")

        # Process resume
        resume_text = extract_text_from_pdf(resume_path)


    while not job_description_text:
        # Get inputs
        job_description_input = input("Enter the job description (or type 'pdf' to upload a PDF): ")

        # Process job description
        if job_description_input.lower() == "pdf":
            job_description_path = input("Enter the path to the job description PDF: ")
            job_description_text = extract_text_from_pdf(job_description_path)
        else:
            job_description_text = job_description_input


    # Analyze resume
    analysis = analyze_resume(resume_text, job_description_text, formatting_rules)

    # print("first resume text: ", resume_text)

    # Display results
    print("\nResume Analysis Results:")
    print(f"Match Score: {analysis['match_score']} %")
    if analysis['matched_keywords'] != None:
        print(f"Matched Keywords: {analysis['matched_keywords']}")
    if analysis['missing_keywords'] != None:
        print(f"Missing Keywords: {analysis['missing_keywords']}")
    print(f"Formatting Score: {analysis['total_score_formatting']} % containnig Headings Score: {analysis['heading_score']} % and Star Score: {analysis['star_score']} %")
    if analysis['missing_headings']:
        print(f"Missing headings: {analysis['missing_headings']}")
    print(f"Final Score: {analysis['final_score']} %")


    # Print the JSON output
    # print(json.dumps(info_output, indent=4))


if __name__ == "__main__":
    main()
