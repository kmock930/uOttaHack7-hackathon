import os
import json
import re
import subprocess
import logging
from typing import Dict, Any

import google.generativeai as genai
from jinja2 import Template
from pylatexenc.latexencode import utf8tolatex

###############################################################################
# 1) Configure Logging
###############################################################################
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("resume_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

###############################################################################
# 2) Configure Google Gemini API
###############################################################################
def configure_gemini_api():
    """
    Configures the Google Gemini API using the API key from environment variables.
    """
    api_key = "AIzaSyCDXa85YsVlRk7qJ_2Hi0nptxUxiRYnHHY"
    if not api_key:
        logger.error("Google Gemini API key not found. Please set the 'GOOGLE_GEMINI_API_KEY' environment variable.")
        raise EnvironmentError("GOOGLE_GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    logger.info("Google Gemini API configured successfully.")

###############################################################################
# 3) Generate Resume JSON
###############################################################################
def generate_resume_json(applicant_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    """
    Calls Google Gemini API to generate a tailored resume JSON object based on the applicant's data and job description.

    Args:
        applicant_data (Dict[str, Any]): The applicant's existing resume data.
        job_description (str): The full text of the job description.

    Returns:
        Dict[str, Any]: A dictionary containing the tailored resume details.
    """
    prompt = f"""
    You are an AI assistant tasked with tailoring a resume based on the applicant's existing resume data and a job description.

    **Applicant's Existing Resume Data:**
    {json.dumps(applicant_data, indent=4)}

    **Job Description:**
    {job_description}

    **Instructions:**
    - Tailor the resume to highlight the most relevant experience, skills, and qualifications that match the job description.
    - Ensure all sections (name, contact, summary, skills, education, experience, projects, certifications, publications) are included.
    - The output should be a well-structured JSON object containing the following fields:
        - name (string)
        - contact (object with location, phone, email, linkedin, github)
        - summary (array of strings)
        - skills (array of strings)
        - education (array of objects with degree, institution, years, location, details)
        - experience (array of objects with position, company, years, location, details)
        - projects (array of objects with title, tech_stack, years, location, details)
        - certifications (array of objects with name, link)
        - publications (array of objects with title, link)
    - Provide only the JSON object without any additional text, explanations, or markdown formatting.
    """

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        answer = response.text.strip()
        logger.info("AI Model Response:\n%s", answer)
    except Exception as e:
        logger.error("Error while generating content from AI model: %s", e)
        raise

    # Extract JSON using regex
    json_str = ""
    json_match = re.search(r'```json\s*(\{.*\})\s*```', answer, re.DOTALL)
    if json_match:
        json_str = json_match.group(1).strip()
        logger.info("Extracted JSON using ```json``` block.")
    else:
        json_match = re.search(r'\{.*\}', answer, re.DOTALL)
        if json_match:
            json_str = json_match.group(0).strip()
            logger.info("Extracted JSON using general braces.")
        else:
            logger.error("No JSON object found in the AI model's response.")
            raise ValueError("No JSON object found in the response.")

    # Attempt to parse the extracted JSON
    try:
        resume_data = json.loads(json_str)
        logger.info("Successfully parsed JSON.")
        return resume_data
    except json.JSONDecodeError as e:
        logger.error("JSON Decode Error: %s", e)
        logger.info("Attempting to clean the JSON string...")

        # Attempt to fix common JSON issues (e.g., missing quotes)
        json_str_fixed = re.sub(r'(\w+):', r'"\1":', json_str)
        try:
            resume_data = json.loads(json_str_fixed)
            logger.info("Successfully parsed cleaned JSON.")
            return resume_data
        except json.JSONDecodeError as e2:
            logger.error("Failed to parse cleaned JSON: %s", e2)
            raise ValueError(f"Unable to parse JSON: {e2}")

###############################################################################
# 4) Safe LaTeX Character Escaping
###############################################################################
def escape_latex(s: str) -> str:
    """
    Escapes LaTeX special characters in a string.

    Args:
        s (str): The input string to escape.

    Returns:
        str: The escaped string safe for LaTeX.
    """
    return utf8tolatex(s)

###############################################################################
# 5) Escape Context Data for LaTeX
###############################################################################
def escape_context(context_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively escapes all strings in the dictionary for LaTeX compatibility.

    Args:
        context_dict (Dict[str, Any]): The dictionary containing resume data.

    Returns:
        Dict[str, Any]: The escaped dictionary.
    """
    escaped_context = {}
    for key, value in context_dict.items():
        if isinstance(value, list):
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

###############################################################################
# 6) LaTeX Resume Template
###############################################################################
latex_template = r"""
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Ensure that generated PDF is machine readable / ATS parsable
\pdfgentounicode=1

%-------------------------
% Custom commands
{% raw %}
\newcommand{\resumeItem}[1]{ \item\small{#1 \vspace{-2pt}} }

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeItemListStart}{\begin{itemize}[leftmargin=*,label={}]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}
{% endraw %}
\setlength{\footskip}{12pt} % Adjusted footskip

\begin{document}

%----------HEADING----------
\begin{center}
    {\Huge \textbf{\scshape {{ name | default("") }} }} \\ \vspace{4pt}

    {% if contact %}
        {% if contact.location or contact.phone or contact.email %}
            {{ contact.location | default("") }}
            {% if contact.phone %} $|$ {{ contact.phone }} {% endif %}
            {% if contact.email %} $|$ \href{mailto:{{ contact.email }}}{\texttt{ {{ contact.email }} }} {% endif %}
            \\ \vspace{4pt}
        {% endif %}

        {% if contact.linkedin or contact.github %}
            {% if contact.linkedin %}
                \href{https://{{ contact.linkedin }}}{\texttt{LinkedIn: {{ contact.linkedin }}}}
            {% endif %}
            {% if contact.github %}
                $|$ \href{https://{{ contact.github }}}{\texttt{GitHub: {{ contact.github }}}}
            {% endif %}
        {% endif %}
    {% endif %}
\end{center}

{% if summary %}
%-----------SUMMARY-----------
\section{Summary}
\resumeItemListStart
{% for item in summary %}
    \resumeItem{ {{ item }} }
{% endfor %}
\resumeItemListEnd
{% endif %}

{% if skills %}
%-----------TECHNICAL SKILLS-----------
\section{Technical Skills}
\resumeItemListStart
{% for skill in skills %}
    \resumeItem{ {{ skill }} }
{% endfor %}
\resumeItemListEnd
{% endif %}

{% if education %}
%-----------EDUCATION-----------
\section{Education}
\resumeItemListStart
{% for edu in education %}
    \resumeSubheading{ {{ edu.degree }} }{ {{ edu.institution }} }{ {{ edu.years }} }{ {{ edu.location }} }
    {% if edu.details %}
    \resumeItemListStart
    {% for detail in edu.details %}
        \resumeItem{ {{ detail }} }
    {% endfor %}
    \resumeItemListEnd
    {% endif %}
{% endfor %}
\resumeItemListEnd
{% endif %}

{% if experience %}
%-----------EXPERIENCE-----------
\section{Experience}
\resumeItemListStart
{% for exp in experience %}
    \resumeSubheading{ {{ exp.position }} }{ {{ exp.company }} }{ {{ exp.years }} }{ {{ exp.location }} }
    {% if exp.details %}
    \resumeItemListStart
    {% for detail in exp.details %}
        \resumeItem{ {{ detail }} }
    {% endfor %}
    \resumeItemListEnd
    {% endif %}
{% endfor %}
\resumeItemListEnd
{% endif %}

{% if projects %}
%-----------PROJECTS-----------
\section{Projects}
\resumeItemListStart
{% for proj in projects %}
    \resumeSubheading{ {{ proj.title }} }{ {{ proj.tech_stack }} }{ {{ proj.years }} }{ {{ proj.location }} }
    {% if proj.details %}
    \resumeItemListStart
    {% for detail in proj.details %}
        \resumeItem{ {{ detail }} }
    {% endfor %}
    \resumeItemListEnd
    {% endif %}
{% endfor %}
\resumeItemListEnd
{% endif %}

{% if certifications %}
%-----------CERTIFICATIONS-----------
\section{Certifications}
\resumeItemListStart
{% for cert in certifications %}
    \resumeItem{ \href{ {{ cert.link }} }{ {{ cert.name }} } }
{% endfor %}
\resumeItemListEnd
{% endif %}

{% if publications %}
%-----------PUBLICATIONS-----------
\section{Publications}
\resumeItemListStart
{% for pub in publications %}
    \resumeItem{ \href{ {{ pub.link }} }{ {{ pub.title }} } }
{% endfor %}
\resumeItemListEnd
{% endif %}

\end{document}
"""

###############################################################################
# 7) Compile LaTeX to PDF
###############################################################################
def compile_latex(tex_filename: str):
    """
    Compiles a LaTeX file into a PDF.

    Args:
        tex_filename (str): The path to the .tex file.

    Returns:
        None
    """
    pdflatex_path = "pdflatex"  # Ensure pdflatex is installed and accessible

    try:
        for i in range(2):  # Run twice for proper references
            result = subprocess.run(
                [pdflatex_path, "-interaction=nonstopmode", tex_filename],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        logger.info("✅ PDF Resume Successfully Generated!")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ LaTeX Compilation Failed: {e}")
        # Attempt to read and display the LaTeX log for debugging
        log_filename = tex_filename.replace(".tex", ".log")
        if os.path.exists(log_filename):
            with open(log_filename, "r", encoding="utf-8") as log_file:
                log_content = log_file.read()
                logger.error("\n--- LaTeX Log ---\n%s\n--- End of Log ---\n", log_content)
        else:
            logger.error("❌ LaTeX log file not found.")

###############################################################################
# 8) Main Function
###############################################################################
def main():
    """
    Main function to generate and compile the tailored LaTeX resume.
    """
    # Applicant's Existing Resume Data
    applicant_data =  {
  "name": "Mahsa Paknejad",
  "location": "",
  "phone": "1 (613) 204-9950",
  "email": "mahsa.paknejad@uottawa.ca",
  "linkedin": "inmahsa-paknejad",
  "github": "mahsaapk",
  "summary": [
    "Obile",
    "With concentration in applied artificial intelligence (AI), GPA: 9.6/10",
    "University of Ottawa, Ottawa, Canada, September 2023 - April 2025 (Expected)",
    "Conduct research focused on autonomous, reliable, scalable, and secure resource management.",
    "Optimize vehicular task offloading in mobile edge computing by employing a custom online dynamic model."
  ],
  "skills": [
    "PyTorch",
    "TensorFlow",
    "Scikit-learn",
    "NumPy",
    "Pandas",
    "C programming",
    "Git",
    "Linux",
    "Simulation of Urban Mobility (SUMO)"
  ],
  "education": [
    {
      "institution": "University of Ottawa, Ottawa, Canada",
      "degree": "Master of Applied Science in Electrical and Computer Engineering",
      "years": "September 2023 - April 2025",
      "location": "",
      "details": ["GPA: 9.6/10"]
    },
    {
      "institution": "Azad University, Tehran, Iran",
      "degree": "Bachelor of Engineering in Computer Engineering with Honors",
      "years": "September 2018 - February 2022",
      "location": "",
      "details": ["GPA: 18.57/20"]
    }
  ],
  "experience": [
    {
      "position": "Digital Content and Communication Chair",
      "company": "IEEE WF-IoT 2024 Website",
      "years": "August 2024 - November 2024",
      "location": "",
      "details": [
        "Managed updates to the IEEE 10th World Forum on the Internet of Things website using HTML and CSS."
      ]
    },
    {
      "position": "Traversal Program Member",
      "company": "Smart Connect Vehicle Innovation Centre",
      "years": "June 2024 - Present",
      "location": "",
      "details": [
        "Training in hard and soft skills, hackathons, internships, international exchanges, and conferences."
      ]
    },
    {
      "position": "Teaching Assistant",
      "company": "University of Ottawa",
      "years": "Fall 2023/2024 & Winter 2024/2025",
      "location": "",
      "details": [
        "Led lab sessions aimed at improving students' practical C and Python programming skills in engineering courses.",
        "Taught computation courses and introductory computer science classes."
      ]
    }
  ]
}



#     job_description_text = """
# Job description
# To be considered, please apply via https://careers-kinaxis.icims.com/jobs/32542/co-op-intern-sales-data-analyst/job?mode=job&iis=SOURCE&iisn=uOttawa
#
# ******************************************************************
#
# This is an external job posting which means that the interview and hiring processes are done outside of the CO-OP Navigator. We post it in the Navigator only to give it visibility. You must therefore apply directly on the employer's website.  If you receive and accept a job offer for this position, please let us know. We need the job number and job title that appears in the co-op portal.
#
# ******************************************************************
#
# Location
#
# This is a hybrid position. You must be in the Ottawa, Canada office, at least three days a week.
#
# About the team
#
# The Intern Sales Data Analysts will gain knowledge of sales processes and hands-on experience in analyzing sales data. It will build a good knowledge foundation for those pursuing a career in data analytics, business intelligence, or sales strategy.
#
# This is a full-time, 4-month position, starting May 2025.
#
# What you will do
#
# Intern Sales Data Analysts will help senior analysts and sales Ops managers in
#
# data collection and cleaning, ensuring the data is accurate.
# performing basic data analysis and analyzing sales trends, patterns, and performance metrics
# creating visual reports and dashboards using PBI or excel
# performing data governance tasks.
# What we are looking for
#
# At least 1-year studies in Business Intelligence, Statistics, Computer Science, Finance, Sales, Market Research (or equivalent)
# Good knowledge of Power BI and Microsoft Excel
# Excellent analytical, quantitative and program-solving skills
# Strong attention to detail
# Good collaborative skills and a positive attitude
# Effective time management and organizational skills
# Familiarity with sales and marketing processes is a plus
#
# Work With Impact: Our platform directly helps companies power the world’s supply chains. We see the results of what we do out in the world every day—when we see store shelves stocked, when medications are available for our loved ones, and so much more.
#
# Work with Fortune 500 Brands: Companies across industries trust us to help them take control of their integrated business planning and digital supply chain. Some of our customers include Ford, Unilever, Yamaha, P&G, Lockheed-Martin, and more.
#
# Social Responsibility at Kinaxis: Our Diversity, Equity, and Inclusion Committee weighs in on hiring practices, talent assessment training materials, and mandatory training on unconscious bias and inclusion fundamentals. Sustainability is key to what we do and we’re committed to net-zero operations strategy for the long term. We are involved in our communities and support causes where we can make the most impact.
#
# People matter at Kinaxis and these are some of the perks and benefits we created for our team:
#
# Flexible vacation and Kinaxis Days (company-wide day off on the last Friday of every month)
# Flexible work options
# Physical and mental well-being programs
# Regularly scheduled virtual fitness classes
# Mentorship programs and training and career development
# Recognition programs and referral rewards
# Hackathons
# For more information, visit the Kinaxis web site at www.kinaxis.com or the company’s blog at http://blog.kinaxis.com.
#
# Kinaxis strongly encourages diverse candidates to apply to our welcoming community. We strive to make our website and application process accessible to any and all users. If you would like to contact us regarding the accessibility of our website or need assistance completing the application process, please contact us at recruitmentprograms@kinaxis.com. This contact information is for accessibility requests only and cannot be used to inquire about the status of applications.
# """
    job_description_text ='''
About the job
Company Overview

At Motorola Solutions, we’re guided by a shared purpose – helping people be their best in the moments that matter – and we live up to our purpose every day by solving for safer. Because people can only be their best when they not only feel safe, but are safe. We’re solving for safer by building the best possible technologies across every part of our safety and security ecosystem. That’s mission-critical communications devices and networks, AI-powered video security & access control and the ability to unite voice, video and data in a single command center view. We’re solving for safer by connecting public safety agencies and enterprises, enabling the collaboration that’s critical to connect those in need with those who can help. The work we do here matters.

Aperçu de l’entreprise

Chez Motorola Solutions, nous sommes guidés par un objectif commun: aider les gens à donner le meilleur d’eux-mêmes dans les moments les plus importants - et nous sommes à la hauteur de notre engagement en créant des solutions sécurisées. Parce que les gens ne peuvent donner le meilleur d’eux-mêmes que lorsqu’ils se sentent en sécurité et qu’ils le sont. Nous créons des solutions sécurisées en développant les meilleures technologies intégrées à travers les écosystèmes de sûreté et de sécurité. Qu’il s’agisse d’appareils et de réseaux de communications essentiels, d’une sécurité vidéo et d’un contrôle d’accès basés sur l’IA ou d’une capacité d’unir la voix, vidéo et les données dans un seul centre de commandement. Nous créons des solutions sécurisées en connectant les agences de sécurité publique et les entreprises, permettant ainsi une collaboration essentielle entre les personnes qui ont besoin d’aide et les personnes pouvant aider. Le travail que nous accomplissons ici est primordial.

Department Overview

Do you want to improve your skills and gain experience in software development and design? Motorola Solutions, the leading supplier of mission-critical communication systems, offers all our Interns on-the-job-experience and insight in the latest technology and solutions. If you are a Software development, Computer Science student or similar you may find an exciting opportunity to accelerate your career with us.

Job Description

We offer a truly international and dynamic working environment and a full spectrum of possibilities. As part of an international engineering team that drives the development of future solutions, you will have the opportunity to collaborate with and learn from experienced professionals, and highly skilled colleagues. You will participate in analyzing data, developing software intended towards software product testing testing and maintaining Continuous Integration - Continuous Development environments.

Qualified Skills:

Have a desire to learn and develop your technical and professional skills. 
Be willing to share your ideas and to challenge the status quo. 
Be a team player. 
Have good communication skills in English as a minimum. 
Have solid programming skills, preferably in C/C++, PHP, JavaScript, Python, Robot Framework. 
Experience with Linux OS and shell scripting is a plus. 
Knowing functional programming is a plus. 
Experience and knowledge of the Agile development process. 
Enjoy creative problem-solving challenges. 
Be a student in Software Development, Computer Science or similar. 

We value the dynamics and fresh ideas that collaboration with students brings. We welcome student projects and internships. At Motorola Solutions we believe in constant career and personal growth in a changing business environment.

Basic Requirements

Pursuing a Bachelor's degree or higher in Computer Science, Computer Engineering or related discipline. 

Travel Requirements

None

Relocation Provided

None

Position Type

Intern

EEO Statement

Motorola Solutions is an Equal Opportunity Employer. All qualified applicants will receive consideration for employment without regard to race, color, religion or belief, sex, sexual orientation, gender identity, national origin, disability, veteran status or any other legally-protected characteristic.

We are proud of our people-first and community-focused culture, empowering every Motorolan to be their most authentic self and to do their best work to deliver on the promise of a safer world. If you’d like to join our team but feel that you don’t quite meet all of the preferred skills, we’d still love to hear why you think you’d be a great addition to our team.

We’re committed to providing an inclusive and accessible recruiting experience for candidates with disabilities, or other physical or mental health conditions. To request an accommodation, please email ohr@motorolasolutions.com.

Motorola Solutions adopte, favorise et promeut les principes de diversité, d’équité et d’inclusion. Nous encourageons et accueillons les candidatures de toutes les personnes qualifiées, quelles que soient leur race, origines ethnique, religion ou croyance, orientation sexuelle, identité et expression sexuelle, statut d’anciens combattants ou tout autre statut protégé par la Loi.

Nous sommes fiers de notre culture axée sur les personnes et les communautés, encourageant ainsi chaque Motorolan d’être la version la plus authentique de lui-même dans ses responsabilités afin de tenir la promesse d’un monde plus sécuritaire.

Si vous souhaitez vous joindre à notre communauté mais croyez que vous ne possédez pas toutes les exigences requises pour le poste convoité, nous aimerions tout de même connaître les raisons pour lesquelles vous pensez être un excellent candidat pour notre équipe.

Nous offrons également des mesures d’adaptation pendant toutes les étapes du processus d’embauche afin de favoriser l’inclusion des personnes vivant avec un handicap physique et/ou mental. Si vous avez besoin de mesures d’adaptation, svp nous faire parvenir un courriel à ohr@motorolasolutions.com.

    '''
    # Step 1: Configure the Google Gemini API
    try:
        configure_gemini_api()
    except EnvironmentError as e:
        logger.error("Environment Error: %s", e)
        return
    except Exception as e:
        logger.error("Unexpected error during API configuration: %s", e)
        return

    # Step 2: Generate Tailored Resume JSON
    try:
        logger.info("Generating tailored resume JSON from applicant data and job description...")
        tailored_resume = generate_resume_json(applicant_data, job_description_text)
    except Exception as e:
        logger.error("Error generating tailored resume JSON: %s", e)
        return

    if not tailored_resume:
        logger.error("Tailored resume JSON is empty. Exiting.")
        return

    # Step 3: Escape LaTeX Special Characters
    try:
        logger.info("Escaping LaTeX special characters in resume data...")
        escaped_resume = escape_context(tailored_resume)
    except Exception as e:
        logger.error("Error escaping LaTeX characters: %s", e)
        return

    # Step 4: Render LaTeX Template with Escaped Data
    try:
        logger.info("Rendering LaTeX template with escaped resume data...")
        template = Template(latex_template)
        filled_latex = template.render(escaped_resume)
    except Exception as e:
        logger.error("Error rendering LaTeX template: %s", e)
        return

    # Step 5: Write Rendered LaTeX to .tex File
    tex_filename = "generated_resume.tex"
    try:
        logger.info(f"Writing rendered LaTeX to {tex_filename}...")
        with open(tex_filename, "w", encoding="utf-8") as f:
            f.write(filled_latex)
    except Exception as e:
        logger.error(f"Error writing LaTeX to file {tex_filename}: %s", e)
        return

    # Step 6: Compile LaTeX to PDF
    try:
        logger.info(f"Compiling {tex_filename} to PDF...")
        compile_latex(tex_filename)
    except Exception as e:
        logger.error(f"Error during LaTeX compilation: {e}")
        return

    logger.info("✅ Resume generation process completed successfully.")

###############################################################################
# 9) Entry Point
###############################################################################
if __name__ == "__main__":
    main()
