from local_llm_client import run_llm
import os
import json


def load_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_schema():
    """Load the resume schema from schema.py"""
    import sys
    sys.path.append('templates')
    try:
        from schema import schema
        return json.dumps(schema, indent=2)
    except ImportError:
        # Fallback schema if file not found
        return json.dumps({
            "name": "string",
            "label": "string",
            # "summary": "string",
            "contactInfo": {"email": "string", "phone": "string", "location": {}},
            "profiles": [{"linkedIn": "string", "github": "string"}],
            "work": [{"title": "string", "company": "string", "summary": ["string"]}]
        }, indent=2)


def save_text(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.strip())


def save_json(file_path, data):
    """Save data as JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def format_prompt(template_path, **kwargs):
    template = load_text(template_path)
    # Add schema to kwargs if not present
    if 'schema' not in kwargs:
        kwargs['schema'] = load_schema()
    return template.format(**kwargs)


def json_to_resume_text(resume_data):
    """Convert resume JSON to formatted text"""
    resume_text = f"{resume_data['name']}\n{resume_data['label']}\n\n"
    resume_text += f"Contact: {resume_data['contactInfo']['email']} | {resume_data['contactInfo']['phone']}\n"
    resume_text += f"Location: {resume_data['contactInfo']['location']['city']}, {resume_data['contactInfo']['location']['countryCode']}\n\n"

    if 'profiles' in resume_data and resume_data['profiles']:
        profile = resume_data['profiles'][0]
        resume_text += "Profiles:\n"
        for key, value in profile.items():
            if value:
                resume_text += f"• {key.capitalize()}: {value}\n"
        resume_text += "\n"

    if 'summary' in resume_data:
        resume_text += "Summary:\n"
        resume_text += f"{resume_data['summary']}\n\n"

    if 'work' in resume_data:
        resume_text += "Work Experience:\n"
        for job in resume_data['work']:
            resume_text += f"\n{job['title']} at {job['company']} ({job.get('dates', job.get('startDate', '') + ' - ' + job.get('endDate', ''))})\n"
            if 'summary' in job:
                for point in job['summary']:
                    resume_text += f"{point}\n"

    return resume_text


def load_adapt_info():
    """Load the adaptation information from adapt_info.json"""
    try:
        return load_json("inputs/adapt_info.json")
    except Exception as e:
        print(f"Error loading adapt_info.json: {e}")
        return {}


def adapt_info_to_text(adapt_data):
    """Convert adaptation JSON data to text format for prompting"""
    work_experience = adapt_data.get('work', [])
    skills = adapt_data.get('skills', [])

    # Format work experience
    work_text = ""
    for job in work_experience:
        title = job.get('title', '')
        company = job.get('company', '')
        dates = job.get('dates', job.get('startDate', '') + ' - ' + job.get('endDate', ''))
        summary = job.get('summary', [])
        summary_text = "\n".join([f"• {point}" for point in summary])
        work_text += f"\n{title} at {company} ({dates})\n{summary_text}\n"

    # Format skills
    skills_text = ""
    for category in skills:
        category_name = category.get('category', '')
        items = category.get('items', [])
        items_text = ", ".join(items)
        skills_text += f"{category_name}: {items_text}\n"

    return f"Work Experience:\n{work_text}\nSkills:\n{skills_text}"


def generate_resume_and_cover_letter(form_data):
    """
    Generate adapted resume and cover letter based on form data
    Only adapts work experience and skills from adapt_info.json

    Args:
        form_data (dict): Dictionary with keys: company_name, job_offer, language

    Returns:
        dict: Contains paths to generated files and status
    """
    try:
        # Load base resume data (for personal info, contact, etc.)
        resume_data = load_json("inputs/resume.json")

        # Load only work experience and skills to adapt
        adapt_data = load_adapt_info()
        adapt_text = adapt_info_to_text(adapt_data)

        # Get form data
        company_name = form_data.get('company_name', '')
        job_offer = form_data.get('job_offer', '')
        language = form_data.get('language', 'English')

        # Create language-specific system messages
        language_prompts = {
            'English': "You are a professional resume editor. You must respond with valid JSON only. Adapt only the work experience and skills sections to match job requirements.",
            'Spanish': "Eres un editor profesional de currículums. Debes responder solo con JSON válido. Adapta solo las secciones de experiencia laboral y habilidades para coincidir con los requisitos del trabajo.",
            'German': "Sie sind ein professioneller Lebenslauf-Editor. Sie müssen nur mit gültigem JSON antworten. Passen Sie nur die Abschnitte Berufserfahrung und Fähigkeiten an die Stellenanforderungen an."
        }

        system_message = language_prompts.get(language, language_prompts['English'])

        # Create focused adaptation prompt
        adaptation_prompt = f"""
