"""
JOBAI Candidate Store
Maintains the verified master profile, genuine CV variants, and validated credentials.
Rule: Zero invention of facts. Only verified information can be cited.
"""

from typing import List, Dict, Optional
from src.models import CandidateProfile, Education, WorkExperience, Project


def get_default_candidate_profile() -> CandidateProfile:
    """
    Returns the candidate's verified master CV profile.
    All facts, metrics, and tools here are validated.
    """
    education = [
        Education(
            degree="B.S. in Data Science & Quantitative Economics (Double Major)",
            institution="University of Washington",
            location="Seattle, WA",
            graduation_year="2024",
            gpa_or_honors="Summa Cum Laude (GPA: 3.92/4.00)",
            relevant_coursework=[
                "Econometrics & Causal Inference",
                "Advanced Statistical Modeling",
                "Machine Learning & Deep Learning",
                "Financial Risk Modeling",
                "Data Structures & Algorithms",
                "Time Series Analysis & Forecasting"
            ]
        )
    ]

    work_experiences = [
        WorkExperience(
            title="Data Analytics & Modeling Intern",
            company="Apex Capital Intelligence",
            location="Seattle, WA",
            start_date="June 2023",
            end_date="August 2023",
            responsibilities=[
                "Built predictive valuation and automated reporting pipelines using Python, SQL, and pandas.",
                "Engineered statistical anomaly detection scripts for transaction data quality validation.",
                "Synthesized weekly data analysis dashboards in Tableau for senior risk officers."
            ],
            technologies=["Python", "SQL", "pandas", "scikit-learn", "Tableau", "Git"],
            achievements=[
                "Reduced reporting generation turnaround by 35% through automated SQL query optimization.",
                "Identified data reconciliation discrepancies totaling $1.2M during portfolio migration audit."
            ]
        ),
        WorkExperience(
            title="Undergraduate Research Assistant (Econometrics Lab)",
            company="Department of Economics, University of Washington",
            location="Seattle, WA",
            start_date="September 2023",
            end_date="May 2024",
            responsibilities=[
                "Assisted Dr. Evelyn Vance with causal inference analysis investigating regional micro-lending policy impacts.",
                "Constructed panel datasets by cleaning, merging, and harmonizing public census and financial records.",
                "Implemented difference-in-differences (DiD) and instrumental variable (IV) models in R and Stata."
            ],
            technologies=["R", "Stata", "Python", "Econometrics", "LaTeX"],
            achievements=[
                "Co-authored data cleaning methodology appendix for a working paper presented at the 2024 Western Economic Association.",
                "Automated data verification routines across 1.4 million municipal micro-credit records."
            ]
        )
    ]

    projects = [
        Project(
            name="Credit Risk Default Probability Forecaster",
            description="Designed an end-to-end credit risk scoring system benchmarking XGBoost, LightGBM, and logistic regression on 250k consumer loan records.",
            technologies=["Python", "scikit-learn", "XGBoost", "pandas", "Streamlit", "Docker"],
            outcomes=[
                "Achieved 0.86 ROC-AUC with rigorous cross-validation and feature attribution using SHAP.",
                "Delivered an interactive Streamlit simulation tool allowing credit analysts to stress-test default thresholds."
            ],
            relevance_tags=["Risk and Financial Analytics", "Data Analytics & Data Science"]
        ),
        Project(
            name="Macroeconomic Shocks & Commodity Price Elasticity",
            description="Conducted an empirical econometrics research project evaluating the transmission of Federal Reserve interest rate shocks to commodity spot prices.",
            technologies=["R", "Python", "Vector Autoregression (VAR)", "Stata", "LaTeX"],
            outcomes=[
                "Estimated impulse response functions demonstrating a 4-month lag in agricultural price adjustments.",
                "Awarded Outstanding Undergraduate Research Paper in Quantitative Economics."
            ],
            relevance_tags=["Economics Research & Predoctoral", "Academic Application"]
        ),
        Project(
            name="Automated Market Intelligence Pipeline",
            description="Built a web extraction and sentiment analysis pipeline tracking commercial retail trends across 50 regional competitor catalogs.",
            technologies=["Python", "PostgreSQL", "FastAPI", "BeautifulSoup", "Docker"],
            outcomes=[
                "Monitored pricing shifts and catalog updates with 99.2% uptime over 6 months.",
                "Exported clean analytical feeds directly to internal business intelligence dashboards."
            ],
            relevance_tags=["Corporate and Business", "Data Analytics & Data Science"]
        )
    ]

    verified_skills = [
        "Python", "SQL", "R", "pandas", "NumPy", "scikit-learn", "XGBoost",
        "Statistical Modeling", "Econometrics", "Causal Inference", "Difference-in-Differences",
        "Financial Risk Analytics", "Credit Risk Modeling", "Tableau", "FastAPI",
        "Git", "Docker", "Stata", "LaTeX", "Data Cleaning & ETL", "A/B Testing"
    ]

    certifications = [
        "Chartered Financial Analyst (CFA) Investment Foundations Certificate",
        "DeepLearning.AI Machine Learning Specialization"
    ]

    screening_answers = {
        "work_authorization": "Authorized to work in the United States without sponsorship.",
        "visa_sponsorship_needed": "No sponsorship required.",
        "years_of_experience": "1 year of combined professional internship and research lab experience.",
        "willing_to_relocate": "Yes, open to relocation or remote arrangements.",
        "preferred_start_date": "Available within two weeks notice.",
        "salary_expectations": "Competitive market rate based on role level and location ($75,000 - $95,000)."
    }

    cv_variants = {
        "Master CV": "Comprehensive overview of technical modeling, data engineering, and econometrics.",
        "Data Science & Analytics CV": "Focus on predictive modeling, SQL pipelines, machine learning, and business impact.",
        "Risk & Financial Analytics CV": "Highlights credit risk modeling, financial data quality, stress testing, and quantitative reasoning.",
        "Economics & Academic Research CV": "Emphasizes causal inference, econometrics, R/Stata empirical research, and academic rigor.",
        "Corporate & Business Intelligence CV": "Focus on dashboarding, workflow automation, stakeholder communication, and analytical ROI."
    }

    return CandidateProfile(
        id="cand-alex-chen-2026",
        full_name="Alex Chen",
        email="alex.chen.datascience@email.com",
        phone="+1 (206) 555-0192",
        location="Seattle, WA",
        linkedin="linkedin.com/in/alex-chen-quant",
        github_or_portfolio="github.com/alexchen-quant",
        target_roles=[
            "Data Scientist",
            "Data Analyst",
            "Financial Risk Analyst",
            "Economics Research Assistant / Predoc",
            "Business Intelligence Analyst"
        ],
        career_interests_and_motivations=(
            "Passionate about leveraging empirical data, statistical rigor, and machine learning "
            "to answer high-stakes questions in business strategy, financial risk management, and public policy. "
            "Eager to translate raw data into validated insights that drive measurable organizational impact."
        ),
        verified_skills=verified_skills,
        education=education,
        work_experiences=work_experiences,
        projects=projects,
        certifications=certifications,
        screening_answers=screening_answers,
        cv_variants=cv_variants
    )


class CandidateStore:
    def __init__(self):
        self._profile: CandidateProfile = get_default_candidate_profile()

    def get_profile(self) -> CandidateProfile:
        return self._profile

    def update_profile(self, updated: CandidateProfile) -> None:
        self._profile = updated

    def get_verified_skills(self) -> List[str]:
        return list(self._profile.verified_skills)

    def select_best_cv_variant(self, job_title: str, industry: str, style_category: str) -> str:
        """
        Determines the most aligned CV variant for the target position.
        """
        lower = f"{job_title} {industry} {style_category}".lower()
        if "predoc" in lower or "research" in lower or "economic" in lower or "academic" in lower:
            return "Economics & Academic Research CV"
        elif "risk" in lower or "credit" in lower or "financial" in lower or "quant" in lower:
            return "Risk & Financial Analytics CV"
        elif "machine learning" in lower or "data sci" in lower or "modeling" in lower or "ai" in lower:
            return "Data Science & Analytics CV"
        elif "business" in lower or "bi " in lower or "strategy" in lower or "operations" in lower:
            return "Corporate & Business Intelligence CV"
        return "Master CV"
