from django.shortcuts import render

import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .services.ats_analyzer import analyze_job_description
from pathlib import Path

from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.cache import never_cache

@require_POST
def analyze_resume_api(request):
    """
    Analyze a resume against a job description.

    Receives JSON:
    {
        "job_description": "...",
        "resume": {...}
    }

    Returns JSON analysis results.
    """

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "status": "error",
                "message": "Invalid JSON request."
            },
            status=400
        )

    if not isinstance(payload, dict):
        return JsonResponse(
            {
                "status": "error",
                "message": "The request must contain a JSON object."
            },
            status=400
        )

    job_description = payload.get("job_description")
    resume_data = payload.get("resume")

    if not isinstance(job_description, str):
        return JsonResponse(
            {
                "status": "error",
                "message": "Job description must be text."
            },
            status=400
        )

    if len(job_description) > 30000:
        return JsonResponse(
            {
                "status": "error",
                "message": "Job description is too long. Maximum: 30,000 characters."
            },
            status=400
        )

    if not isinstance(resume_data, dict):
        return JsonResponse(
            {
                "status": "error",
                "message": "Resume data must be a JSON object."
            },
            status=400
        )

    result = analyze_job_description(
        job_description=job_description,
        resume_data=resume_data
    )

    if result.get("status") == "error":
        return JsonResponse(result, status=400)

    return JsonResponse(result)


def home(request):
    return render(request, 'resume_builder/home.html')


def editor(request):
    return render(request, 'resume_builder/editor.html')



@never_cache
def service_worker(request):
    """Serve the PWA service worker from the website root."""

    worker_path = (
        Path(__file__).resolve().parent
        / "static"
        / "resume_builder"
        / "service-worker.js"
    )

    try:
        source = worker_path.read_text(encoding="utf-8")
    except OSError:
        return HttpResponseNotFound(
            "PWA service worker is not installed."
        )

    response = HttpResponse(
        source,
        content_type="application/javascript; charset=utf-8",
    )

    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"

    return response