import os
from utils.file_operations import load_text


def generate_html_resume(adapted_resume_data, company_name, language, country_code, city):
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
        html_template = load_text(template_path)

        # Generate each section
        profiles_html = _generate_profiles_html(adapted_resume_data)
        work_html = _generate_work_html(adapted_resume_data)
        skills_html = _generate_skills_html(adapted_resume_data)
        projects_html = _generate_projects_html(adapted_resume_data)
        education_html = _generate_education_html(adapted_resume_data)

        # Replace content in template
        html_content = _replace_template_content(
            html_template,
            adapted_resume_data,
            profiles_html,
            work_html,
            skills_html,
            projects_html,
            education_html,
            country_code,
            city
        )

        # Save HTML file
        html_filename = _save_html_file(html_content, company_name, language)
        return html_filename

    except Exception as e:
        print(f"Error generating HTML resume: {e}")
        return None


def _generate_profiles_html(resume_data):
    """Generate HTML for profiles section"""
    profiles_html = ""
    if 'profiles' in resume_data and resume_data['profiles']:
        for profile in resume_data['profiles']:
            for key, value in profile.items():
                if value and key.lower() in ['linkedin', 'github', 'portfolio', 'substack', 'codepen']:
                    icon_map = {
                        'linkedin': '💼', 'github': '🐱', 'portfolio': '💻',
                        'substack': '🗞️', 'codepen': '🎨'
                    }
                    icon = icon_map.get(key.lower(), '🔗')
                    profiles_html += f'''
                <a href="{value}" class="profile-link" data-type="{key.lower()}">
                    <span>{icon}</span> {key.capitalize()}
                </a>'''
    return profiles_html


def _generate_work_html(resume_data):
    """Generate HTML for work experience with consolidation"""
    work_html = ""
    if 'work' in resume_data and resume_data['work']:
        # Consolidate duplicate jobs
        consolidated_jobs = _consolidate_work_experience(resume_data['work'])

        # Generate HTML for each job
        for job in consolidated_jobs.values():
            date_range = _format_date_range(job)
            summary_html = _format_summary_list(job.get('summary', []))

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
    return work_html


def _consolidate_work_experience(work_list):
    """Consolidate jobs with same title and company"""
    consolidated_jobs = {}

    for job in work_list:
        job_key = f"{job.get('title', '')}__{job.get('company', '')}"

        if job_key in consolidated_jobs:
            # Merge summaries
            existing_summary = consolidated_jobs[job_key].get('summary', [])
            new_summary = job.get('summary', [])
            for item in new_summary:
                if item not in existing_summary:
                    existing_summary.append(item)
            consolidated_jobs[job_key]['summary'] = existing_summary

            # Update date range
            _update_date_range(consolidated_jobs[job_key], job)
        else:
            consolidated_jobs[job_key] = job.copy()

    return consolidated_jobs


def _generate_skills_html(resume_data):
    """Generate HTML for skills section, filtering empty categories"""
    skills_html = ""
    if 'skills' in resume_data and resume_data['skills']:
        skills_list_items = []

        for skill_category in resume_data['skills']:
            if 'category' in skill_category and 'items' in skill_category:
                items = skill_category['items']
                if items and len(items) > 0:
                    # Filter out empty items
                    filtered_items = [item.strip() for item in items if item and item.strip()]

                    if filtered_items:
                        skills_items = ' | '.join([f'<span class="keyword">{skill}</span>' for skill in filtered_items])
                        skills_list_items.append(f'''
                    <li class="skill-item">
                        <div class="skill-name allInLine boldText">{skill_category['category']}:</div>
                        <div class="skill-keywords allInLine regularText">
                            {skills_items}
                        </div>
                    </li>''')

        if skills_list_items:
            skills_html = '<ul class="skills-list">' + ''.join(skills_list_items) + '</ul>'

    return skills_html


def _generate_projects_html(resume_data):
    """Generate HTML for projects section"""
    projects_html = ""
    if 'projects' in resume_data and resume_data['projects']:
        for project in resume_data['projects']:
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
    return projects_html


