import json
from utils.file_operations import load_json, save_json, save_text


def load_adapt_info():
    """Load the work experience and skills to adapt from adapt_info.json"""
    try:
        return load_json("inputs/it_jobs/adapt_info.json")
    except FileNotFoundError:
        # Return default structure if file doesn't exist
        return {
            "work": [],
            "skills": []
        }


def adapt_info_to_text(adapt_data):
    """Convert adapt_info JSON to formatted text for work experience and skills only"""
    text = ""

    # Work Experience section
    if 'work' in adapt_data and adapt_data['work']:
        text += "WORK EXPERIENCE TO ADAPT:\n"
        for job in adapt_data['work']:
            text += f"\n{job['title']} at {job['company']}"
            if 'startDate' in job and 'endDate' in job:
                text += f" ({job['startDate']} - {job['endDate']})"
            text += "\n"

            if 'summary' in job:
                for point in job['summary']:
                    text += f"• {point}\n"
        text += "\n"

    # Skills section
    if 'skills' in adapt_data and adapt_data['skills']:
        text += "SKILLS TO ADAPT:\n"
        for skill_category in adapt_data['skills']:
            if 'category' in skill_category and 'items' in skill_category:
                text += f"\n{skill_category['category']}:\n"
                for skill in skill_category['items']:
                    text += f"• {skill}\n"
        text += "\n"

    return text


def json_to_resume_text(resume_data):
    """Convert resume JSON to formatted text"""
    resume_text = f"{resume_data['name']}\n{resume_data['label']}\n\n"
    resume_text += f"Contact: {resume_data['contactInfo']['email']} | {resume_data['contactInfo']['phone']}\n"
    resume_text += f"Location: {resume_data['contactInfo']['location']['city']}, {resume_data['contactInfo']['location']['countryCode']}\n\n"

    if 'profiles' in resume_data and resume_data['profiles']:
        profile = resume_data['profiles'][0]
        resume_text += "Profiles:\n"
        for key, value in profile.items():
            resume_text += f"{key.capitalize()}: {value}\n"
        resume_text += "\n"

    if 'summary' in resume_data:
        resume_text += "Summary:\n"
        resume_text += f"{resume_data['summary']}\n\n"

    if 'work' in resume_data:
        resume_text += "Work Experience:\n"
        for job in resume_data['work']:
            resume_text += f"\n{job['title']} at {job['company']}"
            if 'startDate' in job and 'endDate' in job:
                resume_text += f" ({job['startDate']} - {job['endDate']})"
            resume_text += "\n"

            if 'summary' in job:
                for point in job['summary']:
                    resume_text += f"• {point}\n"

    return resume_text


def parse_llm_json_response(response_text):
    """Parse LLM response and extract JSON with error handling"""
    try:
        if not response_text or response_text.strip() == "":
            raise ValueError("Empty response from LLM")

        # Clean the response to extract JSON
        cleaned_response = response_text.strip()

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

        return adapted_content, True

    except (json.JSONDecodeError, ValueError) as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"📝 Raw response: {repr(response_text)}")
        return None, False


def merge_resume_data(base_resume, adapted_content):
    """Merge adapted work/skills with base resume data"""
    final_resume = base_resume.copy()

    if 'work' in adapted_content:
        final_resume['work'] = adapted_content['work']
        print(f"📊 Work experience adapted: {len(adapted_content['work'])} jobs")

    if 'skills' in adapted_content:
        final_resume['skills'] = adapted_content['skills']
        print(f"🎯 Skills adapted: {len(adapted_content['skills'])} categories")

    return final_resume


def create_safe_filename(company_name):
    """Create a safe filename from company name"""
    safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return safe_name.replace(' ', '_')