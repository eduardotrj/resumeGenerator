
# create_resume.py
schema = {
    "name": "str",
    "label": "str",
    "summary": "str",
    "contactInfo": {
        "email": { "type": "string" },
        "phone": { "type": "string" },
        "location": {
            "address": { "type": "string" },
            "postalCode": { "type": "string" },
            "city": { "type": "string" },
            "countryCode": { "type": "string" },
            "region": { "type": "string" }
    }
  },
    "profiles": [{
        "linkedIn": { "type": "string" },
        "github": { "type": "string" },
        "website": { "type": "string" },
        "substack": { "type": "string" },
        "portfolio": { "type": "string" }
  }],
    "work": [{
        "title": { "type": "string" },
        "company": { "type": "string" },
        "startDate": { "type": "string" },
        "endDate": { "type": "string" },
        "summary": { "type": "array", "items": { "type": "string" } }
  }],
    "skills": [{
        "name": { "type": "string" },
        "level": { "type": "string" },
        "keywords": { "type": "array", "items": { "type": "string" } }
    }],
    "languages": [{
        "language": { "type": "string" },
        "fluency": { "type": "string" }
  }],
    "education": [{
        "institution": { "type": "string" },
        "studyType": { "type": "string" },
        "location": { "type": "string" },
        "course": { "type": "string" },
        "startDate": { "type": "string" },
        "endDate": { "type": "string" }
    }],
    "projects": [{
        "name": { "type": "string" },
        "startDate": { "type": "string" },
        "endDate": { "type": "string" },
        "description": { "type": "string" },
        "url": { "type": "string" }
  }],
}

#