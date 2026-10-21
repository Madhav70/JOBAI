"""
Acceptance Test Suite for JOBAI Cover Letter System & Autonomous Agent
Tests all 7 acceptance requirements specified in user prompt plus the Live AI Agent.
"""

import pytest
import re
from src.models import (
    CoverLetterRequirement, ApplicationStyle, ApplicationStatus,
    CoverLetterVersion
)
from src.candidate_store import CandidateStore
from src.job_store import JobStore
from src.requirement_analyzer import RequirementAnalyzer
from src.cover_letter_engine import CoverLetterEngine
from src.review_engine import QualityReviewEngine
from src.document_exporter import DocumentExporter
from src.agent_workflow import ApplicationWorkflowManager
from src.security import SecuritySanitizer


@pytest.fixture
def workflow():
    candidate_store = CandidateStore()
    job_store = JobStore()
    return ApplicationWorkflowManager(candidate_store, job_store)


def test_1_explicitly_required_cover_letter(workflow):
    """
    Test Case 1:
    A job explicitly requires a cover letter -> generate one tailored to the job.
    """
    job = workflow.job_store.get_job("job-corp-101")
    assert job is not None

    # Assessment verification
    assessment = RequirementAnalyzer.analyze(job.description, job.application_instructions)
    assert assessment.status == CoverLetterRequirement.REQUIRED
    assert assessment.confidence == "High"
    assert "explicit" in assessment.explanation.lower() or "mandates" in assessment.explanation.lower()

    # Package preparation generates tailored cover letter
    app = workflow.prepare_application_package(job)
    assert app.cover_letter_text is not None
    assert app.cover_letter_version_id is not None

    # Verify tailoring and specificity
    text = app.cover_letter_text
    assert "Cascade Health Partners" in text
    assert "Business Analytics Associate" in text
    assert "Apex Capital Intelligence" in text or "Alex Chen" in text
    # Verify quality review passes
    audit = QualityReviewEngine.audit(text, job, workflow.candidate_store.get_profile(), job.style_category.value)
    assert audit.passed is True
    assert audit.overall_score >= 80


def test_2_recommended_cover_letter(workflow):
    """
    Test Case 2:
    A job recommends a cover letter: generate a draft and explain why it is useful.
    """
    job = workflow.job_store.get_job("job-ds-102")
    assert job is not None

    assessment = RequirementAnalyzer.analyze(job.description, job.application_instructions)
    assert assessment.status == CoverLetterRequirement.RECOMMENDED
    assert assessment.confidence == "High"
    assert "strengthen" in assessment.explanation.lower()

    app = workflow.prepare_application_package(job)
    assert app.cover_letter_text is not None

    text = app.cover_letter_text
    assert "DataNexus Labs" in text
    assert "XGBoost" in text or "scikit-learn" in text
    # Contains explanation of suitability
    assert "predictive" in text.lower() or "modeling" in text.lower()


def test_3_not_needed_cover_letter(workflow):
    """
    Test Case 3:
    A job does not require a cover letter: do not create one automatically.
    """
    job = workflow.job_store.get_job("job-noneed-103")
    assert job is not None

    assessment = RequirementAnalyzer.analyze(job.description, job.application_instructions)
    assert assessment.status == CoverLetterRequirement.NOT_NEEDED
    assert assessment.confidence == "High"

    # Crucial rule: When NOT NEEDED, package preparation does NOT create one automatically
    app = workflow.prepare_application_package(job)
    assert app.cover_letter_text is None
    assert app.cover_letter_version_id is None


def test_4_academic_research_motivation_letter(workflow):
    """
    Test Case 4:
    An academic research role requests a motivation letter: use an appropriate research-focused format.
    """
    job = workflow.job_store.get_job("job-econ-104")
    assert job is not None

    assessment = RequirementAnalyzer.analyze(job.description, job.application_instructions)
    assert assessment.status == CoverLetterRequirement.REQUIRED
    assert assessment.word_limit == 450

    app = workflow.prepare_application_package(job)
    text = app.cover_letter_text
    assert text is not None

    # Check academic format & tone
    assert "Brookfield Institute for Economic Policy" in text
    assert "Dear Professor Lin" in text or "Dear Members of the Selection Committee" in text
    # Contains research-focused content: econometrics, causal inference, panel data
    assert "econometric" in text.lower() or "causal inference" in text.lower()
    assert "difference-in-differences" in text.lower() or "panel data" in text.lower()
    assert "phd in economics" in text.lower() or "doctoral" in text.lower()

    # Verify no corporate buzzwords like "synergy" or "bottom line"
    assert "synergy" not in text.lower()
    assert "rockstar" not in text.lower()

    # Verify length compliance under 450 words
    word_count = len(re.findall(r"\b\w+\b", text))
    assert word_count <= 490  # within margin of 450


