
"""
BxB Resume Intelligence — ATS Keyword Analyzer
Version: 1.0.0

Rule-based resume and job-description analysis.
Uses only the Python standard library. No API key or AI model required.

Important:
- Keyword coverage is not an actual ATS score.
- Missing keywords must not be added unless the student has the
  relevant skills or experience.
"""

import re
from typing import Any


# Each entry contains:
# (canonical keyword, category, aliases)
#
# Add new keywords here as the analyzer grows.

KEYWORD_DICTIONARY = (
    # Programming languages
    ("Python", "Programming Languages", ("Python",)),
    ("Java", "Programming Languages", ("Java",)),
    ("C++", "Programming Languages", ("C++", "C plus plus", "CPP")),
    ("C#", "Programming Languages", ("C#", "C sharp")),
    (
        "C",
        "Programming Languages",
        ("C programming", "C language", "programming in C"),
    ),
    ("JavaScript", "Programming Languages", ("JavaScript", "JS")),
    ("TypeScript", "Programming Languages", ("TypeScript",)),
    (
        "SQL",
        "Programming Languages",
        ("SQL", "Structured Query Language"),
    ),
    ("PHP", "Programming Languages", ("PHP",)),
    ("Bash", "Programming Languages", ("Bash", "Shell scripting")),

    # Web development
    ("HTML", "Web Development", ("HTML", "HTML5")),
    ("CSS", "Web Development", ("CSS", "CSS3")),
    ("React", "Web Development", ("React", "React.js", "ReactJS")),
    ("Next.js", "Web Development", ("Next.js", "NextJS")),
    ("Node.js", "Web Development", ("Node.js", "NodeJS")),
    ("Express.js", "Web Development", ("Express.js", "ExpressJS")),
    ("Django", "Web Development", ("Django",)),
    ("Flask", "Web Development", ("Flask",)),
    ("FastAPI", "Web Development", ("FastAPI", "Fast API")),
    (
        "REST API",
        "Web Development",
        ("REST API", "REST APIs", "RESTful API"),
    ),
    ("GraphQL", "Web Development", ("GraphQL",)),

    # Artificial intelligence and data science
    (
        "Artificial Intelligence",
        "AI and Data Science",
        ("Artificial Intelligence", "AI"),
    ),
    ("Machine Learning", "AI and Data Science", ("Machine Learning", "ML")),
    ("Deep Learning", "AI and Data Science", ("Deep Learning",)),
    (
        "Natural Language Processing",
        "AI and Data Science",
        ("Natural Language Processing", "NLP"),
    ),
    ("Computer Vision", "AI and Data Science", ("Computer Vision",)),
    (
        "Data Analysis",
        "AI and Data Science",
        ("Data Analysis", "Data Analytics"),
    ),
    (
        "Data Visualization",
        "AI and Data Science",
        ("Data Visualization", "Data Visualisation"),
    ),
    ("NumPy", "AI and Data Science", ("NumPy",)),
    ("Pandas", "AI and Data Science", ("Pandas",)),
    (
        "Scikit-learn",
        "AI and Data Science",
        ("Scikit-learn", "Scikit learn", "sklearn"),
    ),
    ("PyTorch", "AI and Data Science", ("PyTorch",)),
    ("TensorFlow", "AI and Data Science", ("TensorFlow", "Tensor Flow")),
    ("Statistics", "AI and Data Science", ("Statistics", "Statistical Analysis")),

    # Databases
    ("MySQL", "Databases", ("MySQL",)),
    ("PostgreSQL", "Databases", ("PostgreSQL", "Postgres")),
    ("SQLite", "Databases", ("SQLite",)),
    ("MongoDB", "Databases", ("MongoDB", "Mongo DB")),
    ("Redis", "Databases", ("Redis",)),
    (
        "Database Design",
        "Databases",
        ("Database Design", "Database Schema Design"),
    ),
    ("DBMS", "Computer Science", ("DBMS", "Database Management Systems")),

    # Cloud and development operations
    ("AWS", "Cloud and DevOps", ("AWS", "Amazon Web Services")),
    (
        "Microsoft Azure",
        "Cloud and DevOps",
        ("Microsoft Azure", "Azure"),
    ),
    (
        "Google Cloud",
        "Cloud and DevOps",
        ("Google Cloud", "Google Cloud Platform", "GCP"),
    ),
    ("Docker", "Cloud and DevOps", ("Docker",)),
    ("Kubernetes", "Cloud and DevOps", ("Kubernetes", "K8s")),
    (
        "CI/CD",
        "Cloud and DevOps",
        ("CI/CD", "Continuous Integration", "Continuous Deployment"),
    ),
    ("Git", "Tools", ("Git",)),
    ("GitHub", "Tools", ("GitHub",)),
    ("Linux", "Operating Systems", ("Linux",)),
    ("Jenkins", "Cloud and DevOps", ("Jenkins",)),

    # Cybersecurity
    (
        "Cybersecurity",
        "Cybersecurity",
        ("Cybersecurity", "Cyber Security", "Information Security"),
    ),
    (
        "Penetration Testing",
        "Cybersecurity",
        ("Penetration Testing", "Pen Testing", "Pentesting"),
    ),
    (
        "Vulnerability Assessment",
        "Cybersecurity",
        ("Vulnerability Assessment", "Vulnerability Analysis"),
    ),
    ("OWASP", "Cybersecurity", ("OWASP",)),
    ("Burp Suite", "Cybersecurity", ("Burp Suite",)),
    ("Network Security", "Cybersecurity", ("Network Security",)),
    (
        "Cryptography",
        "Cybersecurity",
        ("Cryptography", "Encryption"),
    ),
    (
        "Secure Coding",
        "Cybersecurity",
        ("Secure Coding", "Secure Software Development"),
    ),

    # Computer science
    (
        "Data Structures",
        "Computer Science",
        ("Data Structures", "Data Structure"),
    ),
    (
        "Algorithms",
        "Computer Science",
        ("Algorithms", "Algorithm Design"),
    ),
    (
        "Object-Oriented Programming",
        "Computer Science",
        ("Object-Oriented Programming", "Object Oriented Programming", "OOP"),
    ),
    (
        "Operating Systems",
        "Computer Science",
        ("Operating Systems", "Operating System"),
    ),
    (
        "Computer Networks",
        "Computer Science",
        ("Computer Networks", "Computer Networking"),
    ),
    (
        "System Design",
        "Computer Science",
        ("System Design", "Software Architecture"),
    ),
    (
        "Distributed Systems",
        "Computer Science",
        ("Distributed Systems", "Distributed System"),
    ),

    # Professional skills and methodologies
    (
        "Communication",
        "Professional Skills",
        ("Communication", "Communication Skills"),
    ),
    (
        "Leadership",
        "Professional Skills",
        ("Leadership", "Team Leadership"),
    ),
    (
        "Teamwork",
        "Professional Skills",
        ("Teamwork", "Team Collaboration", "Collaboration"),
    ),
    (
        "Problem-Solving",
        "Professional Skills",
        ("Problem-Solving", "Problem Solving"),
    ),
    ("Agile", "Professional Skills", ("Agile", "Agile Methodology")),
    ("Scrum", "Professional Skills", ("Scrum",)),
    (
        "Project Management",
        "Professional Skills",
        ("Project Management",),
    ),
)


