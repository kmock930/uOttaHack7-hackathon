import ast
import json
import logging
import os

import resume_evaluator
import Resume
from jinja2 import Environment, FileSystemLoader, Template

from Coverletter import load_json, load_text, extract_job_themes, generate_final_cover_letter, generate_tex, \
    compile_tex_to_pdf

logger = logging.getLogger(__name__)

def process_resume(pdf_path, job_description_text):
    """
    Complete pipeline to extract and structure resume data from a PDF file.

    Args:
        pdf_path (str): Path to the resume PDF file.

    Returns:
        dict: Extracted resume data formatted in JSON.
        :param pdf_path:
        :param job_description_text:
    """

    # Step 1: Extract text from PDF
    extracted_text = resume_evaluator.extract_text_from_pdf(pdf_path)
    if not extracted_text:
        print("Error: Could not extract text from the PDF.")
        return None
    # print("extracted_text:", extracted_text)
    # Step 2: Clean and normalize text
    # cleaned_text = resume_evaluator.extract_resume_info(extracted_text)
    # print("extracted_text:", cleaned_text)
    # Step 3: Parse resume details into structured JSON
    structured_data = resume_evaluator.json_creater(extracted_text)

    print("structured_data:", structured_data)

    # Step 4: Use AI to format the JSON data properly
    original_resume_json = resume_evaluator.json_creater(structured_data)


    #Step 5: Pass resume JSON data together with Job description to Gemini API and return JSON
    new_resume_json = Resume.generate_resume_json(original_resume_json, job_description_text)

    escape_context = Resume.escape_context(new_resume_json)

    TEX_TEMPLATE_PATH = "templates/resume_latex.tex"

    env = Environment(
        loader=FileSystemLoader(os.path.dirname(TEX_TEMPLATE_PATH)),
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='<<',
        variable_end_string='>>',
        autoescape=False  # Handle escaping manually
    )

    tex_template = r"""
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

    template = Template(tex_template)
    filled_latex = template.render(escape_context)

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
        Resume.compile_latex(tex_filename)
    except Exception as e:
        logger.error(f"Error during LaTeX compilation: {e}")
        return

    logger.info("✅ Resume generation process completed successfully.")

def process_cover_letter(pdf_path, job_description_text=None):
    extracted_text = resume_evaluator.extract_text_from_pdf(pdf_path)
    if not extracted_text:
        print("Error: Could not extract text from the PDF.")
        return None

    # Step 3: Parse resume details into structured JSON
    # Ensure json_creater's output is treated as a dictionary
    structured_data = resume_evaluator.json_creater(extracted_text)

    # Debug: Print the raw structured_data
    print("Raw structured_data (from json_creater):", structured_data)

    # If structured_data is not a dictionary, handle the error
    if not isinstance(structured_data, dict):
        logging.error("Structured data is not a valid Python dictionary. Please check json_creater's output.")
        return None

    # Assign applicant_info directly from structured_data (already a dictionary)
    applicant_info = structured_data

    # Job description directly assigned
    job_description = job_description_text

    if not applicant_info:
        logging.error("Applicant information is missing or invalid.")
        return

    if not job_description:
        logging.error("Job description is missing or invalid.")
        return

    # Extract themes and proceed
    job_themes = extract_job_themes(job_description)
    if not job_themes:
        logging.error("Job themes extraction failed.")
        return

    # Generate final cover letter using the correct dictionary format
    cover_letter_data = generate_final_cover_letter(applicant_info, job_description, job_themes)
    if not cover_letter_data:
        logging.error("Cover letter generation failed.")
        return

    generate_tex(cover_letter_data)
    compile_tex_to_pdf()

process_cover_letter("CSYRM.pdf", job_description_text='''

About the job
Type De Rôle

Internship/Co-op

Session De Stage

Summer/Term 3

Lieu De Travail

Toronto, Ontario, Canada

Horaire

37.5

Détails De La Rémunération

$44.000.000 - $48,000.00 CAD

La TD a à cœur d’offrir une rémunération juste et équitable à tous les collègues. Les occasions de croissance et le perfectionnement des compétences sont des caractéristiques essentielles de l’expérience collègue à la TD. Nos politiques et pratiques en matière de rémunération ont été conçues pour permettre aux collègues de progresser dans l’échelle salariale au fil du temps, à mesure qu’ils s’améliorent dans leurs fonctions. Le salaire de base offert peut varier en fonction des compétences et de l’expérience du candidat, de ses connaissances professionnelles, de son emplacement géographique et d’autres besoins particuliers du secteur et de l’entreprise.

En tant que candidat, nous vous encourageons à poser des questions sur la rémunération et à avoir une conversation franche avec votre recruteur, qui pourra vous fournir des détails plus précis sur ce poste.

Department Overview

Description du poste :

Co-op and Internship opportunities allow you to gain valuable work experience across a number of the businesses at TD. You will work with experienced colleagues, receive world class training, and be part of a community of students across TD, where you will have an impact, grow as individual and experience our culture of care.

Role

Our Co-op/Intern Programming is offered with select Co-op and Internship roles and is designed to help you better understand the TD business, build on critical career capabilities, and broaden your professional network. This program is designed to complement your on-the job experience and features:

Leadership talks with key Leaders from across the organization 
Connect and Learns on topics such as Innovation 
Diversity and Inclusion and Personal Branding and so much more 

TD Model Validation (MV) group is responsible for the independent validation and approval of analytical models used for risk, pricing, hedging, and capital evaluation for portfolio of financial products. This also includes validation of decision-making models, such as credit approval and behavioral scoring models.

Candidate will be a member of the Innovation Lab in AI/Machine Learning MV group providing advanced data and software solutions for internal stakeholders. The position reports to the Senior Manager, Innovation Lab, within Model Validation and Model Risk Management group.

Job Description

The successful candidate will be a member of the Innovation Lab in AI/Machine Learning model validation group providing advanced data and software solutions for internal stakeholders. The position reports to the Senior Manager, Innovation Lab, within Model Validation and Model Risk Management group.

Detailed Accountability Includes

Contribute to complex and highly visible solutions to enable innovation and automation in multiple business processes. 
Work closely with internal stakeholders to ensure successful Python application design and development. 
Contribute to Python application development for a variety of purposes including data controls, business analysis, statistical testing, data visualization, report generation, etc. 
Maintain well organized, complete, and up-to-date project documentation, testing, and verification/quality control documents and programs ensuring inspection readiness. 

Job Requirements

Currently enrolled in an undergraduate degree in Engineering, Finance, Accounting, Analytics, Data, Business/Commerce or related field 
Must be enrolled in an undergraduate degree with the intent of going back to school at the start of your work term. 
Experience in using NumPy, SciPy, Pandas, Requests, and other data processing related Python libraries. 
Experience with version control systems such as Bitbucket and GitHub. 
Knowledge of modelling techniques and ability to conduct quantitative tests. 
Inquisitive nature, ability to ask the right questions and escalate issues. Risk & Control mindset. 
Good time management and multitasking skills, with ability to work under pressure and meet tight deadlines. 
Ability to work independently and as part of a team, with problem solving and critical-thinking skills. 

Nice To Have

Experience in developing web applications using Python's Dash, Streamlit, Django, or Flask. 
Exposure to machine learning, natural language processing (NLP), and large language model (LLM). 
Experience in scientific computing. 

Additional Information

Add if applicable: Please note that this is a general posting. If you are selected for an interview, more information regarding which business group and the specific job duties will be provided.

This position is a 4-month work term and will commence May 5th – August 29th, 2025. 
Applications must include a transcript, cover letter (one letter-sized page or less) and a resume (maximum of 2 pages). 
We welcome all applications; however, we will only contact qualified candidates chosen for an interview. Thank you for your interest. 
TD requires employees to reside in the country where the role is located, irrespective of remote working arrangements 
TD is committed to providing you with the best candidate experience and internship in these unique circumstances. As such, work location and start dates are subject to change. 

HOURS

Monday-Friday, standard business hours

INCLUSIVENESS

At TD, we are committed to fostering an inclusive, accessible environment, where all employees and customers feel valued, respected and supported. We are dedicated to building a workforce that reflects the diversity of our customers and communities in which we live and serve. If you require an accommodation for the recruitment/interview process (including alternate formats of materials, or accessible meeting rooms or other accommodation), please let us know and we will work with you to meet your needs.

À propos de nous

La TD est un chef de file mondial dans le secteur des institutions financières. Elle représente la cinquième banque en Amérique du Nord de par son nombre de succursales. Chaque jour, nous offrons une expérience client légendaire à plus de 27 millions de ménages et d’entreprises au Canada, aux États-Unis et partout dans le monde. Plus de 95 000 collègues de la TD mettent en commun leurs compétences, leur talent et leur créativité au service de la Banque, des clients qu’elle sert et des économies qu’elle appuie. Nous sommes guidés par notre vision d’être une meilleure banque et par notre objectif d’enrichir la vie de nos clients, de nos collectivités et de nos collègues.

La TD est une entreprise profondément engagée à être une leader en matière d’expérience client. Voilà pourquoi nous croyons que chaque collègue, peu importe son secteur d’activité, est en contact avec la clientèle. En parallèle de l’évolution de nos activités et de notre stratégie, nous innovons afin d’améliorer l’expérience client et de créer des capacités pour façonner l’avenir des services bancaires. Que vous ayez plusieurs années d’expérience dans le secteur bancaire ou que vous commenciez tout juste votre carrière dans le domaine des services financiers, nous pouvons vous aider à réaliser votre plein potentiel. Vous pourrez compter sur nos programmes de formation et de mentorat et sur des conversations sur le perfectionnement et le leadership pour réaliser votre plein potentiel et atteindre vos objectifs. Notre croissance en tant qu’entreprise rime avec la vôtre.

Notre programme de rémunération globale

Notre programme de rémunération globale reflète les investissements que nous faisons pour aider nos collègues et leur famille à atteindre leurs objectifs en matière de bien-être mental, physique et financier. La rémunération globale à la TD inclut le salaire de base, la rémunération variable et bien d’autres régimes clés, comme des avantages sociaux en matière de santé et de bien-être, des régimes d’épargne et de retraite, des congés payés, des avantages bancaires et des rabais, des occasions de développement de carrière et des programmes de récompenses et reconnaissance. En savoir plus

Renseignements Supplémentaires

Nous sommes ravis que vous envisagiez une carrière à la TD. Sachez que nous avons à cœur d’aider nos collègues à réussir dans leur vie tant personnelle que professionnelle. C’est d’ailleurs pourquoi nous leur offrons des conversations sur le perfectionnement, des programmes de formation et un régime d’avantages sociaux concurrentiel.

Perfectionnement des collègues 

Un cheminement professionnel particulier vous intéresse ou vous cherchez à acquérir certaines compétences? Nous tenons à vous mettre sur la voie de la réussite. Vous aurez des conversations régulières sur le développement de carrière, le perfectionnement et le rendement avec votre gestionnaire. Une variété de programmes de mentorat et une plateforme d’apprentissage en ligne seront également à votre disposition pour vous aider à ouvrir de nouvelles portes. Que vous ayez à cœur d’aider les clients et souhaitiez élargir votre expérience ou que vous préfériez coacher et inspirer vos collègues, sachez que la TD propose un grand nombre de cheminements professionnels et qu’elle s’engage à vous aider à relever les occasions qui vont dans le sens de vos objectifs.

Formation et intégration

Nous tenons à nous assurer que vous disposez des outils et ressources nécessaires pour réussir à votre nouveau poste. Dans cette optique, nous organiserons des séances d’intégration et de formation.

Processus d’entrevue 

Nous communiquerons avec les candidats sélectionnés pour planifier une entrevue. Nous ferons notre possible pour communiquer par courriel ou par téléphone avec tous les candidats pour leur faire part de notre décision.

Mesures d’adaptation

L’accessibilité est importante pour nous. N’hésitez pas à nous faire part de toute mesure d’adaptation (salles de réunion accessibles, sous-titres pour les entrevues virtuelles, etc.) dont vous pourriez avoir besoin pour participer sans entraves au processus d’entrevue.

Nous avons hâte d’avoir de vos nouvelles!

''')


process_resume("CSYRM.pdf", job_description_text='''

About the job
Type De Rôle

Internship/Co-op

Session De Stage

Summer/Term 3

Lieu De Travail

Toronto, Ontario, Canada

Horaire

37.5

Détails De La Rémunération

$44.000.000 - $48,000.00 CAD

La TD a à cœur d’offrir une rémunération juste et équitable à tous les collègues. Les occasions de croissance et le perfectionnement des compétences sont des caractéristiques essentielles de l’expérience collègue à la TD. Nos politiques et pratiques en matière de rémunération ont été conçues pour permettre aux collègues de progresser dans l’échelle salariale au fil du temps, à mesure qu’ils s’améliorent dans leurs fonctions. Le salaire de base offert peut varier en fonction des compétences et de l’expérience du candidat, de ses connaissances professionnelles, de son emplacement géographique et d’autres besoins particuliers du secteur et de l’entreprise.

En tant que candidat, nous vous encourageons à poser des questions sur la rémunération et à avoir une conversation franche avec votre recruteur, qui pourra vous fournir des détails plus précis sur ce poste.

Department Overview

Description du poste :

Co-op and Internship opportunities allow you to gain valuable work experience across a number of the businesses at TD. You will work with experienced colleagues, receive world class training, and be part of a community of students across TD, where you will have an impact, grow as individual and experience our culture of care.

Role

Our Co-op/Intern Programming is offered with select Co-op and Internship roles and is designed to help you better understand the TD business, build on critical career capabilities, and broaden your professional network. This program is designed to complement your on-the job experience and features:

Leadership talks with key Leaders from across the organization 
Connect and Learns on topics such as Innovation 
Diversity and Inclusion and Personal Branding and so much more 

TD Model Validation (MV) group is responsible for the independent validation and approval of analytical models used for risk, pricing, hedging, and capital evaluation for portfolio of financial products. This also includes validation of decision-making models, such as credit approval and behavioral scoring models.

Candidate will be a member of the Innovation Lab in AI/Machine Learning MV group providing advanced data and software solutions for internal stakeholders. The position reports to the Senior Manager, Innovation Lab, within Model Validation and Model Risk Management group.

Job Description

The successful candidate will be a member of the Innovation Lab in AI/Machine Learning model validation group providing advanced data and software solutions for internal stakeholders. The position reports to the Senior Manager, Innovation Lab, within Model Validation and Model Risk Management group.

Detailed Accountability Includes

Contribute to complex and highly visible solutions to enable innovation and automation in multiple business processes. 
Work closely with internal stakeholders to ensure successful Python application design and development. 
Contribute to Python application development for a variety of purposes including data controls, business analysis, statistical testing, data visualization, report generation, etc. 
Maintain well organized, complete, and up-to-date project documentation, testing, and verification/quality control documents and programs ensuring inspection readiness. 

Job Requirements

Currently enrolled in an undergraduate degree in Engineering, Finance, Accounting, Analytics, Data, Business/Commerce or related field 
Must be enrolled in an undergraduate degree with the intent of going back to school at the start of your work term. 
Experience in using NumPy, SciPy, Pandas, Requests, and other data processing related Python libraries. 
Experience with version control systems such as Bitbucket and GitHub. 
Knowledge of modelling techniques and ability to conduct quantitative tests. 
Inquisitive nature, ability to ask the right questions and escalate issues. Risk & Control mindset. 
Good time management and multitasking skills, with ability to work under pressure and meet tight deadlines. 
Ability to work independently and as part of a team, with problem solving and critical-thinking skills. 

Nice To Have

Experience in developing web applications using Python's Dash, Streamlit, Django, or Flask. 
Exposure to machine learning, natural language processing (NLP), and large language model (LLM). 
Experience in scientific computing. 

Additional Information

Add if applicable: Please note that this is a general posting. If you are selected for an interview, more information regarding which business group and the specific job duties will be provided.

This position is a 4-month work term and will commence May 5th – August 29th, 2025. 
Applications must include a transcript, cover letter (one letter-sized page or less) and a resume (maximum of 2 pages). 
We welcome all applications; however, we will only contact qualified candidates chosen for an interview. Thank you for your interest. 
TD requires employees to reside in the country where the role is located, irrespective of remote working arrangements 
TD is committed to providing you with the best candidate experience and internship in these unique circumstances. As such, work location and start dates are subject to change. 

HOURS

Monday-Friday, standard business hours

INCLUSIVENESS

At TD, we are committed to fostering an inclusive, accessible environment, where all employees and customers feel valued, respected and supported. We are dedicated to building a workforce that reflects the diversity of our customers and communities in which we live and serve. If you require an accommodation for the recruitment/interview process (including alternate formats of materials, or accessible meeting rooms or other accommodation), please let us know and we will work with you to meet your needs.

À propos de nous

La TD est un chef de file mondial dans le secteur des institutions financières. Elle représente la cinquième banque en Amérique du Nord de par son nombre de succursales. Chaque jour, nous offrons une expérience client légendaire à plus de 27 millions de ménages et d’entreprises au Canada, aux États-Unis et partout dans le monde. Plus de 95 000 collègues de la TD mettent en commun leurs compétences, leur talent et leur créativité au service de la Banque, des clients qu’elle sert et des économies qu’elle appuie. Nous sommes guidés par notre vision d’être une meilleure banque et par notre objectif d’enrichir la vie de nos clients, de nos collectivités et de nos collègues.

La TD est une entreprise profondément engagée à être une leader en matière d’expérience client. Voilà pourquoi nous croyons que chaque collègue, peu importe son secteur d’activité, est en contact avec la clientèle. En parallèle de l’évolution de nos activités et de notre stratégie, nous innovons afin d’améliorer l’expérience client et de créer des capacités pour façonner l’avenir des services bancaires. Que vous ayez plusieurs années d’expérience dans le secteur bancaire ou que vous commenciez tout juste votre carrière dans le domaine des services financiers, nous pouvons vous aider à réaliser votre plein potentiel. Vous pourrez compter sur nos programmes de formation et de mentorat et sur des conversations sur le perfectionnement et le leadership pour réaliser votre plein potentiel et atteindre vos objectifs. Notre croissance en tant qu’entreprise rime avec la vôtre.

Notre programme de rémunération globale

Notre programme de rémunération globale reflète les investissements que nous faisons pour aider nos collègues et leur famille à atteindre leurs objectifs en matière de bien-être mental, physique et financier. La rémunération globale à la TD inclut le salaire de base, la rémunération variable et bien d’autres régimes clés, comme des avantages sociaux en matière de santé et de bien-être, des régimes d’épargne et de retraite, des congés payés, des avantages bancaires et des rabais, des occasions de développement de carrière et des programmes de récompenses et reconnaissance. En savoir plus

Renseignements Supplémentaires

Nous sommes ravis que vous envisagiez une carrière à la TD. Sachez que nous avons à cœur d’aider nos collègues à réussir dans leur vie tant personnelle que professionnelle. C’est d’ailleurs pourquoi nous leur offrons des conversations sur le perfectionnement, des programmes de formation et un régime d’avantages sociaux concurrentiel.

Perfectionnement des collègues 

Un cheminement professionnel particulier vous intéresse ou vous cherchez à acquérir certaines compétences? Nous tenons à vous mettre sur la voie de la réussite. Vous aurez des conversations régulières sur le développement de carrière, le perfectionnement et le rendement avec votre gestionnaire. Une variété de programmes de mentorat et une plateforme d’apprentissage en ligne seront également à votre disposition pour vous aider à ouvrir de nouvelles portes. Que vous ayez à cœur d’aider les clients et souhaitiez élargir votre expérience ou que vous préfériez coacher et inspirer vos collègues, sachez que la TD propose un grand nombre de cheminements professionnels et qu’elle s’engage à vous aider à relever les occasions qui vont dans le sens de vos objectifs.

Formation et intégration

Nous tenons à nous assurer que vous disposez des outils et ressources nécessaires pour réussir à votre nouveau poste. Dans cette optique, nous organiserons des séances d’intégration et de formation.

Processus d’entrevue 

Nous communiquerons avec les candidats sélectionnés pour planifier une entrevue. Nous ferons notre possible pour communiquer par courriel ou par téléphone avec tous les candidats pour leur faire part de notre décision.

Mesures d’adaptation

L’accessibilité est importante pour nous. N’hésitez pas à nous faire part de toute mesure d’adaptation (salles de réunion accessibles, sous-titres pour les entrevues virtuelles, etc.) dont vous pourriez avoir besoin pour participer sans entraves au processus d’entrevue.

Nous avons hâte d’avoir de vos nouvelles!

''')