IMPORTANT: You must respond with valid JSON only. No explanations, no markdown, just pure JSON.

ADAPT ONLY WORK EXPERIENCE AND SKILLS FOR THIS JOB OFFER:

JOB OFFER:
{job_offer}

CURRENT WORK EXPERIENCE AND SKILLS TO ADAPT:
{adapt_text}

INSTRUCTIONS:
1. Analyze the job offer requirements
2. Adapt ONLY the work experience descriptions to highlight relevant accomplishments
3. Adapt ONLY the skills section to emphasize the most relevant technical and soft skills
4. Use keywords from the job offer when appropriate
5. Quantify achievements where possible
6. Respond with ONLY valid JSON in this exact structure:

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

        print("🤖 Sending prompt to LLM...")
        adapted_content_json = run_llm(adaptation_prompt, system_message)

        # Debug: Print the raw response
        print(f"📝 Raw LLM Response (first 200 chars): {repr(adapted_content_json[:200])}")
        print(f"📏 Response length: {len(adapted_content_json)}")

        # Try to parse the JSON response with improved cleaning
        try:
            if not adapted_content_json or adapted_content_json.strip() == "":
                raise ValueError("Empty response from LLM")

            # Clean the response to extract JSON
            cleaned_response = adapted_content_json.strip()

            # Remove common markdown formatting
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]

            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]

            cleaned_response = cleaned_response.strip()

            # Try to find JSON in the response if it's mixed with other text
            if not cleaned_response.startswith('{'):
                start_idx = cleaned_response.find('{')
                if start_idx != -1:
                    cleaned_response = cleaned_response[start_idx:]

            if not cleaned_response.endswith('}'):
                end_idx = cleaned_response.rfind('}')
                if end_idx != -1:
                    cleaned_response = cleaned_response[:end_idx + 1]

            print(f"🧹 Cleaned response (first 200 chars): {repr(cleaned_response[:200])}")

            # Parse JSON
            adapted_content = json.loads(cleaned_response)
            print("✅ JSON parsing successful!")

            # Validate required fields
            if 'work' not in adapted_content and 'skills' not in adapted_content:
                raise ValueError("Response doesn't contain work or skills sections")

            # Merge adapted content with base resume data
            final_resume = resume_data.copy()
            if 'work' in adapted_content:
                final_resume['work'] = adapted_content['work']
                print(f"📊 Work experience adapted: {len(adapted_content['work'])} jobs")
            if 'skills' in adapted_content:
                final_resume['skills'] = adapted_content['skills']
                print(f"🎯 Skills adapted: {len(adapted_content['skills'])} categories")

            # Create output filenames with company name
            safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_company_name = safe_company_name.replace(' ', '_')

            # Save adapted JSON format
            resume_json_filename = f"outputs/adapted_resume_{safe_company_name}_{language}.json"
            save_json(resume_json_filename, final_resume)
            print(f"💾 JSON file saved: {resume_json_filename}")

            # Convert to text format
            adapted_resume_text = json_to_resume_text(final_resume)
            resume_text_filename = f"outputs/adapted_resume_{safe_company_name}_{language}.txt"
            save_text(resume_text_filename, adapted_resume_text)
            print(f"📄 Text file saved: {resume_text_filename}")

            # Generate HTML resume
            html_filename = generate_html_resume(final_resume, company_name, language)
            if html_filename:
                print(f"🌐 HTML file saved: {html_filename}")
            else:
                print("⚠️ HTML file generation failed")

            json_parse_success = True

        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"📝 Raw response: {repr(adapted_content_json)}")

            # Fallback: save as text if JSON parsing fails
            safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_company_name = safe_company_name.replace(' ', '_')

            resume_text_filename = f"outputs/adapted_resume_{safe_company_name}_{language}.txt"

            # Create a simple text resume using the original data
            fallback_text = f"RESUME ADAPTATION FAILED - USING ORIGINAL DATA\n\n"
            fallback_text += f"Original response from LLM:\n{adapted_content_json}\n\n"
            fallback_text += json_to_resume_text(resume_data)

            save_text(resume_text_filename, fallback_text)

            adapted_resume_text = fallback_text
            resume_json_filename = None
            html_filename = None
            json_parse_success = False

        # Generate Cover Letter using adapted content
        cover_letter_system = language_prompts.get(language, "You are a professional recruiter. Write a compelling cover letter.")
        cover_letter_system = cover_letter_system.replace("You must respond with valid JSON only", "Write a professional cover letter")

        cover_prompt = f"""
Write a compelling cover letter for this job application:

COMPANY: {company_name}

JOB OFFER:
{job_offer}

RESUME CONTENT:
{adapted_resume_text if 'adapted_resume_text' in locals() else adapt_text}

Create a personalized cover letter that:
1. Addresses the company and specific role
2. Highlights the most relevant experience and skills
3. Shows enthusiasm for the position
4. Demonstrates knowledge of the company/role
5. Includes a strong opening and closing
6. Keeps professional tone throughout
"""

        print("📝 Generating cover letter...")
        cover_letter = run_llm(cover_prompt, cover_letter_system)
        safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_company_name = safe_company_name.replace(' ', '_')
        cover_filename = f"outputs/cover_letter_{safe_company_name}_{language}.txt"
        save_text(cover_filename, cover_letter)
        print(f"💌 Cover letter saved: {cover_filename}")

        # Prepare return message
        files_created = [resume_text_filename, cover_filename]
        if resume_json_filename:
            files_created.insert(0, resume_json_filename)
        if html_filename:
            files_created.append(html_filename)

        status_message = "Resume and cover letter generated successfully"
        if not json_parse_success:
            status_message += " (Note: JSON parsing failed, text format used)"

        return {
            'status': 'success',
            'resume_file': resume_text_filename,
            'resume_json_file': resume_json_filename if resume_json_filename else None,
            'resume_html_file': html_filename if html_filename else None,
            'cover_letter_file': cover_filename,
            'files_created': files_created,
            'message': f'{status_message} for {company_name} in {language}'
        }

    except Exception as e:
        print(f"💥 Error in generate_resume_and_cover_letter: {e}")
        return {
            'status': 'error',
            'message': f'Error generating documents: {str(e)}'
        }


