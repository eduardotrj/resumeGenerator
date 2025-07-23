import os
import json


def load_text(file_path):
    """Load text content from a file"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_json(file_path):
    """Load JSON data from a file"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_text(file_path, content):
    """Save text content to a file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.strip())


def save_json(file_path, data):
    """Save data as JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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
            "contactInfo": {"email": "string", "phone": "string", "location": {}},
            "profiles": [{"linkedIn": "string", "github": "string"}],
            "work": [{"title": "string", "company": "string", "summary": ["string"]}],
            "skills": [{"category": "string", "items": ["string"]}]
        }, indent=2)