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
    sys.path.append('prompt_templates')
    try:
        from schema import schema
        return json.dumps(schema, indent=2)
    except ImportError:
        # Fallback schema if file not found
        return json.dumps({
            "name": "string",
            "label": "string",
            "summary": "string",
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

    resume_text += f"Summary:\n{resume_data['summary']}\n\n"

    if 'work' in resume_data:
        resume_text += "Work Experience:\n"
        for job in resume_data['work']:
            resume_text += f"\n{job['title']} at {job['company']} ({job.get('dates', job.get('startDate', '') + ' - ' + job.get('endDate', ''))})\n"
            if 'summary' in job:
                for point in job['summary']:
                    resume_text += f"{point}\n"

    return resume_text

def generate_resume_and_cover_letter(form_data):
    """
    Generate adapted resume and cover letter based on form data

    Args:
        form_data (dict): Dictionary with keys: company_name, job_offer, language

    Returns:
        dict: Contains paths to generated files and status
    """
    try:
        # Load resume data
        resume_data = load_json("inputs/resume.json")
        resume_text = json_to_resume_text(resume_data)

        # Get form data
        company_name = form_data.get('company_name', '')
        job_offer = form_data.get('job_offer', '')
        language = form_data.get('language', 'English')

        # Create language-specific system messages
        language_prompts = {
            'English': "You are a professional resume editor. Respond in English with valid JSON only.",
            'Spanish': "Eres un editor profesional de currículums. Responde solo en español con JSON válido.",
            'German': "Sie sind ein professioneller Lebenslauf-Editor. Antworten Sie nur auf Deutsch mit gültigem JSON."
        }

        system_message = language_prompts.get(language, language_prompts['English'])

        # Adapt Resume
        resume_prompt = format_prompt("prompt_templates/resume_prompt.txt",
                                    resume=resume_text,
                                    job_offer=job_offer)

        adapted_resume_json = run_llm(resume_prompt, system_message)

        # Try to parse the JSON response
        try:
            # Clean the response to extract JSON
            cleaned_response = adapted_resume_json.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            adapted_resume_data = json.loads(cleaned_response)

            # Create output filenames with company name
            safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_company_name = safe_company_name.replace(' ', '_')

            # Save JSON format
            resume_json_filename = f"outputs/adapted_resume_{safe_company_name}_{language}.json"
            save_json(resume_json_filename, adapted_resume_data)

            # Convert JSON back to text for cover letter and text output
            adapted_resume_text = json_to_resume_text(adapted_resume_data)
            resume_text_filename = f"outputs/adapted_resume_{safe_company_name}_{language}.txt"
            save_text(resume_text_filename, adapted_resume_text)

        except json.JSONDecodeError as e:
            # Fallback: save as text if JSON parsing fails
            print(f"Warning: Could not parse JSON response. Saving as text. Error: {e}")
            safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_company_name = safe_company_name.replace(' ', '_')

            resume_text_filename = f"outputs/adapted_resume_{safe_company_name}_{language}.txt"
            save_text(resume_text_filename, adapted_resume_json)
            adapted_resume_text = adapted_resume_json
            resume_json_filename = None

        # Generate Cover Letter (using text format)
        cover_letter_system = language_prompts.get(language, "You are a professional recruiter. Respond in English.")
        cover_letter_system = cover_letter_system.replace("with valid JSON only", "").replace("con JSON válido", "").replace("mit gültigem JSON", "")

        cover_prompt = format_prompt("prompt_templates/cover_letter_prompt.txt",
                                   resume=adapted_resume_text,
                                   job_offer=job_offer)

        cover_letter = run_llm(cover_prompt, cover_letter_system)
        cover_filename = f"outputs/cover_letter_{safe_company_name}_{language}.txt"
        save_text(cover_filename, cover_letter)

        # Prepare return message
        files_created = [resume_text_filename, cover_filename]
        if resume_json_filename:
            files_created.insert(0, resume_json_filename)

        return {
            'status': 'success',
            'resume_file': resume_text_filename,
            'resume_json_file': resume_json_filename if resume_json_filename else None,
            'cover_letter_file': cover_filename,
            'files_created': files_created,
            'message': f'Resume and cover letter generated successfully for {company_name} in {language}'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error generating documents: {str(e)}'
        }

def main_cli():
    """Original main function for command line usage"""
    resume = load_text("inputs/resume.txt")
    job_offer = load_text("inputs/job_offer.txt")

    # Adapt Resume
    resume_prompt = format_prompt("prompt_templates/resume_prompt.txt", resume=resume, job_offer=job_offer)
    adapted_resume = run_llm(resume_prompt)
    save_text("outputs/adapted_resume.txt", adapted_resume)
    print("✅ Adapted resume generated.")

    # Generate Cover Letter
    cover_prompt = format_prompt("prompt_templates/cover_letter_prompt.txt", resume=adapted_resume, job_offer=job_offer)
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