def generate_html_resume(adapted_resume_data, company_name, language):
    """
    Generate HTML resume using the template and adapted data

    Args:
        adapted_resume_data (dict): Complete resume data with adapted work/skills
        company_name (str): Company name for filename
        language (str): Language for filename

    Returns:
        str: Path to generated HTML file
    """
    try:
        # Load HTML template
        template_path = "templates/resume_model.html"
        with open(template_path, "r", encoding="utf-8") as f:
            html_template = f.read()

        # Generate profiles HTML
        profiles_html = ""
        if 'profiles' in adapted_resume_data and adapted_resume_data['profiles']:
            for profile in adapted_resume_data['profiles']:
                for key, value in profile.items():
                    if value and key.lower() in ['linkedin', 'github', 'portfolio', 'substack', 'codepen']:
                        icon_map = {
                            'linkedin': '💼',
                            'github': '🐱',
                            'portfolio': '💻',
                            'substack': '🗞️',
                            'codepen': '🎨'
                        }
                        icon = icon_map.get(key.lower(), '🔗')
                        profiles_html += f'''
                <a href="{value}" class="profile-link" data-type="{key.lower()}">
                    <span>{icon}</span> {key.capitalize()}
                </a>'''

        # Generate work experience HTML - consolidate jobs with same title and company
        work_html = ""
        if 'work' in adapted_resume_data and adapted_resume_data['work']:
            # Dictionary to track consolidated jobs by title + company
            consolidated_jobs = {}

            for job in adapted_resume_data['work']:
                job_key = f"{job.get('title', '')}__{job.get('company', '')}"

                if job_key in consolidated_jobs:
                    # Job already exists, merge summary
                    existing_summary = consolidated_jobs[job_key].get('summary', [])
                    new_summary = job.get('summary', [])
                    # Add new summary items to existing ones, avoiding duplicates
                    for item in new_summary:
                        if item not in existing_summary:
                            existing_summary.append(item)
                    consolidated_jobs[job_key]['summary'] = existing_summary

                    # Update date range if needed (take the earliest start and latest end)
                    existing_start = consolidated_jobs[job_key].get('startDate', '')
                    existing_end = consolidated_jobs[job_key].get('endDate', '')
                    new_start = job.get('startDate', '')
                    new_end = job.get('endDate', '')

                    # Simple date comparison (assuming YYYY-MM format)
                    if new_start and (not existing_start or new_start < existing_start):
                        consolidated_jobs[job_key]['startDate'] = new_start
                    if new_end and (not existing_end or new_end > existing_end):
                        consolidated_jobs[job_key]['endDate'] = new_end

                else:
                    # New job, add to consolidated list
                    consolidated_jobs[job_key] = job.copy()

            # Generate HTML for consolidated jobs
            for job in consolidated_jobs.values():
                # Format date range
                date_range = ""
                if 'startDate' in job and 'endDate' in job:
                    date_range = f"{job['startDate']} - {job['endDate']}"
                elif 'dates' in job:
                    date_range = job['dates']

                # Format summary as list items
                summary_html = ""
                if 'summary' in job and job['summary']:
                    for item in job['summary']:
                        summary_html += f"<li>{item}</li>"

                work_html += f'''
                <div class="work-item item">
                    <div class="work-title titleText">{job.get('title', '')}</div>
                    <div class="work-company separatedText">
                        <span class="company-name">{job.get('company', '')}</span>
                        <span class="company-range">{date_range}</span>
                    </div>
                    <ul class="regularText work-summary">
                        {summary_html}
                    </ul>
                </div>'''

        # Generate skills HTML - only include categories with items
        skills_html = ""
        if 'skills' in adapted_resume_data and adapted_resume_data['skills']:
            skills_list_items = []

            for skill_category in adapted_resume_data['skills']:
                if 'category' in skill_category and 'items' in skill_category:
                    # Only add category if it has items
                    items = skill_category['items']
                    if items and len(items) > 0:
                        # Filter out empty items
                        filtered_items = [item.strip() for item in items if item and item.strip()]

                        if filtered_items:  # Only add if there are non-empty items
                            skills_items = ' | '.join([f'<span class="keyword">{skill}</span>' for skill in filtered_items])
                            skills_list_items.append(f'''
                    <li class="skill-item">
                        <div class="skill-name allInLine boldText">{skill_category['category']}:</div>
                        <div class="skill-keywords allInLine regularText">
                            {skills_items}
                        </div>
                    </li>''')

            if skills_list_items:  # Only create skills section if there are items
                skills_html = '<ul class="skills-list">' + ''.join(skills_list_items) + '</ul>'

        # Generate projects HTML (if exists)
        projects_html = ""
        if 'projects' in adapted_resume_data and adapted_resume_data['projects']:
            for project in adapted_resume_data['projects']:
                project_link = ""
                if 'link' in project and project['link']:
                    project_link = f'<a class="project-link" href="{project["link"]}">View Project →</a>'

                projects_html += f'''
                <div class="project-item item">
                    <div class="project-name boldText">{project.get('name', '')}:
                        {project_link}
                    </div>
                    <p class="project-description regularText">• {project.get('description', '')}</p>
                </div>'''

        # Generate education HTML (if exists)
        education_html = ""
        if 'education' in adapted_resume_data and adapted_resume_data['education']:
            for edu in adapted_resume_data['education']:
                location = edu.get('location', {})
                location_str = ""
                if isinstance(location, dict):
                    location_str = f"{location.get('city', '')}, {location.get('countryCode', '')}"
                else:
                    location_str = str(location)

                education_html += f'''
                <div class="education-item item">
                    <div class="studyType boldText allInLine">{edu.get('studyType', '')}</div><span> | </span>
                    <div class="work-title boldText allInLine">{edu.get('area', '')}</div><span> | </span>
                    <div class="education-institution regularText allInLine">{edu.get('institution', '')}</div><span> | </span>
                    <div class="date-range regularText allInLine">{edu.get('startDate', '')} - {edu.get('endDate', '')}</div><span> | </span>
                    <div class="location regularText allInLine">{location_str}</div>
                </div>'''

        # Replace placeholders in HTML template
        html_content = html_template

        # Basic information
        html_content = html_content.replace('John Doe', adapted_resume_data.get('name', 'John Doe'))
        html_content = html_content.replace('john.doe@example.com', adapted_resume_data.get('contactInfo', {}).get('email', ''))
        html_content = html_content.replace('+1 (555) 123-4567', adapted_resume_data.get('contactInfo', {}).get('phone', ''))

        # Location
        location_info = adapted_resume_data.get('contactInfo', {}).get('location', {})
        if isinstance(location_info, dict):
            location_text = f"{location_info.get('city', '')}, {location_info.get('countryCode', '')}"
        else:
            location_text = str(location_info)
        html_content = html_content.replace('San Francisco, CA', location_text)

        # Replace profile links section
        profiles_start = html_content.find('<div class="profile" id="profiles">')
        profiles_end = html_content.find('</div>', profiles_start) + 6
        if profiles_start != -1 and profiles_end != -1:
            html_content = html_content[:profiles_start] + f'<div class="profile" id="profiles">{profiles_html}\n            </div>' + html_content[profiles_end:]

        # Replace work experience section
        work_start = html_content.find('<div id="work">')
        work_end = html_content.find('</div>', work_start) + 6
        if work_start != -1 and work_end != -1:
            html_content = html_content[:work_start] + f'<div id="work">{work_html}\n                    </div>' + html_content[work_end:]

        # Replace skills section - only if there are skills to show
        if skills_html:
            skills_start = html_content.find('<div class="skills-grid" id="skills">')
            skills_end = html_content.find('</div>', skills_start) + 6
            if skills_start != -1 and skills_end != -1:
                html_content = html_content[:skills_start] + f'<div class="skills-grid" id="skills">\n                        {skills_html}\n                    </div>' + html_content[skills_end:]
        else:
            # Remove the entire skills section if no skills to display
            section_start = html_content.find('<section class="section">\n                    <h2>Technical Skills</h2>')
            if section_start != -1:
                section_end = html_content.find('</section>', section_start) + 10
                if section_end != -1:
                    html_content = html_content[:section_start] + html_content[section_end:]

        # Replace projects section (if exists)
        if projects_html:
            projects_start = html_content.find('<div id="projects">')
            projects_end = html_content.find('</div>', projects_start) + 6
            if projects_start != -1 and projects_end != -1:
                html_content = html_content[:projects_start] + f'<div id="projects">{projects_html}\n                    </div>' + html_content[projects_end:]

        # Replace education section (if exists)
        if education_html:
            education_start = html_content.find('<div id="education">')
            education_end = html_content.find('</div>', education_start) + 6
            if education_start != -1 and education_end != -1:
                html_content = html_content[:education_start] + f'<div id="education">{education_html}\n                    </div>' + html_content[education_end:]

        # Save HTML file
        safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_company_name = safe_company_name.replace(' ', '_')

        html_filename = f"outputs/resume_{safe_company_name}_{language}.html"
        os.makedirs(os.path.dirname(html_filename), exist_ok=True)

        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        return html_filename

    except Exception as e:
        print(f"Error generating HTML resume: {e}")
        return None


