"""
JOBAI Core Data Models
Defines typed structures for Candidates, Jobs, Cover Letters, Applications, and Audit Reports.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid


class CoverLetterRequirement(str, Enum):
    REQUIRED = "Required"
    RECOMMENDED = "Recommended"
    OPTIONAL = "Optional"
    NOT_NEEDED = "Not needed"
    UNCLEAR = "Unclear"


class ApplicationStyle(str, Enum):
    CORPORATE = "Corporate and Business"
    DATA_ANALYTICS = "Data Analytics & Data Science"
    RISK_FINANCIAL = "Risk and Financial Analytics"
    ECONOMICS_RESEARCH = "Economics Research & Predoctoral"
    ACADEMIC = "Academic Application"


class ApplicationStatus(str, Enum):
    DISCOVERED = "Discovered"
    MATCHED = "Matched"
    PREPARING = "Preparing"
    READY_FOR_REVIEW = "Ready for Review"
    SUBMITTED = "Submitted"
    SKIPPED = "Skipped"
    REJECTED = "Rejected"


@dataclass
class Project:
    name: str
    description: str
    technologies: List[str]
    outcomes: List[str]
    relevance_tags: List[str] = field(default_factory=list)


@dataclass
class WorkExperience:
    title: str
    company: str
    location: str
    start_date: str
    end_date: str
    responsibilities: List[str]
    technologies: List[str]
    achievements: List[str]


@dataclass
class Education:
    degree: str
    institution: str
    location: str
    graduation_year: str
    gpa_or_honors: str
    relevant_coursework: List[str] = field(default_factory=list)


@dataclass
class CandidateProfile:
    id: str
    full_name: str
    email: str
    phone: str
    location: str
    linkedin: str
    github_or_portfolio: str
    target_roles: List[str]
    career_interests_and_motivations: str
    verified_skills: List[str]
    education: List[Education]
    work_experiences: List[WorkExperience]
    projects: List[Project]
    certifications: List[str]
    screening_answers: Dict[str, str] = field(default_factory=dict)
    cv_variants: Dict[str, str] = field(default_factory=dict)  # variant_name -> summary/focus


@dataclass
class RequirementAssessment:
    status: CoverLetterRequirement
    confidence: str  # "High", "Medium", "Low"
    confidence_score: float  # 0.0 - 1.0
    explanation: str
    extracted_clues: List[str] = field(default_factory=list)
    word_limit: Optional[int] = None
    specific_prompts: List[str] = field(default_factory=list)


@dataclass
class JobPosting:
    id: str
    title: str
    employer: str
    industry: str
    location: str
    job_type: str  # Full-time, Internship, etc.
    workplace_type: str  # Remote, Hybrid, Onsite
    description: str
    application_instructions: str
    stated_requirements: List[str]
    preferred_qualifications: List[str]
    screening_questions: List[str] = field(default_factory=list)
    word_limit: Optional[int] = None
    posted_date: str = ""
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    assessment: Optional[RequirementAssessment] = None
    style_category: ApplicationStyle = ApplicationStyle.CORPORATE


@dataclass
class AuditReport:
    specificity_score: int  # 0-100
    evidence_score: int     # 0-100
    factual_accuracy_score: int  # 0-100
    non_repetition_score: int    # 0-100
    tone_score: int         # 0-100
    grammar_score: int      # 0-100
    length_compliance_score: int # 0-100
    overall_score: int      # 0-100
    passed: bool
    word_count: int
    detected_claims_verified: List[str]
    warnings_or_unsupported: List[str]
    suggestions: List[str]


@dataclass
class CoverLetterVersion:
    version_id: str
    job_id: str
    timestamp: str
    content: str
    action_origin: str  # e.g., "Initial Generation", "User Edited", "Shortened", "Tone Adjusted", "Specific Focus"
    tone_used: str
    audit_report: Optional[AuditReport] = None


@dataclass
class ApplicationRecord:
    application_id: str
    job_id: str
    job_title: str
    employer: str
    cv_variant_used: str
    cover_letter_version_id: Optional[str]
    cover_letter_text: Optional[str]
    screening_qna: Dict[str, str]
    fit_score: int
    match_breakdown: Dict[str, Any]
    status: ApplicationStatus
    submitted_at: Optional[str]
    submission_mode: str  # "Autonomous Live Agent" or "Manual Approval"
    submission_receipt: Optional[str]
    audit_log: List[str] = field(default_factory=list)