def _generate_education_html(resume_data):
    """Generate HTML for education section"""
    education_html = ""
    if 'education' in resume_data and resume_data['education']:
        for edu in resume_data['education']:
            location = edu.get('location', {})
            location_str = ""
            if isinstance(location, dict):
                location_str = f"{location.get('city', '')}, {location.get('countryCode', '')}"
            else:
                location_str = str(location)

            education_html += f'''
                <div class="education-item item">
                    <div class="studyType boldText allInLine">{edu.get('studyType', '')}</div><span> | </span>
                    <div class="work-title boldText allInLine">{edu.get('course', '')}</div><span> | </span>
                    <div class="education-institution regularText allInLine">{edu.get('institution', '')}</div><span> | </span>
                    <div class="date-range regularText allInLine">{edu.get('startDate', '')} - {edu.get('endDate', '')}</div><span> | </span>
                    <div class="location regularText allInLine">{location_str}</div>
                </div>'''
    return education_html


def _format_date_range(job):
    """Format date range for a job"""
    if 'startDate' in job and 'endDate' in job:
        return f"{job['startDate']} - {job['endDate']}"
    elif 'dates' in job:
        return job['dates']
    return ""


def _format_summary_list(summary_items):
    """Format summary items as HTML list"""
    return "".join([f"<li>{item}</li>" for item in summary_items])


def _update_date_range(existing_job, new_job):
    """Update date range when consolidating jobs"""
    existing_start = existing_job.get('startDate', '')
    existing_end = existing_job.get('endDate', '')
    new_start = new_job.get('startDate', '')
    new_end = new_job.get('endDate', '')

    if new_start and (not existing_start or new_start < existing_start):
        existing_job['startDate'] = new_start
    if new_end and (not existing_end or new_end > existing_end):
        existing_job['endDate'] = new_end


def _replace_template_content(html_template, resume_data, profiles_html, work_html, skills_html, projects_html, education_html, country_code, city):
    """Replace all content in the HTML template"""
    html_content = html_template

    # Basic information
    html_content = html_content.replace('John Doe', resume_data.get('name', 'John Doe'))
    html_content = html_content.replace('john.doe@example.com', resume_data.get('contactInfo', {}).get('email', ''))
    html_content = html_content.replace('+1 (555) 123-4567', resume_data.get('contactInfo', {}).get('phone', ''))

    # Location
    location_info = resume_data.get('contactInfo', {}).get('location', {})

    if country_code and city:
        location_text = f"{city}, {country_code}"
    elif isinstance(location_info, dict):
        location_text = f"{location_info.get('city', '')}, {location_info.get('countryCode', '')}"
    else:
        location_text = str(location_info)
    html_content = html_content.replace('San Francisco, CA', location_text)

    # Replace sections
    html_content = _replace_section(html_content, 'profiles', profiles_html)
    html_content = _replace_section(html_content, 'work', work_html)

    if skills_html:
        html_content = _replace_section(html_content, 'skills', skills_html, 'skills-grid')
    else:
        html_content = _remove_skills_section(html_content)

    if projects_html:
        html_content = _replace_section(html_content, 'projects', projects_html)

    if education_html:
        html_content = _replace_section(html_content, 'education', education_html)

    return html_content


def _replace_section(html_content, section_id, section_html, section_class=None):
    """Replace a specific section in the HTML"""
    if section_class:
        start_marker = f'<div class="{section_class}" id="{section_id}">'
    else:
        start_marker = f'<div id="{section_id}">'

    start_pos = html_content.find(start_marker)
    if start_pos != -1:
        end_pos = html_content.find('</div>', start_pos) + 6
        if end_pos != -1:
            replacement = f'{start_marker}{section_html}\n                    </div>'
            html_content = html_content[:start_pos] + replacement + html_content[end_pos:]

    return html_content


def _remove_skills_section(html_content):
    """Remove the entire skills section if no skills to display"""
    section_start = html_content.find('<section class="section">\n                    <h2>Technical Skills</h2>')
    if section_start != -1:
        section_end = html_content.find('</section>', section_start) + 10
        if section_end != -1:
            html_content = html_content[:section_start] + html_content[section_end:]
    return html_content


def _save_html_file(html_content, company_name, language):
    """Save the HTML content to a file"""
    from processors.resume_processor import create_safe_filename

    safe_company_name = create_safe_filename(company_name)
    html_filename = f"outputs/{safe_company_name}/resume_{safe_company_name}_{language}.html"
    os.makedirs(os.path.dirname(html_filename), exist_ok=True)

    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_filename