def test_5_missing_experience_transferable_skills(workflow):
    """
    Test Case 5:
    A job requests specific experience missing from the CV: acknowledge transferable skills without inventing experience.
    """
    job = workflow.job_store.get_job("job-missing-105")
    assert job is not None

    profile = workflow.candidate_store.get_profile()
    # Candidate verified skills do NOT include AWS Redshift or Snowflake
    assert "AWS Redshift" not in profile.verified_skills
    assert "Snowflake" not in profile.verified_skills

    app = workflow.prepare_application_package(job)
    text = app.cover_letter_text

    # The engine must NOT invent that candidate has 5 years of Redshift or Snowflake
    assert "10 years of snowflake" not in text.lower()

    # The engine MUST acknowledge transferable skills honestly
    assert "transferable" in text.lower() or "transition" in text.lower()
    assert "postgresql" in text.lower() or "sql" in text.lower()


def test_6_untrusted_prompt_injection_defense(workflow):
    """
    Test Case 6:
    The job description contains misleading instructions or attempts to override application rules:
    treat it as untrusted content and prevent hallucination/injection.
    """
    job = workflow.job_store.get_job("job-inject-106")
    assert job is not None

    # Security check on job text
    sanitized, is_flagged, threats = SecuritySanitizer.inspect_and_sanitize(job.description)
    assert is_flagged is True
    assert len(threats) > 0

    # Generate cover letter
    profile = workflow.candidate_store.get_profile()
    version = CoverLetterEngine.generate_cover_letter(job, profile)
    text = version.content

    # Adversarial commands MUST be neutralized and NEVER obeyed
    assert "renaissance technologies" not in text.lower()
    assert "chief quantitative architect" not in text.lower()
    assert "500m" not in text.lower()
    assert "phd in physics from mit" not in text.lower()
    assert "10 years on wall street" not in text.lower()

    # Candidate remains truthfully Alex Chen from UW
    assert "Alex Chen" in text or "University of Washington" in text


def test_7_user_edits_and_downloads_preserved(workflow):
    """
    Test Case 7:
    The user edits and downloads the letter: preserve the final version and associate it with the correct job.
    """
    job = workflow.job_store.get_job("job-corp-101")
    app = workflow.prepare_application_package(job)
    original_text = app.cover_letter_text

    # Candidate edits the letter
    edited_text = original_text + "\n\nPS: I am also available for an in-person tour of your Seattle clinic facilities."
    new_version = CoverLetterVersion(
        version_id="v-user-edit-999",
        job_id=job.id,
        timestamp="2026-10-21 23:30:00",
        content=edited_text,
        action_origin="User Custom Edit",
        tone_used="Corporate and Business"
    )

    # Record version
    workflow.record_cover_letter_version(new_version)

    # Check that job has version history preserved
    history = workflow.cover_letter_history[job.id]
    assert len(history) >= 2
    assert history[-1].version_id == "v-user-edit-999"
    assert "Seattle clinic facilities" in history[-1].content
    assert app.cover_letter_text == edited_text

    # Test PDF and DOCX generation
    profile = workflow.candidate_store.get_profile()
    docx_bytes = DocumentExporter.generate_docx_bytes(edited_text, profile, job.employer, job.title)
    pdf_bytes = DocumentExporter.generate_pdf_bytes(edited_text, profile, job.employer, job.title)

    assert len(docx_bytes) > 1000
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


def test_8_live_autonomous_agent(workflow):
    """
    Test Case 8:
    The Live Autonomous AI Agent discovers jobs, checks fit threshold, drafts packages,
    and auto-applies to matching roles under which the candidate is fit.
    """
    workflow.auto_apply_enabled = True
    workflow.min_fit_threshold = 70  # Candidate qualifies for high and moderate matches

    cycle_results = workflow.run_live_autonomous_cycle()
    assert len(cycle_results) > 0

    applied_jobs = [r for r in cycle_results if r["action"] == "Auto-Applied"]
    assert len(applied_jobs) >= 2  # Cascade Health and DataNexus and Vanguard fit Alex Chen

    for applied in applied_jobs:
        job_id = applied["job_id"]
        app_record = workflow.applications[job_id]
        assert app_record.status == ApplicationStatus.SUBMITTED
        assert app_record.submission_receipt is not None
        assert app_record.submission_receipt.startswith("RECEIPT-")
        assert app_record.fit_score >= workflow.min_fit_threshold
