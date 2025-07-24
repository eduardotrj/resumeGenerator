from .file_operations import load_text, load_schema


def format_prompt(template_path, **kwargs):
    """Format a prompt template with given parameters"""
    template = load_text(template_path)
    # Add schema to kwargs if not present
    if 'schema' not in kwargs:
        kwargs['schema'] = load_schema()
    return template.format(**kwargs)


def create_adaptation_prompt(job_offer, adapt_text, language='English'):
    """Create the adaptation prompt for work experience and skills"""

    language_prompts = {
        'English': "You are a professional resume editor. You must respond with valid JSON only. Adapt only the work experience and skills sections to match job requirements.",
        'Spanish': "Eres un editor profesional de currículums. Debes responder solo con JSON válido. Adapta solo las secciones de experiencia laboral y habilidades para coincidir con los requisitos del trabajo.",
        'German': "Sie sind ein professioneller Lebenslauf-Editor. Sie müssen nur mit gültigem JSON antworten. Passen Sie nur die Abschnitte Berufserfahrung und Fähigkeiten an die Stellenanforderungen an."
    }

    system_message = language_prompts.get(language, language_prompts['English'])

    adaptation_prompt = f"""
IMPORTANT: You must respond with valid JSON only. No explanations, no markdown, just pure JSON.

ADAPT ONLY WORK EXPERIENCE AND SKILLS FOR THIS JOB OFFER:

JOB OFFER:
{job_offer}

CURRENT WORK EXPERIENCE AND SKILLS TO ADAPT:
{adapt_text}

INSTRUCTIONS:
1. Analyze the job offer requirements
2. Adapt ONLY the work experience descriptions to highlight relevant accomplishments in 4 sentences
3. Don't change Company Name or experience dates, just adapt the summary
4. Adapt ONLY the skills section to emphasize the most relevant technical and soft skills
5. Use keywords from the job offer when appropriate
6. Quantify achievements where possibles
7. Respond with ONLY valid JSON in this exact structure:

{{
  "work": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "startDate": "YYYY-MM",
      "endDate": "YYYY-MM or present",
      "summary": ["Adapted bullet point 1", "Adapted bullet point 2"]
    }}
  ],
  "skills": [
    {{
      "category": "Category Name",
      "items": ["Skill 1", "Skill 2"]
    }}
  ]
}}

RESPOND WITH JSON ONLY - NO OTHER TEXT.
"""

    return adaptation_prompt, system_message


def create_cover_letter_prompt(company_name, job_offer, resume_content, language='English'):
    """Create the cover letter generation prompt"""

    language_prompts = {
        'English': "You are a professional recruiter. Write a compelling cover letter.",
        'Spanish': "Eres un reclutador profesional. Escribe una carta de presentación convincente.",
        'German': "Sie sind ein professioneller Personalvermittler. Schreiben Sie ein überzeugendes Anschreiben."
    }

    system_message = language_prompts.get(language, language_prompts['English'])

    cover_prompt = f"""
Write a compelling cover letter for this job application:

COMPANY: {company_name}

JOB OFFER:
{job_offer}

RESUME CONTENT:
{resume_content}

Create a personalized cover letter that:
1. Addresses the company and specific role
2. Highlights the most relevant experience and skills
3. Shows enthusiasm for the position
4. Demonstrates knowledge of the company/role
5. Includes a strong opening and closing
6. Keeps professional tone throughout
7. Instead of addressing the hiring manager by name, use a more general greeting such as "Dear Team."
8. Avoid including company details, personal information or any other unnecessary text.
"""

    return cover_prompt, system_message