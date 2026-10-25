
/*
 * ============================================================
 * BxB Resume Intelligence — Frontend Connector
 * Version: 1.0.0
 *
 * Responsibilities:
 * 1. Read the current resume from the existing editor.
 * 2. Send the job description and resume to Django.
 * 3. Include the Django CSRF token.
 * 4. Render keyword analysis and recommendations safely.
 *
 * Core analysis is performed by Python, not JavaScript.
 * ============================================================
 */

(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", initializeAnalyzer);

    function initializeAnalyzer() {
        const panel = document.getElementById("resumeIntelligencePanel");

        if (!panel) {
            console.error(
                "BxB Resume Intelligence: analysis panel was not found."
            );
            return;
        }

        const analyzeButton = document.getElementById("riAnalyzeButton");
        const jobDescriptionInput = document.getElementById("riJobDescription");
        const statusElement = document.getElementById("riStatus");
        const resultsElement = document.getElementById("riResults");

        if (
            !analyzeButton ||
            !jobDescriptionInput ||
            !statusElement ||
            !resultsElement
        ) {
            console.error(
                "BxB Resume Intelligence: required interface elements are missing."
            );
            return;
        }

        analyzeButton.addEventListener("click", analyzeCurrentResume);

        // Ctrl+Enter / Cmd+Enter runs the analysis when the job description
        // textarea is focused.
        jobDescriptionInput.addEventListener("keydown", function (event) {
            if (
                event.key === "Enter" &&
                (event.ctrlKey || event.metaKey)
            ) {
                event.preventDefault();
                analyzeCurrentResume();
            }
        });

        async function analyzeCurrentResume() {
            const jobDescription = jobDescriptionInput.value.trim();

            if (!jobDescription) {
                showStatus(
                    "Paste a job description before running the analysis."
                );
                jobDescriptionInput.focus();
                return;
            }

            if (jobDescription.length > 30000) {
                showStatus(
                    "The job description is too long. Maximum: 30,000 characters."
                );
                return;
            }

            if (
                !window.BxBResumeBuilder ||
                typeof window.BxBResumeBuilder.getResumeDataForAnalysis !== "function"
            ) {
                showStatus(
                    "The resume editor is not ready. Refresh the page and try again."
                );
                console.error(
                    "BxB Resume Intelligence: resume data interface is unavailable."
                );
                return;
            }

            let resumeData;

            try {
                resumeData =
                    window.BxBResumeBuilder.getResumeDataForAnalysis();
            } catch (error) {
                console.error("Unable to read resume data:", error);
                showStatus(
                    "Could not read the current resume. Check the editor and try again."
                );
                return;
            }

            if (!resumeData || typeof resumeData !== "object") {
                showStatus("Resume data is unavailable. Complete your resume first.");
                return;
            }

            const analysisUrl = panel.dataset.analysisUrl;

            if (!analysisUrl) {
                showStatus(
                    "The analysis endpoint is not configured. Check editor.html."
                );
                return;
            }

            const csrfToken = getCsrfToken();

            if (!csrfToken) {
                showStatus(
                    "Security token is missing. Refresh the page and try again."
                );
                console.error(
                    "BxB Resume Intelligence: Django CSRF token was not found."
                );
                return;
            }

            setLoading(true);
            showStatus("Analyzing your resume against the job description...");
            resultsElement.hidden = true;

            try {
                const response = await fetch(analysisUrl, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: JSON.stringify({
                        job_description: jobDescription,
                        resume: resumeData
                    })
                });

                const result = await parseJsonResponse(response);

                if (!response.ok) {
                    throw new Error(
                        result.message ||
                        "The analysis request failed. Please try again."
                    );
                }

                if (result.status === "error") {
                    throw new Error(
                        result.message || "Unable to analyze this resume."
                    );
                }

                if (result.status === "no_keywords") {
                    renderResults(result);
                    showStatus(
                        result.message ||
                        "No supported keywords were found in this job description."
                    );
                    return;
                }

                if (result.status !== "ok") {
                    throw new Error(
                        result.message || "The server returned an unexpected response."
                    );
                }

                renderResults(result);

                showStatus(
                    "Analysis complete. Review the results before editing your resume."
                );

            } catch (error) {
                console.error("BxB Resume Intelligence error:", error);

                showStatus(
                    error.message ||
                    "Something went wrong during analysis. Please try again."
                );

            } finally {
                setLoading(false);
            }
        }

        function getCsrfToken() {
            const csrfInput = document.querySelector(
                '#riCsrfForm input[name="csrfmiddlewaretoken"]'
            );

            if (csrfInput && csrfInput.value) {
                return csrfInput.value;
            }

            // Fallback for pages where a CSRF form input is not available.
            const cookie = document.cookie
                .split("; ")
                .find(item => item.startsWith("csrftoken="));

            return cookie
                ? decodeURIComponent(cookie.substring("csrftoken=".length))
                : "";
        }

        async function parseJsonResponse(response) {
            const contentType = response.headers.get("content-type") || "";

            if (!contentType.toLowerCase().includes("application/json")) {
                if (response.status === 403) {
                    throw new Error(
                        "Django rejected the request. Refresh the page and check CSRF configuration."
                    );
                }

                if (response.status === 404) {
                    throw new Error(
                        "Analysis endpoint not found. Check resume_builder/urls.py."
                    );
                }

                throw new Error(
                    "The server returned an unexpected response. Check the Django terminal."
                );
            }

            try {
                return await response.json();
            } catch (error) {
                throw new Error("The server returned invalid JSON.");
            }
        }

        function renderResults(result) {
            const matched = Array.isArray(result.matched)
                ? result.matched
                : [];

            const needsEvidence = Array.isArray(result.needs_evidence)
                ? result.needs_evidence
                : [];

            const missing = Array.isArray(result.missing)
                ? result.missing
                : [];

            const recommendations = Array.isArray(result.recommendations)
                ? result.recommendations
                : [];

            setText(
                "riCoverage",
                formatPercent(result.keyword_coverage_percent)
            );

            setText(
                "riPresence",
                formatPercent(result.resume_keyword_presence_percent)
            );

            setText(
                "riTotal",
                formatNumber(result.total_keywords)
            );

            setText("riMatchedCount", `(${matched.length})`);
            setText("riEvidenceCount", `(${needsEvidence.length})`);
            setText("riMissingCount", `(${missing.length})`);

            renderKeywordList(
                "riMatched",
                "riMatchedEmpty",
                matched,
                "No keywords matched with substantive resume evidence."
            );

            renderKeywordList(
                "riEvidence",
                "riEvidenceEmpty",
                needsEvidence,
                "No keywords currently need stronger evidence."
            );

            renderKeywordList(
                "riMissing",
                "riMissingEmpty",
                missing,
                "No recognized job-description keywords are missing."
            );

            renderRecommendations(recommendations);

            setText(
                "riExplanation",
                result.explanation ||
                "Keyword coverage is a comparison against the analyzer's supported vocabulary, not a prediction of ATS ranking or shortlisting."
            );

            document.getElementById("riResults").hidden = false;
        }

        function renderKeywordList(listId, emptyId, items, emptyMessage) {
            const list = document.getElementById(listId);
            const emptyMessageElement = document.getElementById(emptyId);

            if (!list || !emptyMessageElement) return;

            list.replaceChildren();

            items.forEach(function (item) {
                const label = typeof item === "string"
                    ? item
                    : item && typeof item.term === "string"
                        ? item.term
                        : "";

                if (!label) return;

                const listItem = document.createElement("li");

                // textContent prevents job descriptions or keywords from
                // injecting HTML into the page.
                listItem.textContent = label;
                list.appendChild(listItem);
            });

            const hasItems = list.children.length > 0;

            emptyMessageElement.textContent = emptyMessage;
            emptyMessageElement.hidden = hasItems;
            list.hidden = !hasItems;
        }

        function renderRecommendations(recommendations) {
            const list = document.getElementById("riRecommendations");
            const emptyMessage = document.getElementById(
                "riRecommendationsEmpty"
            );

            if (!list || !emptyMessage) return;

            list.replaceChildren();

            recommendations.forEach(function (recommendation) {
                if (
                    !recommendation ||
                    typeof recommendation.message !== "string"
                ) {
                    return;
                }

                const item = document.createElement("li");
                const title = document.createElement("strong");
                const message = document.createElement("span");

                title.textContent = recommendation.keyword
                    ? recommendation.keyword + ": "
                    : "";

                message.textContent = recommendation.message;

                item.appendChild(title);
                item.appendChild(message);
                list.appendChild(item);
            });

            const hasItems = list.children.length > 0;

            emptyMessage.textContent =
                "No additional recommendations are needed for the recognized keywords.";

            emptyMessage.hidden = hasItems;
            list.hidden = !hasItems;
        }

        function formatPercent(value) {
            const number = Number(value);

            if (!Number.isFinite(number)) {
                return "—";
            }

            return `${Math.max(0, Math.min(100, number))}%`;
        }

        function formatNumber(value) {
            const number = Number(value);

            return Number.isFinite(number) && number >= 0
                ? String(Math.floor(number))
                : "0";
        }

        function setText(id, value) {
            const element = document.getElementById(id);

            if (element) {
                element.textContent = value;
            }
        }

        function showStatus(message) {
            statusElement.textContent = message;
        }

        function setLoading(isLoading) {
            analyzeButton.disabled = isLoading;
            analyzeButton.setAttribute(
                "aria-busy",
                String(isLoading)
            );

            analyzeButton.textContent = isLoading
                ? "Analyzing..."
                : "Analyze job description";
        }
    }
})();
