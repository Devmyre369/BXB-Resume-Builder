
"""
BxB Resume Intelligence — ATS Keyword Analyzer
Version: 1.0.0

Rule-based resume and job-description analysis.
Uses only the Python standard library. No API key or AI model required.

Important:
- The score is an estimated, job-description-specific compatibility indicator,
  not an actual score produced by a recruiter's ATS.
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


# Recommendation messages are intentionally varied by skill category.
# They guide honest resume improvement; they do not invent experience.
_EVIDENCE_RECOMMENDATIONS: dict[str, tuple[str, ...]] = {
    "Programming Languages": (
        "Add a project bullet describing a feature or script you implemented with {keyword}.",
        "Explain a programming problem you solved with {keyword} and what your code did.",
        "Mention the module, function, or workflow where you applied {keyword}; include a result when possible.",
        "Show how you tested or debugged code written in {keyword} in a project or coursework task.",
    ),
    "Web Development": (
        "Identify the page, feature, or API endpoint you built using {keyword}.",
        "Explain how {keyword} contributed to a working web application and what you implemented.",
        "Add a project bullet describing how you tested or improved a feature built with {keyword}.",
        "Describe the specific frontend, backend, or integration task you completed with {keyword}.",
    ),
    "AI and Data Science": (
        "Describe the dataset, experiment, or analysis where you applied {keyword}.",
        "Explain the problem you explored with {keyword}, the method you used, and the result.",
        "Name the model, notebook, or data workflow where you used {keyword}; avoid claiming results you did not measure.",
        "Add a practical project example showing how {keyword} supported data preparation, analysis, or evaluation.",
    ),
    "Databases": (
        "Describe the tables, queries, schema, or data operations you handled using {keyword}.",
        "Explain how you used {keyword} to store, retrieve, update, or validate application data.",
        "Add a concrete database example involving {keyword}, such as a query or a design decision.",
        "Mention the part of your project that depended on {keyword} and what data task it enabled.",
    ),
    "Cloud and DevOps": (
        "Describe what you configured, automated, ran, or deployed with {keyword}.",
        "Identify the project workflow where you applied {keyword} and explain your contribution.",
        "Add a practical example of how {keyword} helped with deployment, environments, or delivery.",
        "Explain a setup or troubleshooting task you completed using {keyword}.",
    ),
    "Tools": (
        "Describe a development task you completed using {keyword}.",
        "Explain how {keyword} supported version control, testing, or collaboration on a project.",
        "Mention a specific workflow where you used {keyword} and what you were responsible for.",
    ),
    "Operating Systems": (
        "Describe a development, command-line, or troubleshooting task you performed in {keyword}.",
        "Give a practical example of how you used {keyword} while building or running software.",
        "Mention the environment or system task involving {keyword} and what you learned or resolved.",
    ),
    "Cybersecurity": (
        "Describe an authorised lab or defensive assessment where you applied {keyword}.",
        "Explain the security question you investigated with {keyword} and the finding or lesson from it.",
        "Add a controlled lab or security project involving {keyword}, including your specific role.",
        "Describe how you used {keyword} in a safe, permitted exercise rather than listing the tool alone.",
    ),
    "Computer Science": (
        "Show how you applied {keyword} in a coding problem, coursework exercise, or project.",
        "Describe a concrete problem you solved using {keyword} and outline your approach.",
        "Add a relevant implementation or coursework example that demonstrates your understanding of {keyword}.",
        "Include a concise example of where {keyword} influenced a design or technical decision.",
    ),
    "Professional Skills": (
        "Describe a real situation where you demonstrated {keyword} and your specific contribution.",
        "Use an example from a team project, hackathon, or coursework to support {keyword}.",
        "Explain the action you took and the outcome that demonstrates {keyword}; quantify it only if you have a real measure.",
        "Add context about who you worked with, what you did, and how {keyword} helped the team.",
    ),
}

_MISSING_RECOMMENDATIONS: dict[str, tuple[str, ...]] = {
    "Programming Languages": (
        "If you have used {keyword}, add the project or coding task where you applied it. Otherwise, try a small exercise before listing it.",
        "Consider building a small, demonstrable program with {keyword} if it is important for this role.",
        "Check whether {keyword} is essential or preferred in the job description, then prioritise learning it if relevant.",
        "Before adding {keyword}, make sure you can explain its basics and show a genuine example of your work.",
    ),
    "Web Development": (
        "If you know {keyword}, describe a feature you built with it. Otherwise, practise with a small working web exercise first.",
        "A simple website, application, or API using {keyword} could help you build demonstrable experience.",
        "Review the role's requirements for {keyword} and prioritise it if it aligns with the type of work you want to do.",
        "Only add {keyword} once you can explain its purpose and your actual level of hands-on experience.",
    ),
    "AI and Data Science": (
        "If you have applied {keyword}, describe the task and how you evaluated the result. Otherwise, begin with a small experiment.",
        "Try a beginner project involving {keyword} and document the data, method, and actual findings.",
        "Build familiarity with {keyword} through a practical exercise before presenting it as an established skill.",
        "Check how relevant {keyword} is to this role before deciding whether it should be your next learning priority.",
    ),
    "Databases": (
        "If you have used {keyword}, include a real query or data-management example. Otherwise, practise with sample data first.",
        "A small application that stores and retrieves data can help you demonstrate relevant knowledge of {keyword}.",
        "Try a practical exercise with {keyword}, such as querying data or designing a small schema, before listing it as a skill.",
        "Review the job's database requirements and learn {keyword} if it is relevant to the work you would be doing.",
    ),
    "Cloud and DevOps": (
        "If you have used {keyword}, describe what you configured or deployed. Otherwise, practise with a test application first.",
        "Try a small deployment or automation exercise with {keyword} and document what you actually completed.",
        "Develop hands-on experience with {keyword} before presenting it as a skill on your resume.",
        "Check the role's infrastructure requirements to decide whether learning {keyword} should be a priority.",
    ),
    "Tools": (
        "If you have used {keyword}, mention the workflow it supported. Otherwise, practise it during a small project.",
        "Use {keyword} in a personal or coursework project so you can describe your actual experience with it.",
        "Check whether {keyword} is important for this internship before choosing it as your next learning task.",
    ),
    "Operating Systems": (
        "If you have worked with {keyword}, include a real development or troubleshooting example.",
        "Try a hands-on exercise involving {keyword} and record what you learned before claiming practical experience.",
        "Practise a relevant command-line or system task in {keyword} if it is needed for this role.",
    ),
    "Cybersecurity": (
        "If you have experience with {keyword}, describe a legitimate lab or defensive exercise. Otherwise, use an authorised learning environment.",
        "Consider a controlled security-learning project involving {keyword} and document your methods and findings.",
        "Build practical knowledge of {keyword} through safe, permitted exercises before listing it as an established skill.",
        "Check whether {keyword} is relevant to the role and focus on fundamentals before claiming hands-on proficiency.",
    ),
    "Computer Science": (
        "If you have studied or applied {keyword}, add a relevant coursework or coding example. Otherwise, practise it first.",
        "Try a small problem-solving exercise involving {keyword} and write down your approach.",
        "Review the core concepts behind {keyword} and prepare to explain them with a genuine example in an interview.",
        "Look for a project or coding challenge where you can apply {keyword} rather than adding it without supporting evidence.",
    ),
    "Professional Skills": (
        "Include {keyword} only when you can support it with a genuine example from teamwork, coursework, or volunteering.",
        "Think of a real situation that demonstrates {keyword}; describe your contribution and the outcome.",
        "Look for an opportunity to practise {keyword} in a team project before presenting it as a demonstrated strength.",
        "Use a specific example to show {keyword} instead of relying on a general claim about your abilities.",
    ),
}


def _build_recommendations(
    items: list[dict[str, str]],
    message_catalogue: dict[str, tuple[str, ...]],
    recommendation_type: str,
) -> list[dict[str, str]]:
    """Build varied, category-aware recommendation messages deterministically."""
    recommendations: list[dict[str, str]] = []
    category_positions: dict[str, int] = {}
    fallback_messages = (
        "Review whether {keyword} is relevant to this role and use a genuine example if you have the skill.",
        "If {keyword} is a skill you have, support it with a project or coursework example; otherwise consider learning it.",
        "Prioritise {keyword} based on the job requirements, and do not claim experience you cannot demonstrate.",
    )
    fallback_position = 0

    for item in items:
        category = item.get("category", "")
        options = message_catalogue.get(category)

        if options:
            position = category_positions.get(category, 0)
            category_positions[category] = position + 1
            message = options[position % len(options)].format(keyword=item["term"])
        else:
            message = fallback_messages[fallback_position % len(fallback_messages)].format(
                keyword=item["term"]
            )
            fallback_position += 1

        recommendations.append({
            "keyword": item["term"],
            "type": recommendation_type,
            "message": message,
        })

    return recommendations


# ============================================================
# ESTIMATED ATS COMPATIBILITY SCORE
# ============================================================
# This is a transparent heuristic, not a score from a real ATS.
# A recognized requirement found in substantive resume text receives full
# credit; a requirement found only as a skill mention receives partial credit;
# a missing requirement receives no credit.
_MATCHED_WEIGHT = 1.0
_NEEDS_EVIDENCE_WEIGHT = 0.4
_MISSING_WEIGHT = 0.0

_SCORE_BANDS: tuple[dict[str, Any], ...] = (
    {
        "minimum": 0,
        "maximum": 24,
        "label": "Bad",
        "description": (
            "Many recognized requirements from this job description are not "
            "currently reflected in your resume. Start with the most relevant "
            "missing skills and genuine project evidence."
        ),
    },
    {
        "minimum": 25,
        "maximum": 39,
        "label": "Moderate",
        "description": (
            "Some role-related keywords appear in your resume, but important "
            "gaps remain. Review missing requirements and build relevant evidence."
        ),
    },
    {
        "minimum": 40,
        "maximum": 54,
        "label": "Needs a Little Improvement",
        "description": (
            "Your resume has a starting level of alignment, but several skills "
            "may be missing or listed without enough supporting detail."
        ),
    },
    {
        "minimum": 55,
        "maximum": 69,
        "label": "Good",
        "description": (
            "Your resume reflects a useful portion of the recognized job "
            "requirements. Strengthen evidence and address the most relevant gaps."
        ),
    },
    {
        "minimum": 70,
        "maximum": 79,
        "label": "Strong",
        "description": (
            "Your resume appears well aligned with many recognized requirements. "
            "Improve the remaining gaps and make project achievements more specific."
        ),
    },
    {
        "minimum": 80,
        "maximum": 89,
        "label": "Great",
        "description": (
            "Your resume shows strong apparent alignment with the recognized "
            "requirements. Review the remaining gaps and keep evidence specific."
        ),
    },
    {
        "minimum": 90,
        "maximum": 100,
        "label": "Top Level",
        "description": (
            "Your resume shows very high alignment with the recognized keywords "
            "in this job description. This does not guarantee ATS ranking or selection; "
            "continue checking accuracy and the quality of your evidence."
        ),
    },
)


def _get_score_category(score: int) -> dict[str, Any]:
    """Return the score band matching a score from 0 to 100."""
    for band in _SCORE_BANDS:
        if band["minimum"] <= score <= band["maximum"]:
            return dict(band)

    # Defensive fallback; the scoring function normally returns 0–100.
    return dict(_SCORE_BANDS[0] if score < 0 else _SCORE_BANDS[-1])


def _calculate_ats_score(
    matched_count: int,
    needs_evidence_count: int,
    missing_count: int,
) -> int:
    """
    Estimate job-specific compatibility using recognized JD keywords.

    Fully evidenced matches receive 1.0 credit; terms needing evidence get
    0.4 credit; absent terms get 0. The result is a heuristic score, not an
    actual ATS ranking or hiring probability.
    """
    total = matched_count + needs_evidence_count + missing_count
    if total <= 0:
        return 0

    weighted_total = (
        matched_count * _MATCHED_WEIGHT
        + needs_evidence_count * _NEEDS_EVIDENCE_WEIGHT
        + missing_count * _MISSING_WEIGHT
    )
    return max(0, min(100, round((weighted_total / total) * 100)))


def _build_priority_improvements(
    matched: list[dict[str, str]],
    needs_evidence: list[dict[str, str]],
    missing: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Build short, job-specific action groups ordered by likely impact."""
    improvements: list[dict[str, Any]] = []

    if missing:
        improvements.append({
            "priority": len(improvements) + 1,
            "type": "missing_requirements",
            "title": "Review missing job requirements",
            "keywords": [item["term"] for item in missing],
            "message": (
                "These recognized keywords appear in the job description but "
                "were not detected in your resume. If you already have these "
                "skills, add truthful supporting details. Otherwise, prioritise "
                "learning only the requirements relevant to your target role; "
                "do not add skills you do not have."
            ),
        })

    if needs_evidence:
        improvements.append({
            "priority": len(improvements) + 1,
            "type": "add_evidence",
            "title": "Turn skill mentions into evidence",
            "keywords": [item["term"] for item in needs_evidence],
            "message": (
                "These skills appear in your resume, but the analyzer did not "
                "find them in the main evidence sections. Where accurate, add "
                "a project, coursework, experience, certification, or achievement "
                "example showing how you used each skill."
            ),
        })

    if matched:
        improvements.append({
            "priority": len(improvements) + 1,
            "type": "strengthen_relevance",
            "title": "Make relevant experience more specific",
            "keywords": [item["term"] for item in matched],
            "message": (
                "Keep the skills already reflected in substantive resume sections, "
                "and strengthen relevant bullets with your action, the problem "
                "you solved, and the outcome. Use numbers only when you can "
                "support them with real results."
            ),
        })

    if not improvements:
        improvements.append({
            "priority": 1,
            "type": "improve_job_alignment",
            "title": "Improve job-description alignment",
            "keywords": [],
            "message": (
                "Review the full job description and compare its responsibilities "
                "with your genuine projects, education, and experience. The current "
                "keyword dictionary may not recognise every relevant requirement."
            ),
        })

    return improvements[:3]


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

    Returns a JSON-friendly dictionary with keyword analysis, score,
    score category, recommendations, and prioritized improvements.

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
            # The term may appear in another resume field, but not in
            # the main evidence sections.
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
            "ats_score": None,
            "score_category": "Unavailable",
            "score_description": (
                "A score cannot be estimated because no supported keywords were "
                "recognized in the supplied job description. Try a more detailed "
                "description or expand the keyword dictionary."
            ),
            "score_method": (
                "Recognized job-description keywords only; a heuristic indicator, "
                "not an actual ATS score."
            ),
            "total_keywords": 0,
            "matched": [],
            "needs_evidence": [],
            "missing": [],
            "recommendations": [],
            "priority_improvements": [],
        }

    # Keyword coverage counts only skills found in substantive sections.
    keyword_coverage = round(
        (len(matched) / total_keywords) * 100
    )

    # Resume keyword presence also includes skills that need stronger evidence.
    resume_keyword_presence = round(
        ((len(matched) + len(needs_evidence)) / total_keywords) * 100
    )

    # Recommendations vary by category and by evidence status.
    recommendations = _build_recommendations(
        needs_evidence,
        _EVIDENCE_RECOMMENDATIONS,
        "strengthen_evidence",
    )
    recommendations.extend(
        _build_recommendations(
            missing,
            _MISSING_RECOMMENDATIONS,
            "review_missing_keyword",
        )
    )

    ats_score = _calculate_ats_score(
        matched_count=len(matched),
        needs_evidence_count=len(needs_evidence),
        missing_count=len(missing),
    )

    score_category = _get_score_category(ats_score)

    priority_improvements = _build_priority_improvements(
        matched=matched,
        needs_evidence=needs_evidence,
        missing=missing,
    )

    return {
        "status": "ok",
        "keyword_coverage_percent": keyword_coverage,
        "resume_keyword_presence_percent": resume_keyword_presence,
        "ats_score": ats_score,
        "score_category": score_category["label"],
        "score_description": score_category["description"],
        "score_range": {
            "minimum": score_category["minimum"],
            "maximum": score_category["maximum"],
        },
        "score_method": (
            "Estimated from recognized keywords in this job description: "
            "substantive-section matches receive full credit, skills needing "
            "evidence receive 40% credit, and missing keywords receive no credit. "
            "This is not an actual ATS score, ATS ranking, or hiring prediction."
        ),
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
        "priority_improvements": priority_improvements,
        "explanation": (
            "Keyword coverage is the percentage of recognized job-description "
            "keywords found in substantive resume sections. Resume keyword "
            "presence also includes keywords that need stronger evidence. The "
            "estimated compatibility score uses those same recognized keywords "
            "with a transparent weighting method. None of these measures is an "
            "actual ATS score or a prediction of shortlisting. Only include skills "
            "you can honestly demonstrate."
        ),
    }