def _to_searchable_text(value: Any) -> str:
    """
    Convert nested resume values into searchable text.

    Supports strings, numbers, lists, tuples and dictionaries.
    Dictionary keys are ignored because they are usually field names,
    not resume content.
    """
    if value is None or isinstance(value, bool):
        return ""

    if isinstance(value, (str, int, float)):
        return str(value)

    if isinstance(value, dict):
        return " ".join(
            _to_searchable_text(item)
            for item in value.values()
        )

    if isinstance(value, (list, tuple, set)):
        return " ".join(
            _to_searchable_text(item)
            for item in value
        )

    return ""


def _contains_alias(text: str, aliases: tuple[str, ...]) -> bool:
    """
    Check aliases using case-insensitive term boundaries.

    Examples:
    - Java does not match JavaScript.
    - React matches React.js.
    - C++ matches C++ without treating plus signs as regex syntax.
    """
    if not text:
        return False

    for alias in aliases:
        words = alias.strip().split()

        if not words:
            continue

        escaped_words = [re.escape(word) for word in words]
        pattern_text = r"\s+".join(escaped_words)

        pattern = re.compile(
            rf"(?<![a-zA-Z0-9]){pattern_text}(?![a-zA-Z0-9])",
            re.IGNORECASE,
        )

        if pattern.search(text):
            return True

    return False


