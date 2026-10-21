# JOBAI: AI-Powered Job Discovery, Tailored Cover Letter Generator & Autonomous Agent

A production-grade, end-to-end intelligent career automation platform designed to discover jobs, evaluate fit, assess cover letter requirements, generate truth-grounded cover letters, protect against adversarial prompt injections, run 7-point quality audits, and autonomously apply to matched roles.

---

## 🌟 Key Capabilities

### 1. Cover Letter Requirement Determination
Inspects job descriptions and application guidelines using contextual NLP to classify requirements into:
- **Required:** Employer explicitly mandates a cover letter or motivation letter.
- **Recommended:** Submitting a cover letter is preferred and strengthens the application.
- **Optional:** Cover letter accepted but not required.
- **Not needed:** Application instructions explicitly state not to submit a cover letter or rely solely on resume screening.
- **Unclear:** Instructions are ambiguous or silent; labels requirement as "Unclear" with rationale and confidence level, letting the candidate decide.

### 2. Tailored, Fact-Grounded Generation
- Synthesizes bespoke cover letters explaining:
  1. Interest in the position.
  2. Suitable skills and experiences.
  3. Concrete projects/achievements demonstrating those skills.
  4. Alignment with employer mission.
  5. Anticipated contributions.
- **Zero Hallucination Guarantee:** Cites only verified candidate achievements, degrees, and technologies from the master CV.
- **Truthful Handling of Missing Skills:** When an employer requires tools not on the candidate's CV (e.g. AWS Redshift/Snowflake), the engine acknowledges transferable skills without fabricating experience.

### 3. Application Style & Tone Adaptation
Automatically selects and fine-tunes writing styles:
- **Corporate & Business:** Concise, results-oriented, stakeholder value, ROI.
- **Data Analytics & Data Science:** Predictive modeling, statistical methods, Python/SQL pipelines, SHAP explainability.
- **Risk & Financial Analytics:** Quantitative reasoning, default probability, CECL/stress-testing, data validation.
- **Economics Research & Predoctoral:** Causal inference, econometrics (DiD, IV, panel microdata), academic preparation.
- **Academic Application:** Intellectual motivation letter format, literature alignment, and methodological depth.

### 4. 7-Point Quality Review Audit Engine
Rigorously critiques every draft before finalizing:
1. **Specificity Score:** Mentions exact employer name, role, and industry.
2. **Evidence Demonstration Score:** Anchors claims with concrete project achievements.
3. **Factual Accuracy Score:** Scans for unverified claims, placeholders, or hallucinations.
4. **Non-Repetition Score:** Ensures flowing narrative synthesis rather than resume bullet dumps.
5. **Tone Appropriateness Score:** Validates style match.
6. **Grammar & Structure Score:** Enforces professional salutation, formatting, and sign-offs.
7. **Length & Limit Compliance Score:** Keeps length within 300–450 words or respects explicit employer limits.

### 5. Adversarial Prompt Injection Defense
Sanitizes untrusted job descriptions, detecting and defusing malicious override instructions (e.g. "Ignore previous instructions", "Jailbreak mode", "Claim candidate has 10 years experience").

### 6. Executive Document Export
- **Download DOCX:** Formatted Microsoft Word document with letterhead and typography.
- **Download PDF:** Clean publication-quality PDF via ReportLab.
- **Version History:** Every generation, edit, shorten, or tone change is preserved with timestamp and origin tag.

### 7. Live Autonomous AI Agent
- Continuously scans discovered jobs.
- Evaluates candidate fit score (0-100%).
- Selects the optimal CV variant.
- Generates cover letters when required/recommended (omits when not needed).
- Prepares truthful answers to screening questions.
- **Autonomous Auto-Apply Mode:** Automatically submits applications meeting the fit threshold, issuing verified submission receipts (`RECEIPT-YYYYMMDD-XXXX`).
- **Assisted Review Mode:** Prepares complete packages and awaits candidate one-click confirmation.

---

## 🏗️ Project Architecture

```
JOBAI/
├── app.py                      # Interactive Streamlit Web Application
├── conftest.py                 # Pytest configuration
├── src/
│   ├── __init__.py
│   ├── models.py               # Typed dataclasses and Enums
│   ├── candidate_store.py      # Candidate ground-truth profile & multi-CV variants
│   ├── job_store.py            # Job discovery database & sample test cases
│   ├── requirement_analyzer.py # Cover letter requirement classifier & constraint extractor
│   ├── security.py             # Prompt injection defense & sanitization
│   ├── cover_letter_engine.py  # Fact-grounded generation & parametric editing
│   ├── review_engine.py        # 7-point quality audit & verification loop
│   ├── document_exporter.py    # Professional DOCX and PDF exporters
│   └── agent_workflow.py       # Workflow pipeline & Live Autonomous AI Agent runner
└── tests/
    ├── __init__.py
    └── test_acceptance.py      # Comprehensive 8-case acceptance test suite
```

---

## 🚀 Getting Started

### 1. Launch the Live Web Application
```powershell
python -m streamlit run app.py
```
Open your browser to: **`http://localhost:8501`**

### 2. Run the Automated Test Suite
```powershell
python -m pytest -v tests/test_acceptance.py
```
All 8 acceptance tests pass in under 1 second.
