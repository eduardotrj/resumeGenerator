
import re
from local_llm_client import run_llm
from utils.file_operations import load_json, save_json, save_text, create_folder_if_not_exists
from utils.prompt_handler import create_adaptation_prompt, create_cover_letter_prompt
from processors.resume_processor import (
    load_adapt_info, load_resume_info, adapt_info_to_text, json_to_resume_text,
    parse_llm_json_response, merge_resume_data, create_safe_filename
)
from generators.html_generator import generate_html_resume
from generators.html_pdf_generator import html_to_pdf
from generators.txt_pdf_generator import TxtToPDF
from db.db import save_generation


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

        # Get form data
        company_name = form_data.get('company_name', '')
        job_offer = form_data.get('job_offer', '')
        language = form_data.get('language', 'English')
        city = form_data.get('city', '')
        country_code = form_data.get('country_code', '')
        name = form_data.get('name', 'Applicant')

        # Select which adaptation data to use based on language
        # In a future version, use it to choose different resume profiles.
        if language == 'German':
            folder = "it_de"

        elif language == 'Spanish':
            folder = "it_es"

        else:
            folder = "it_en"

        # Load base resume data
        resume_data = load_resume_info(folder)

        # Load adaptation data
        adapt_data = load_adapt_info(folder)
        adapt_text = adapt_info_to_text(adapt_data)

        # Create adaptation prompt
        adaptation_prompt, system_message = create_adaptation_prompt(job_offer, adapt_text, language)

        print("🤖 Sending prompt to LLM...")
        adapted_content_json = run_llm(adaptation_prompt, system_message)

        print(f"📝 Raw LLM Response (first 200 chars): {repr(adapted_content_json[:200])}")
        print(f"📏 Response length: {len(adapted_content_json)}")

        # Parse LLM response
        adapted_content, json_parse_success = parse_llm_json_response(adapted_content_json)

        # Create safe filename
        safe_company_name = create_safe_filename(company_name)

        name_person = create_safe_filename(resume_data.get('name', name))

        if json_parse_success and adapted_content:
            # Merge adapted content with base resume
            final_resume = merge_resume_data(resume_data, adapted_content)

            # Check if company folder exists, create if not
            create_folder_if_not_exists("outputs", safe_company_name)
            # Save files
            resume_json_filename = f"outputs/{safe_company_name}/adapted_resume_{safe_company_name}_{language}.json"

            save_json(resume_json_filename, final_resume)
            print(f"💾 JSON file saved: {resume_json_filename}")

            # Convert to text
            adapted_resume_text = json_to_resume_text(final_resume)
            resume_text_filename = f"outputs/{safe_company_name}/adapted_resume_{safe_company_name}_{language}.txt"
            save_text(resume_text_filename, adapted_resume_text)
            print(f"📄 Text file saved: {resume_text_filename}")

            # Generate HTML
            html_filename = generate_html_resume(final_resume, company_name, language, country_code, city, adapt_data)
            if html_filename:
                print(f"🌐 HTML file saved: {html_filename}")
                html_to_pdf(html_filename, f"outputs/{safe_company_name}/{name_person}_resume.pdf")
                save_generation(company_name, job_offer, language, country_code, city)

        else:
            # Fallback for failed JSON parsing
            resume_text_filename = f"outputs/{safe_company_name}/adapted_resume_{safe_company_name}_{language}.txt"
            fallback_text = f"RESUME ADAPTATION FAILED - USING ORIGINAL DATA\n\n"
            fallback_text += f"Original response from LLM:\n{adapted_content_json}\n\n"
            fallback_text += json_to_resume_text(resume_data)

            save_text(resume_text_filename, fallback_text)
            adapted_resume_text = fallback_text
            resume_json_filename = None
            html_filename = None

        # Generate cover letter
        cover_letter_file = _generate_cover_letter(
            company_name, job_offer, adapted_resume_text if 'adapted_resume_text' in locals() else adapt_text,
            language, safe_company_name, name_person
        )

        # Prepare response
        files_created = [resume_text_filename, cover_letter_file]
        if json_parse_success and resume_json_filename:
            files_created.insert(0, resume_json_filename)
        if json_parse_success and html_filename:
            files_created.append(html_filename)

        status_message = "Resume and cover letter generated successfully"
        if not json_parse_success:
            status_message += " (Note: JSON parsing failed, text format used)"

        return {
            'status': 'success',
            'resume_file': resume_text_filename,
            'resume_json_file': resume_json_filename if json_parse_success else None,
            'resume_html_file': html_filename if json_parse_success else None,
            'cover_letter_file': cover_letter_file,
            'files_created': files_created,
            'message': f'{status_message} for {company_name} in {language}'
        }

    except Exception as e:
        print(f"💥 Error in generate_resume_and_cover_letter: {e}")
        return {
            'status': 'error',
            'message': f'Error generating documents: {str(e)}'
        }


def _generate_cover_letter(company_name, job_offer, resume_content, language, safe_company_name, name_person):
    """Generate cover letter using LLM"""
    cover_prompt, cover_system = create_cover_letter_prompt(company_name, job_offer, resume_content, language)

    print("📝 Generating cover letter...")
    cover_letter = run_llm(cover_prompt, cover_system)

    # Remove any company or person details from the cover letter
    # cover_letter = cover_letter.replace(company_name, "[Company Name]").replace(name_person, "[Applicant Name]")
    match = re.search(
        r"(Dear Hiring|Sehr geehrte.*)",
        cover_letter,
        re.IGNORECASE | re.DOTALL)

    if match:
        trimmed = match.group(0)
        cover_letter = cover_letter.replace(trimmed.strip(), "")

    cover_filename = f"outputs/{safe_company_name}/cover_letter_{safe_company_name}_{language}.txt"
    save_text(cover_filename, cover_letter)
    print(f"💌 Cover letter saved: {cover_filename}")

    safe_person_name = create_safe_filename(name_person)
    name_person = name_person.replace("_", " ")
    # company_name = company_name.replace("_", " ")

    conversor = TxtToPDF(font="Arial", font_size=9, title_font_size=16)
    conversor.convert(cover_filename, f"outputs/{safe_company_name}/cover_letter_{safe_person_name}.pdf", title=f"Cover Letter by {name_person}")

    return cover_filename


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

        if not test_connection():
            return False

        response = run_llm(test_prompt, "You must respond with valid JSON only.")
        print(f"📝 Raw response: {repr(response)}")

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
