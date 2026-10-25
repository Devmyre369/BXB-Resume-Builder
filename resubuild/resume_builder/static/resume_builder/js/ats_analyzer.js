

(() => {
    "use strict";

    const panel = document.getElementById("resumeIntelligencePanel");
    if (!panel) return;

    const get = (id) => document.getElementById(id);
    const button = get("riAnalyzeButton");
    const jobDescriptionField = get("riJobDescription");
    const statusNode = get("riStatus");
    const resultsNode = get("riResults");

    if (!button || !jobDescriptionField || !statusNode || !resultsNode) return;

    const CATEGORY_COLORS = {
        "Bad": "#f87171",
        "Moderate": "#fb923c",
        "Needs a Little Improvement": "#facc15",
        "Good": "#60a5fa",
        "Strong": "#34d399",
        "Great": "#2dd4bf",
        "Top Level": "#b6a7ff",
        "Unavailable": "#94a3b8",
    };

    function setStatus(message, isError = false) {
        statusNode.textContent = message;
        statusNode.setAttribute("aria-live", isError ? "assertive" : "polite");
        statusNode.style.color = isError ? "#f87171" : "";
    }

    function setText(id, value, fallback = "") {
        const node = get(id);
        if (node) {
            node.textContent =
                value === undefined || value === null || value === ""
                    ? fallback
                    : String(value);
        }
        return node;
    }

    function setEmptyState(listId, emptyId, hasItems) {
        const list = get(listId);
        const empty = get(emptyId);

        if (list) list.hidden = !hasItems;
        if (empty) empty.hidden = hasItems;
    }

    function clearList(id) {
        const list = get(id);
        if (list) list.replaceChildren();
        return list;
    }

    function renderKeywordList(listId, emptyId, items) {
        const list = clearList(listId);
        const validItems = Array.isArray(items) ? items : [];

        if (list) {
            validItems.forEach((item) => {
                const term = typeof item === "string" ? item : item?.term;
                if (!term) return;

                const li = document.createElement("li");
                li.textContent = term;
                list.appendChild(li);
            });
        }

        const hasItems = Boolean(list && list.children.length);
        setEmptyState(listId, emptyId, hasItems);
    }

    function renderRecommendations(items) {
        const list = clearList("riRecommendations");
        const validItems = Array.isArray(items) ? items : [];

        if (list) {
            validItems.forEach((item) => {
                if (!item || (!item.keyword && !item.message)) return;

                const li = document.createElement("li");
                const heading = document.createElement("strong");
                heading.textContent = item.keyword || "Recommendation";
                li.appendChild(heading);

                if (item.message) {
                    const message = document.createElement("span");
                    message.textContent = ` — ${item.message}`;
                    li.appendChild(message);
                }

                list.appendChild(li);
            });
        }

        const hasItems = Boolean(list && list.children.length);
        setEmptyState("riRecommendations", "riRecommendationsEmpty", hasItems);
    }

    function renderPriorityImprovements(items) {
        const container = clearList("riPriorityImprovements");
        const validItems = Array.isArray(items) ? items : [];

        if (container) {
            validItems.forEach((item, index) => {
                if (!item) return;

                const card = document.createElement("article");
                card.className = "ri-priority-card";

                const eyebrow = document.createElement("div");
                eyebrow.className = "ri-priority-number";

                const priority = Number.isFinite(Number(item.priority))
                    ? Number(item.priority)
                    : index + 1;

                eyebrow.textContent = `Priority ${priority}`;
                card.appendChild(eyebrow);

                const heading = document.createElement("h5");
                heading.textContent = item.title || "Recommended improvement";
                card.appendChild(heading);

                const message = document.createElement("p");
                message.textContent =
                    item.message || "Review this area against the job description.";
                card.appendChild(message);

                if (Array.isArray(item.keywords) && item.keywords.length) {
                    const keywords = document.createElement("div");
                    keywords.className = "ri-priority-keywords";

                    item.keywords.forEach((keyword) => {
                        if (!keyword) return;

                        const tag = document.createElement("span");
                        tag.textContent = keyword;
                        keywords.appendChild(tag);
                    });

                    if (keywords.children.length) {
                        card.appendChild(keywords);
                    }
                }

                container.appendChild(card);
            });
        }

        const hasItems = Boolean(container && container.children.length);
        const empty = get("riPriorityEmpty");

        if (empty) empty.hidden = hasItems;
        if (container) container.hidden = !hasItems;
    }

    function renderScore(data) {
        const rawScore = data.ats_score;
        const hasScore =
            typeof rawScore === "number" && Number.isFinite(rawScore);

        const score = hasScore
            ? Math.max(0, Math.min(100, Math.round(rawScore)))
            : null;

        const category = hasScore
            ? (data.score_category || "Unavailable")
            : "Unavailable";

        const color = CATEGORY_COLORS[category] || CATEGORY_COLORS.Unavailable;
        const gauge = get("riScoreGauge");

        setText("riScoreValue", score === null ? "—" : score);
        setText("riScoreCategory", category, "Unavailable");

        setText(
            "riScoreTitle",
            score === null
                ? "A score could not be calculated"
                : `Your resume scored ${score} out of 100`,
        );

        setText(
            "riScoreDescription",
            data.score_description ||
                data.message ||
                "No additional score explanation was provided.",
        );

        setText(
            "riScoreMethod",
            data.score_method ||
                "This is an estimated keyword-based compatibility indicator, not a score from an employer's ATS.",
        );

        const categoryNode = get("riScoreCategory");

        if (categoryNode) {
            categoryNode.style.color = color;
            categoryNode.style.borderColor = color;
            categoryNode.style.backgroundColor = `${color}14`;
        }

        if (gauge) {
            gauge.style.background = score === null
                ? "conic-gradient(#64748b 0%, rgba(255,255,255,.10) 0)"
                : `conic-gradient(${color} ${score}%, rgba(255,255,255,.10) ${score}% 100%)`;

            gauge.setAttribute(
                "aria-label",
                score === null
                    ? "Estimated ATS compatibility score unavailable"
                    : `Estimated ATS compatibility score: ${score} out of 100, category ${category}`,
            );
        }
    }

    function renderAnalysis(data) {
        resultsNode.hidden = false;
        renderScore(data);

        setText("riCoverage", `${Number(data.keyword_coverage_percent ?? 0)}%`);
        setText("riPresence", `${Number(data.resume_keyword_presence_percent ?? 0)}%`);
        setText("riTotal", data.total_keywords ?? 0);

        const counts = data.counts || {};
        const matched = Array.isArray(data.matched) ? data.matched : [];
        const needsEvidence = Array.isArray(data.needs_evidence)
            ? data.needs_evidence
            : [];
        const missing = Array.isArray(data.missing) ? data.missing : [];

        setText("riMatchedCount", `(${counts.matched ?? matched.length})`);
        setText(
            "riEvidenceCount",
            `(${counts.needs_evidence ?? needsEvidence.length})`,
        );
        setText("riMissingCount", `(${counts.missing ?? missing.length})`);

        renderKeywordList("riMatched", "riMatchedEmpty", matched);
        renderKeywordList("riEvidence", "riEvidenceEmpty", needsEvidence);
        renderKeywordList("riMissing", "riMissingEmpty", missing);

        renderPriorityImprovements(data.priority_improvements);
        renderRecommendations(data.recommendations);

        setText("riExplanation", data.explanation || "");
    }

    function getCsrfToken() {
        const input = document.querySelector(
            '#riCsrfForm input[name="csrfmiddlewaretoken"]',
        );

        return input ? input.value : "";
    }

    async function analyzeResume() {
        const jobDescription = jobDescriptionField.value.trim();

        if (!jobDescription) {
            setStatus("Paste a job description before running the analysis.", true);
            jobDescriptionField.focus();
            return;
        }

        if (
            !window.BxBResumeBuilder ||
            typeof window.BxBResumeBuilder.getResumeDataForAnalysis !== "function"
        ) {
            setStatus(
                "Resume data is not available. Refresh the editor and try again.",
                true,
            );
            return;
        }

        const analysisUrl = panel.dataset.analysisUrl;

        if (!analysisUrl) {
            setStatus(
                "The analysis endpoint is not configured. Check the Django URL in editor.html.",
                true,
            );
            return;
        }

        const resumeData =
            window.BxBResumeBuilder.getResumeDataForAnalysis();
        const csrfToken = getCsrfToken();

        button.disabled = true;
        button.setAttribute("aria-busy", "true");
        setStatus("Analyzing your resume against this job description…");

        try {
            const headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            };

            if (csrfToken) {
                headers["X-CSRFToken"] = csrfToken;
            }

            const response = await fetch(analysisUrl, {
                method: "POST",
                credentials: "same-origin",
                headers,
                body: JSON.stringify({
                    job_description: jobDescription,
                    resume: resumeData,
                }),
            });

            let data;

            try {
                data = await response.json();
            } catch (_error) {
                throw new Error(
                    "The server returned an unreadable response. Check the Django terminal for errors.",
                );
            }

            if (!response.ok || data.status === "error") {
                throw new Error(
                    data.message || `Analysis request failed (${response.status}).`,
                );
            }

            if (data.status === "no_keywords") {
                data.ats_score = null;
                data.score_category = "Unavailable";
                data.score_description =
                    data.message ||
                    "No supported job-description keywords were detected.";

                data.score_method =
                    "No score was calculated because the analyzer could not identify supported keywords in this job description.";

                data.counts = {
                    matched: 0,
                    needs_evidence: 0,
                    missing: 0,
                };

                data.priority_improvements = [];
                data.recommendations = [];
            }

            renderAnalysis(data);

            setStatus(
                data.status === "no_keywords"
                    ? "Analysis completed, but no supported keywords were recognized."
                    : "Analysis complete. Use the priorities to improve your resume for this role.",
            );
        } catch (error) {
            setStatus(
                error instanceof Error
                    ? error.message
                    : "Unable to analyze the resume. Please try again.",
                true,
            );
        } finally {
            button.disabled = false;
            button.removeAttribute("aria-busy");
        }
    }

    button.addEventListener("click", analyzeResume);
})();