def main_cli():
    """Original main function for command line usage"""
    resume = load_text("inputs/resume.txt")
    job_offer = load_text("inputs/job_offer.txt")

    # Adapt Resume
    resume_prompt = format_prompt("templates/resume_prompt.txt", resume=resume, job_offer=job_offer)
    adapted_resume = run_llm(resume_prompt)
    save_text("outputs/adapted_resume.txt", adapted_resume)
    print("✅ Adapted resume generated.")

    # Generate Cover Letter
    cover_prompt = format_prompt("templates/cover_letter_prompt.txt", resume=adapted_resume, job_offer=job_offer)
    cover_letter = run_llm(cover_prompt)
    save_text("outputs/cover_letter.txt", cover_letter)
    print("✅ Cover letter generated.")


def main():
    """Launch the GUI application"""
    try:
        from view import main as gui_main
        print("🚀 Launching Resume Generator GUI...")
        gui_main()
    except ImportError as e:
        print(f"Error importing GUI: {e}")
        print("Falling back to CLI mode...")
        main_cli()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        print("Please check that all dependencies are installed.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        main_cli()
    else:
        main()


def test_llm_json():
    """Test function to check if LLM returns valid JSON"""
    test_prompt = """
RESPOND WITH VALID JSON ONLY:

{
  "work": [
    {
      "title": "Test Job",
      "company": "Test Company",
      "startDate": "2020-01",
      "endDate": "2023-01",
      "summary": ["Test accomplishment 1", "Test accomplishment 2"]
    }
  ],
  "skills": [
    {
      "category": "Test Skills",
      "items": ["Skill 1", "Skill 2"]
    }
  ]
}

RESPOND WITH THIS EXACT JSON STRUCTURE.
"""

    try:
        from local_llm_client import test_connection, run_llm

        print("🧪 Testing LLM JSON response...")

        # First test connection
        if not test_connection():
            return False

        # Test JSON generation
        response = run_llm(test_prompt, "You must respond with valid JSON only.")
        print(f"📝 Raw response: {repr(response)}")

        # Try to parse
        try:
            import json
            parsed = json.loads(response.strip())
            print("✅ JSON parsing successful!")
            print(f"📊 Parsed data: {parsed}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            return False

    except Exception as e:
        print(f"💥 Test failed: {e}")
        return False