def _section_text(resume: dict[str, Any], keys: tuple[str, ...]) -> str:
    """Combine selected resume sections into one searchable string."""
    return " ".join(
        _to_searchable_text(resume.get(key))
        for key in keys
    )


def analyze_job_description(
    job_description: str,
    resume_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Analyze recognized job-description keywords against a resume.

    Expected resume_data keys can include:
        summary
        skills
        education
        project or projects
        experience
        certifications
        achievements

    Returns a JSON-friendly dictionary with:
        status
        keyword_coverage_percent
        resume_keyword_presence_percent
        matched
        needs_evidence
        missing
        recommendations
        explanation

    This function does not save resume data or make hiring predictions.
    """

    if not isinstance(job_description, str) or not job_description.strip():
        return {
            "status": "error",
            "message": "Paste a job description before running the analysis.",
        }

    if not isinstance(resume_data, dict):
        return {
            "status": "error",
            "message": "Resume data must be provided as a dictionary.",
        }

    all_resume_text = _to_searchable_text(resume_data)

    if not all_resume_text.strip():
        return {
            "status": "error",
            "message": "Your resume appears to be empty. Add resume details first.",
        }

    # Evidence sections help distinguish a demonstrated skill from
    # a keyword that appears only in a skills list.
    evidence_text = _section_text(
        resume_data,
        (
            "summary",
            "experience",
            "education",
            "project",
            "projects",
            "certifications",
            "achievements",
        ),
    )

    skills_text = _section_text(resume_data, ("skills",))

    matched: list[dict[str, str]] = []
    needs_evidence: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []

    for term, category, aliases in KEYWORD_DICTIONARY:
        # Only consider keywords that appear in the supplied job description.
        if not _contains_alias(job_description, aliases):
            continue

        item = {
            "term": term,
            "category": category,
        }

        if _contains_alias(evidence_text, aliases):
            matched.append(item)

        elif _contains_alias(skills_text, aliases):
            needs_evidence.append(item)

        elif _contains_alias(all_resume_text, aliases):
            # For example, the term may appear in another resume field,
            # but not in the main evidence sections.
            needs_evidence.append(item)

        else:
            missing.append(item)

    total_keywords = len(matched) + len(needs_evidence) + len(missing)

    if total_keywords == 0:
        return {
            "status": "no_keywords",
            "message": (
                "No supported keywords were detected in this job description. "
                "Try a more detailed description or expand the keyword dictionary."
            ),
            "keyword_coverage_percent": 0,
            "resume_keyword_presence_percent": 0,
            "total_keywords": 0,
            "matched": [],
            "needs_evidence": [],
            "missing": [],
            "recommendations": [],
        }

    # This is a transparent keyword-coverage measure, not an ATS prediction.
    keyword_coverage = round(
        (len(matched) / total_keywords) * 100
    )

    # This second measure includes terms present in the resume but needing
    # stronger evidence. It is not a hiring probability either.
    resume_keyword_presence = round(
        ((len(matched) + len(needs_evidence)) / total_keywords) * 100
    )

    recommendations = []

    for item in needs_evidence:
        recommendations.append({
            "keyword": item["term"],
            "type": "strengthen_evidence",
            "message": (
                f"Your resume mentions {item['term']}, but could benefit "
                "from a concrete example in a relevant project, experience, "
                "coursework or certification section."
            ),
        })

    for item in missing:
        recommendations.append({
            "keyword": item["term"],
            "type": "review_missing_keyword",
            "message": (
                f"Review {item['term']}: include it only if you genuinely "
                "have the relevant skill or experience. Consider gaining "
                "the skill before claiming it."
            ),
        })

    return {
        "status": "ok",
        "keyword_coverage_percent": keyword_coverage,
        "resume_keyword_presence_percent": resume_keyword_presence,
        "total_keywords": total_keywords,
        "counts": {
            "matched": len(matched),
            "needs_evidence": len(needs_evidence),
            "missing": len(missing),
        },
        "matched": matched,
        "needs_evidence": needs_evidence,
        "missing": missing,
        "recommendations": recommendations,
        "explanation": (
            "Keyword coverage is the percentage of recognized job-description "
            "keywords found in substantive resume sections. Resume keyword "
            "presence also includes keywords that need stronger evidence. "
            "Neither measure is an actual ATS score or a prediction of "
            "shortlisting. Only include skills you can honestly demonstrate."
        ),
    }
