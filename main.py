import google.generativeai as genai
import PyPDF2
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download stopwords if you haven't already
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')


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

def clean_text(text):
    """
    Cleans text by removing special characters and converting to lowercase.

    Args:
        text (str): Input text.

    Returns:
        str: Cleaned text.
    """
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text.lower()

def score_resume_format(resume_text, formatting_rules):
    """Scores a resume based on defined formatting rules.

    Args:
        resume_text (str): The text content of the resume.
        formatting_rules (dict): A dictionary specifying formatting rules and weights.

    Returns:
        dict: A dictionary containing the formatting score, reasons, and individual rule scores.
    """

    score = 0
    reasons = []
    rule_scores = {}
    total_weight = 0

    for rule_name, rule_config in formatting_rules.items():
        rule_score = 0
        if rule_name == "section_headers":
            headers = rule_config["headers"]
            for header in headers:
                if header == "education":
                    pattern = re.compile(rf"\b{header}\b", re.IGNORECASE)
                    if pattern.search(resume_text):
                        rule_score += rule_config["weight"]
                    else:
                        reasons.append(f"Missing required header: {header}")
                elif "skills" in header.lower():
                    pattern = re.compile(r"\b\w*skills\w*\b", re.IGNORECASE)
                    if pattern.search(resume_text):
                        rule_score += rule_config["weight"]
                    else:
                         reasons.append(f"Missing a required header containing the word 'skills'")

                elif "experience" in header.lower():
                    pattern = re.compile(r"\b\w*experience\w*\b", re.IGNORECASE)
                    if pattern.search(resume_text):
                        rule_score += rule_config["weight"]
                    else:
                         reasons.append(f"Missing a required header containing the word 'experience'")
        score += rule_score
        rule_scores[rule_name] = rule_score
        total_weight = sum([value['weight'] for key, value in formatting_rules.items()])
    
    normalized_score = min(100, (score / total_weight) * 100 if total_weight > 0 else 0)
    return {
      "score": normalized_score,
      "reasons": reasons,
      "rule_scores": rule_scores
    }


TECHNOLOGY_MAPPING = {
    "python": ["pandas", "numpy", "scikit-learn", "django", "flask", "requests", "beautifulsoup4", "matplotlib", "seaborn", "pytest", "unittest"],
    "deep learning": ["pytorch", "tensorflow", "keras", "theano", "caffe", "onnx", "tensorrt", "transformers"],
    "javascript": ["react", "angular", "node.js", "vue.js", "express", "webpack", "babel", "jquery", "typescript"],
    "java": ["spring", "hibernate", "maven", "gradle", "junit", "mockito", "servlet", "jsp"],
    "sql": ["mysql", "postgresql", "sqlite", "oracle", "sql server", "mongodb", "cassandra", "redis"],
    "c++": ["boost", "stl", "qt", "opencv", "cmake"],
    "c#": [".net", "asp.net", "entity framework", "unity", "xamarin"],
    "mobile development": ["android", "ios", "swift", "kotlin", "flutter", "react native", "xamarin"],
    "cloud computing": ["aws", "azure", "google cloud", "docker", "kubernetes", "lambda", "ecs", "gke", "ec2"],
    "devops": ["jenkins", "gitlab ci", "circleci", "ansible", "terraform", "chef", "puppet", "prometheus", "grafana", "kubernetes", "docker"],
    "data visualization": ["tableau", "power bi", "d3.js", "plotly"],
    "testing": ["selenium", "junit", "pytest", "cypress", "mocha", "jest"],
    "api": ["rest", "graphql", "soap"],
    "machine learning": ["scikit-learn", "xgboost", "lightgbm", "catboost"],
    "frontend": ["html", "css", "javascript", "react", "angular", "vue.js"],
    "backend": ["node.js", "java", "python", "php", "ruby", "go", "c#"],
    "databases": ["mysql", "postgresql", "mongodb", "cassandra", "redis", "oracle", "sql server"],
    "version control": ["git", "github", "gitlab", "bitbucket"],
    "operating system": ["linux", "windows", "macos"]
}


def get_related_technologies(keyword):
  """Returns related technologies of the given key word"""
  related = []
  for key, value in TECHNOLOGY_MAPPING.items():
    if keyword == key:
      related += value
  return related


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
    job_description_text = clean_text(job_description_text)

    # ------ Gemini Prompt to extract Keywords from the Job Description -------
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"extract the key skills and requirements from this job description: {job_description_text}"
    response = model.generate_content(prompt)
    if response and response.text:
        job_keywords = set(clean_text(response.text).split())
    else:
        job_keywords = set(job_description_text.split())

    # Get stop words
    stop_words = set(stopwords.words('english'))

    # Tokenize and remove stop words from job keywords
    filtered_job_keywords = set(
        word for word in job_keywords if word not in stop_words
    )
     #Expand keywords to include related technologies
    expanded_job_keywords = set()
    for keyword in filtered_job_keywords:
        expanded_job_keywords.add(keyword)
        expanded_job_keywords.update(get_related_technologies(keyword))

    #Tokenize and remove stop words from resume keywords
    resume_keywords = set(
        word for word in word_tokenize(resume_text_cleaned) if word not in stop_words
    )

    # Find matches
    matched_keywords = expanded_job_keywords & resume_keywords
    match_score = len(matched_keywords) / len(expanded_job_keywords) * 100 if expanded_job_keywords else 0

    # Score the resume formatting
    formatting_score_data = score_resume_format(resume_text, formatting_rules)

    # Combine scores with weights (e.g., 70% match score, 30% formatting score)
    final_score = min(100, 0.70 * match_score + 0.30 * formatting_score_data["score"])

    return {
        "match_score": match_score,
        "matched_keywords": matched_keywords,
        "missing_keywords": expanded_job_keywords - matched_keywords,
        "formatting_score": formatting_score_data["score"],
        "formatting_reasons": formatting_score_data["reasons"],
        "formatting_rule_scores": formatting_score_data["rule_scores"],
        "final_score": final_score
    }


def main():
    """
    Main function to process resumes and job descriptions.
    """
    # Configure the Gemini API
    configure_gemini_api()

     # Define formatting rules
    formatting_rules = {
        "section_headers": {
            "headers": ["education", "skills", "experience"],
            "weight": 100/3,
        }
    }

    # Get inputs
    resume_path = input("Enter the path to the resume PDF: ")
    job_description_input = input("Enter the job description (or type 'pdf' to upload a PDF): ")

    # Process resume
    resume_text = extract_text_from_pdf(resume_path)

    # Process job description
    if job_description_input.lower() == "pdf":
        job_description_path = input("Enter the path to the job description PDF: ")
        job_description_text = extract_text_from_pdf(job_description_path)
    else:
        job_description_text = job_description_input

    # Analyze resume
    analysis = analyze_resume(resume_text, job_description_text, formatting_rules)

    # Display results
    print("\nResume Analysis Results:")
    print(f"Match Score: {analysis['match_score']:.2f}%")
    print(f"Matched Keywords: {', '.join(analysis['matched_keywords'])}")
    print(f"Missing Keywords: {', '.join(analysis['missing_keywords'])}")
    print(f"Formatting Score: {analysis['formatting_score']:.2f}%")
    print(f"Formatting Reasons: {analysis['formatting_reasons']}")
    print(f"Formatting Rule Scores: {analysis['formatting_rule_scores']}")
    print(f"Final Score: {analysis['final_score']:.2f}%")

if __name__ == "__main__":
    main()
