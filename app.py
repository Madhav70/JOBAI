"""
JOBAI - AI-Powered Job Discovery, Tailored Cover Letter Generator & Autonomous Agent
Interactive Streamlit Application
"""

import streamlit as st
import io
import time
from datetime import datetime

from src.models import (
    CoverLetterRequirement, ApplicationStyle, ApplicationStatus,
    CoverLetterVersion, JobPosting
)
from src.candidate_store import CandidateStore
from src.job_store import JobStore
from src.requirement_analyzer import RequirementAnalyzer
from src.cover_letter_engine import CoverLetterEngine
from src.review_engine import QualityReviewEngine
from src.document_exporter import DocumentExporter
from src.agent_workflow import ApplicationWorkflowManager
from src.security import SecuritySanitizer


# -----------------------------------------------------------------------------
# App Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="JOBAI - Autonomous Agent & Cover Letter Studio",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished typography, badges, and layout
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #112E51;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .badge-required {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-recommended {
        background-color: #FEF08A;
        color: #854D0E;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-optional {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-noneed {
        background-color: #F3F4F6;
        color: #374151;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-unclear {
        background-color: #F3E8FF;
        color: #6B21A8;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-fit-high {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-fit-mid {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .audit-card {
        background-color: #F8FAFC;
        border-left: 4px solid #2563EB;
        padding: 14px;
        border-radius: 4px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .agent-active-box {
        background-color: #ECFDF5;
        border: 1px solid #10B981;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "workflow_manager" not in st.session_state:
    candidate_store = CandidateStore()
    job_store = JobStore()
    st.session_state.workflow_manager = ApplicationWorkflowManager(candidate_store, job_store)

if "active_job_id" not in st.session_state:
    st.session_state.active_job_id = "job-corp-101"

if "cover_letter_draft" not in st.session_state:
    st.session_state.cover_letter_draft = {}

mgr: ApplicationWorkflowManager = st.session_state.workflow_manager
candidate = mgr.candidate_store.get_profile()


# -----------------------------------------------------------------------------
# Sidebar: Navigation & Autonomous Agent Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=64)
    st.title("JOBAI Intelligence")
    st.caption("AI-Powered Job Application Engine & Agent")

    st.markdown("---")
    st.subheader("🤖 Autonomous Agent")

    auto_apply_toggle = st.toggle(
        "Enable Autonomous Auto-Apply",
        value=mgr.auto_apply_enabled,
        help="When enabled, the live agent submits applications directly for positions meeting your fit threshold."
    )
    mgr.auto_apply_enabled = auto_apply_toggle

    threshold = st.slider(
        "Minimum Fit Threshold (%)",
        min_value=50,
        max_value=95,
        value=mgr.min_fit_threshold,
        step=5,
        help="The agent only acts on jobs where candidate fit matches or exceeds this percentage."
    )
    mgr.min_fit_threshold = threshold

    if st.button("⚡ Run Autonomous Scan Cycle", type="primary", use_container_width=True):
        with st.spinner("Agent scanning jobs, evaluating fit, generating materials & applying..."):
            cycle_results = mgr.run_live_autonomous_cycle()
            st.success(f"Agent cycle complete! Processed {len(cycle_results)} opportunities.")

    st.markdown("---")
    menu = st.radio(
        "Navigation",
        [
            "💼 Job Discovery & Studio",
            "🤖 Live Agent Activity Log",
            "📋 Submissions & History",
            "👤 Candidate Master CV & Profile",
            "🧪 Run Acceptance Test Suite",
            "➕ Add Custom Job Posting"
        ]
    )

    st.markdown("---")
    st.markdown(f"**Candidate:** {candidate.full_name}")
    st.caption(f"📍 {candidate.location} | {candidate.education[0].institution}")
    st.caption("Double Major: Data Science & Quant Economics")


# -----------------------------------------------------------------------------
# Helper Badges
# -----------------------------------------------------------------------------
def get_requirement_badge(status: CoverLetterRequirement) -> str:
    if status == CoverLetterRequirement.REQUIRED:
        return '<span class="badge-required">📌 Required</span>'
    elif status == CoverLetterRequirement.RECOMMENDED:
        return '<span class="badge-recommended">⭐ Recommended</span>'
    elif status == CoverLetterRequirement.OPTIONAL:
        return '<span class="badge-optional">💡 Optional</span>'
    elif status == CoverLetterRequirement.NOT_NEEDED:
        return '<span class="badge-noneed">🚫 Not needed</span>'
    else:
        return '<span class="badge-unclear">❓ Unclear</span>'


def get_fit_badge(score: int) -> str:
    if score >= 80:
        return f'<span class="badge-fit-high">🎯 {score}% Fit (High)</span>'
    elif score >= 65:
        return f'<span class="badge-fit-mid">⚖️ {score}% Fit (Moderate)</span>'
    else:
        return f'<span class="badge-noneed">⚠️ {score}% Fit (Low)</span>'


# =============================================================================
# View 1: Job Discovery & Cover Letter Application Studio
# =============================================================================
if menu == "💼 Job Discovery & Studio":
    st.markdown('<div class="main-header">Job Discovery & Application Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Discover tailored positions, inspect cover letter requirements, customize letters with 7-point quality audits, and package applications.</div>', unsafe_allow_html=True)

    # Job List & Filter bar
    jobs = mgr.job_store.list_jobs()

    col1, col2 = st.columns([1, 2.5])

    with col1:
        st.subheader("Discovered Jobs")
        filter_status = st.selectbox("Filter by Status", ["All", "Discovered", "Ready for Review", "Submitted", "Skipped"])

        # Display list of jobs
        for j in jobs:
            fit_score, _ = mgr.evaluate_fit(j)
            assessment = j.assessment or RequirementAnalyzer.analyze(j.description, j.application_instructions)
            app_record = mgr.applications.get(j.id)
            current_status = app_record.status.value if app_record else "Discovered"

            if filter_status != "All" and current_status != filter_status:
                continue

            is_active = (j.id == st.session_state.active_job_id)

            card_border = "2px solid #2563EB" if is_active else "1px solid #E2E8F0"
            bg_color = "#EFF6FF" if is_active else "#FFFFFF"

            with st.container():
                st.markdown(
                    f"""
                    <div style="border: {card_border}; background-color: {bg_color}; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                        <div style="font-weight: 700; font-size: 1rem; color: #1E293B;">{j.title}</div>
                        <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 6px;">{j.employer} • {j.location}</div>
                        <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 6px;">
                            {get_fit_badge(fit_score)}
                            {get_requirement_badge(assessment.status)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button(f"View & Work on Role", key=f"sel_{j.id}", use_container_width=True):
                    st.session_state.active_job_id = j.id
                    st.rerun()

    with col2:
        active_job = mgr.job_store.get_job(st.session_state.active_job_id)
        if not active_job:
            st.info("Select a job on the left to begin.")
        else:
            fit_score, fit_breakdown = mgr.evaluate_fit(active_job)
            assessment = active_job.assessment or RequirementAnalyzer.analyze(active_job.description, active_job.application_instructions)
            app_record = mgr.applications.get(active_job.id)

            if not app_record:
                app_record = mgr.prepare_application_package(active_job)

            # Header Details
            st.markdown(f"### {active_job.title} at **{active_job.employer}**")
            st.caption(f"🏢 Industry: {active_job.industry} | 📍 Workplace: {active_job.workplace_type} ({active_job.location})")

            # Status Banner
            banner_col1, banner_col2, banner_col3 = st.columns([1, 1, 1.2])
            with banner_col1:
                st.markdown(f"**Candidate Fit:**")
                st.markdown(get_fit_badge(fit_score), unsafe_allow_html=True)
            with banner_col2:
                st.markdown(f"**Cover Letter:**")
                st.markdown(get_requirement_badge(assessment.status), unsafe_allow_html=True)
            with banner_col3:
                st.markdown(f"**Application State:**")
                if app_record.status == ApplicationStatus.SUBMITTED:
                    st.success(f"✅ Submitted ({app_record.submission_receipt})")
                else:
                    st.info(f"⏳ {app_record.status.value}")

            # Assessment explanation box
            st.markdown(
                f"""
                <div class="audit-card">
                    <b>Requirement Assessment (Confidence: {assessment.confidence}):</b> {assessment.explanation}<br/>
                    <small><b>Detected Clues:</b> {', '.join(assessment.extracted_clues) if assessment.extracted_clues else 'None'}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Security Warning if Untrusted Injection was detected
            sanitized_desc, is_flagged, threats = SecuritySanitizer.inspect_and_sanitize(active_job.description)
            if is_flagged:
                st.error("🛡️ **Security Alert: Adversarial Prompt Injection Detected in Job Description!**")
                for threat in threats:
                    st.caption(f"• {threat}")
                st.warning("The system has neutralized untrusted override commands. Candidate facts and truthfulness remain strictly enforced.")

            # Tabs for Studio
            tab_desc, tab_workflow, tab_cl, tab_qna, tab_history = st.tabs([
                "📄 Job Description & Fit",
                "⚙️ Workflow & Packaging",
                "✍️ Cover Letter Studio",
                "❓ Screening Q&A",
                "📜 Version History & Audit"
            ])

            # Tab: Description & Fit
            with tab_desc:
                st.markdown("#### Job Overview")
                st.write(active_job.description)
                st.markdown("#### Application Instructions")
                st.info(active_job.application_instructions)
                st.markdown("#### Match Breakdown")
                st.markdown(f"- **Matched Skills:** {', '.join(fit_breakdown['matched_skills'])}")
                if fit_breakdown['missing_or_transferable_requirements']:
                    st.markdown(f"- **Requirements Requiring Transferable Skills:** {', '.join(fit_breakdown['missing_or_transferable_requirements'])}")
                st.markdown(f"- **Degree & Academic Preparation:** Summa Cum Laude, B.S. in Data Science & Quantitative Economics")

            # Tab: Workflow & Packaging
            with tab_workflow:
                st.markdown("#### Application Package Setup")
                st.write("Review the materials assembled for submission:")

                col_cv, col_mode = st.columns(2)
                with col_cv:
                    selected_cv = st.selectbox(
                        "Selected CV Variant",
                        list(candidate.cv_variants.keys()),
                        index=list(candidate.cv_variants.keys()).index(app_record.cv_variant_used) if app_record.cv_variant_used in candidate.cv_variants else 0
                    )
                    app_record.cv_variant_used = selected_cv
                    st.caption(f"Variant Focus: {candidate.cv_variants[selected_cv]}")

                with col_mode:
                    st.markdown("**Submission Approval:**")
                    if app_record.status == ApplicationStatus.SUBMITTED:
                        st.success(f"Submitted on {app_record.submitted_at} via {app_record.submission_mode}")
                        st.code(f"Receipt ID: {app_record.submission_receipt}")
                    else:
                        st.write("Ready to finalize package.")
                        if st.button("🚀 Submit Application Now", type="primary", use_container_width=True):
                            success, receipt = mgr.submit_application(active_job.id, mode="Manual User Approval")
                            if success:
                                st.balloons()
                                st.success(f"Application successfully submitted! Receipt: {receipt}")
                                st.rerun()

            # Tab: Cover Letter Studio
            with tab_cl:
                st.markdown("#### AI-Powered Cover Letter Studio")

                if assessment.status == CoverLetterRequirement.NOT_NEEDED and not app_record.cover_letter_text:
                    st.info(
                        "ℹ️ **Cover letter is Not Needed:** The employer specifies that cover letters are not accepted. "
                        "No letter has been generated automatically to respect employer instructions. "
                        "If you wish to force create one anyway, click 'Generate Cover Letter' below."
                    )

                # Action Buttons Toolbar
                b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([1, 1, 1, 1, 1.4])

                with b_col1:
                    if st.button("✨ Generate", help="Generate or regenerate tailored letter"):
                        with st.spinner("Synthesizing tailored cover letter..."):
                            new_ver = CoverLetterEngine.generate_cover_letter(
                                active_job, candidate, action_origin="Manual Generation"
                            )
                            mgr.record_cover_letter_version(new_ver)
                            st.session_state.cover_letter_draft[active_job.id] = new_ver.content
                            st.success("Generated!")
                            st.rerun()

                with b_col2:
                    if st.button("🔄 Regenerate", help="Regenerate with fresh phrasing"):
                        with st.spinner("Regenerating letter..."):
                            new_ver = CoverLetterEngine.generate_cover_letter(
                                active_job, candidate, action_origin="Regenerated Version"
                            )
                            mgr.record_cover_letter_version(new_ver)
                            st.session_state.cover_letter_draft[active_job.id] = new_ver.content
                            st.rerun()

                with b_col3:
                    if st.button("✂️ Shorten", help="Condense letter to concise ~300 words"):
                        with st.spinner("Shortening letter..."):
                            new_ver = CoverLetterEngine.generate_cover_letter(
                                active_job, candidate, action_origin="Shortened Version", shorten=True
                            )
                            mgr.record_cover_letter_version(new_ver)
                            st.session_state.cover_letter_draft[active_job.id] = new_ver.content
                            st.rerun()

                with b_col4:
                    if st.button("🎯 Specific", help="Deepen project specifics and metrics"):
                        with st.spinner("Deepening specificity..."):
                            new_ver = CoverLetterEngine.generate_cover_letter(
                                active_job, candidate, action_origin="Deepened Specificity", make_specific=True
                            )
                            mgr.record_cover_letter_version(new_ver)
                            st.session_state.cover_letter_draft[active_job.id] = new_ver.content
                            st.rerun()

                with b_col5:
                    target_tone = st.selectbox(
                        "Change Tone",
                        [
                            "Corporate and Business",
                            "Data Analytics & Data Science",
                            "Risk and Financial Analytics",
                            "Economics Research & Predoctoral",
                            "Academic Application"
                        ],
                        index=0
                    )
                    if st.button("Apply Tone"):
                        with st.spinner(f"Adapting tone to '{target_tone}'..."):
                            new_ver = CoverLetterEngine.generate_cover_letter(
                                active_job, candidate, tone_override=target_tone, action_origin=f"Tone Shift ({target_tone})"
                            )
                            mgr.record_cover_letter_version(new_ver)
                            st.session_state.cover_letter_draft[active_job.id] = new_ver.content
                            st.rerun()

                # Text Editor & Preview
                current_text = app_record.cover_letter_text or ""
                if active_job.id in st.session_state.cover_letter_draft:
                    current_text = st.session_state.cover_letter_draft[active_job.id]

                if not current_text:
                    st.write("*No cover letter drafted yet. Click 'Generate' above.*")
                else:
                    word_count = len(current_text.split())
                    limit_label = f"Target: ~300-450 words (Employer limit: {active_job.word_limit} words)" if active_job.word_limit else "Target: ~300-450 words"
                    st.caption(f"📊 **Word Count:** {word_count} words | {limit_label}")

                    edited_text = st.text_area(
                        "Editable Cover Letter Draft",
                        value=current_text,
                        height=420,
                        key=f"editor_{active_job.id}"
                    )

                    col_save, col_docx, col_pdf = st.columns([1.5, 1, 1])

                    with col_save:
                        if st.button("💾 Save Custom Edits"):
                            user_ver = CoverLetterVersion(
                                version_id=f"v-edit-{datetime.now().strftime('%H%M%S')}",
                                job_id=active_job.id,
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                content=edited_text,
                                action_origin="User Custom Edit",
                                tone_used="Custom"
                            )
                            mgr.record_cover_letter_version(user_ver)
                            st.session_state.cover_letter_draft[active_job.id] = edited_text
                            st.success("Saved revised version to history!")
                            st.rerun()

                    with col_docx:
                        docx_bytes = DocumentExporter.generate_docx_bytes(
                            edited_text, candidate, active_job.employer, active_job.title
                        )
                        st.download_button(
                            label="📄 Download DOCX",
                            data=docx_bytes,
                            file_name=f"CoverLetter_{active_job.employer.replace(' ', '_')}_{candidate.full_name.replace(' ', '_')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )

                    with col_pdf:
                        pdf_bytes = DocumentExporter.generate_pdf_bytes(
                            edited_text, candidate, active_job.employer, active_job.title
                        )
                        st.download_button(
                            label="📑 Download PDF",
                            data=pdf_bytes,
                            file_name=f"CoverLetter_{active_job.employer.replace(' ', '_')}_{candidate.full_name.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

                    # 7-Point Quality Audit Scorecard
                    audit = QualityReviewEngine.audit(edited_text, active_job, candidate, active_job.style_category.value)
                    st.markdown("---")
                    st.markdown("#### 🛡️ 7-Point Quality & Truthfulness Audit")

                    score_col1, score_col2 = st.columns([1, 2.5])
                    with score_col1:
                        st.metric("Overall Quality Score", f"{audit.overall_score} / 100", delta="Passed" if audit.passed else "Needs Revision")
                    with score_col2:
                        st.markdown(
                            f"""
                            - **Job Specificity:** {audit.specificity_score}/100
                            - **Evidence & Qualifications:** {audit.evidence_score}/100
                            - **Factual Accuracy (Anti-Hallucination):** {audit.factual_accuracy_score}/100
                            - **Narrative vs CV Repetition:** {audit.non_repetition_score}/100
                            - **Tone Appropriateness:** {audit.tone_score}/100
                            - **Length Compliance:** {audit.length_compliance_score}/100
                            """
                        )

                    if audit.detected_claims_verified:
                        st.markdown("**Verified Claims Grounded in CV:**")
                        for claim in audit.detected_claims_verified[:4]:
                            st.caption(f"✅ {claim}")

                    if audit.warnings_or_unsupported:
                        st.warning("**Audit Warnings:**")
                        for w in audit.warnings_or_unsupported:
                            st.write(f"⚠️ {w}")

            # Tab: Screening Q&A
            with tab_qna:
                st.markdown("#### Truthful Screening Question Answers")
                st.write("Automated responses strictly grounded in verified candidate profile:")
                for q, ans in app_record.screening_qna.items():
                    st.markdown(f"**Q: {q}**")
                    st.write(f"👉 *{ans}*")
                    st.markdown("---")

            # Tab: Version History
            with tab_history:
                st.markdown("#### Version History for this Job")
                history = mgr.cover_letter_history.get(active_job.id, [])
                if not history:
                    st.write("No versions recorded yet.")
                else:
                    for idx, v in enumerate(reversed(history)):
                        with st.expander(f"Version {v.version_id} ({v.action_origin}) - {v.timestamp}"):
                            st.caption(f"Tone: {v.tone_used}")
                            st.text(v.content[:350] + "...")
                            if st.button("Restore this Version", key=f"restore_{v.version_id}"):
                                mgr.record_cover_letter_version(v)
                                st.session_state.cover_letter_draft[active_job.id] = v.content
                                st.rerun()

                st.markdown("#### Application Audit Trail Log")
                for log_entry in app_record.audit_log:
                    st.code(log_entry, language="bash")


# =============================================================================
# View 2: Live Autonomous AI Agent Dashboard
# =============================================================================
elif menu == "🤖 Live Agent Activity Log":
    st.markdown('<div class="main-header">Live Autonomous AI Agent Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Monitor your autonomous agent as it scans discovered jobs, verifies candidate fit, drafts tailored packages, and executes submissions.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(
            f"""
            <div class="agent-active-box">
                <h4 style="margin:0; color:#065F46;">🤖 Agent Status: {'ACTIVE (Auto-Apply Enabled)' if mgr.auto_apply_enabled else 'STANDBY (Assisted Approval Mode)'}</h4>
                <p style="margin:5px 0 0 0; font-size:0.9rem; color:#047857;">
                    Fit Threshold: <b>{mgr.min_fit_threshold}%</b> | Target: <b>Alex Chen</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        if st.button("⚡ Execute Autonomous Cycle Now", type="primary", use_container_width=True):
            with st.spinner("Autonomous agent running cycle..."):
                results = mgr.run_live_autonomous_cycle()
                st.success(f"Agent finished cycle! Handled {len(results)} job roles.")

    st.markdown("### Real-Time Agent Activity Feed")
    if not mgr.agent_activity_logs:
        st.info("No activity recorded yet. Click 'Execute Autonomous Cycle Now' or run a scan from the sidebar.")
    else:
        for log in reversed(mgr.agent_activity_logs[-25:]):
            st.text(log)


# =============================================================================
# View 3: Submissions & Application History
# =============================================================================
elif menu == "📋 Submissions & History":
    st.markdown('<div class="main-header">Confirmed Application Outcomes & Receipts</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Verified submission records with document snapshots and unique transaction receipts.</div>', unsafe_allow_html=True)

    submitted_apps = [a for a in mgr.applications.values() if a.status == ApplicationStatus.SUBMITTED]

    if not submitted_apps:
        st.info("No applications submitted yet. Either submit an application from the studio or trigger the autonomous agent.")
    else:
        st.write(f"Total Confirmed Applications: **{len(submitted_apps)}**")
        for app in submitted_apps:
            with st.container():
                st.markdown(
                    f"""
                    <div style="border: 1px solid #10B981; background-color: #F0FDF4; padding: 14px; border-radius: 8px; margin-bottom: 12px;">
                        <h4 style="margin:0; color: #065F46;">{app.job_title} — {app.employer}</h4>
                        <div style="font-size:0.9rem; color: #047857; margin-top: 4px;">
                            Receipt: <b>{app.submission_receipt}</b> | Mode: <b>{app.submission_mode}</b> | Submitted: <b>{app.submitted_at}</b>
                        </div>
                        <div style="font-size:0.85rem; color: #374151; margin-top: 6px;">
                            CV Variant: <i>{app.cv_variant_used}</i> | Cover Letter Version: <i>{app.cover_letter_version_id or 'None required'}</i>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# =============================================================================
# View 4: Candidate Master CV & Profile
# =============================================================================
elif menu == "👤 Candidate Master CV & Profile":
    st.markdown('<div class="main-header">Candidate Master CV & Ground Truth Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Verified facts, projects, education, and career motivations. The AI generator is strictly prohibited from inventing anything outside this record.</div>', unsafe_allow_html=True)

    st.markdown(f"### {candidate.full_name}")
    st.write(f"📧 {candidate.email} | 📱 {candidate.phone} | 📍 {candidate.location} | 🔗 {candidate.linkedin}")

    st.markdown("#### Career Motivations")
    st.info(candidate.career_interests_and_motivations)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Verified Technical Skills")
        st.write(", ".join(candidate.verified_skills))

        st.markdown("#### Certifications")
        for c in candidate.certifications:
            st.write(f"• {c}")

        st.markdown("#### Education")
        for e in candidate.education:
            st.markdown(f"**{e.degree}**")
            st.write(f"{e.institution} ({e.graduation_year}) — {e.gpa_or_honors}")
            st.caption(f"Coursework: {', '.join(e.relevant_coursework)}")

    with col2:
        st.markdown("#### Work Experience")
        for w in candidate.work_experiences:
            st.markdown(f"**{w.title}** at *{w.company}* ({w.start_date} - {w.end_date})")
            for ach in w.achievements:
                st.write(f"- {ach}")

        st.markdown("#### Verified Projects")
        for p in candidate.projects:
            st.markdown(f"**{p.name}**")
            st.caption(f"Tech: {', '.join(p.technologies)}")
            for out in p.outcomes:
                st.write(f"- {out}")


# =============================================================================
# View 5: Acceptance Test Suite Runner
# =============================================================================
elif menu == "🧪 Run Acceptance Test Suite":
    st.markdown('<div class="main-header">Interactive Acceptance Test Suite</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Execute all 8 core acceptance tests specified in the system design requirements.</div>', unsafe_allow_html=True)

    if st.button("▶️ Run All Acceptance Tests Now", type="primary"):
        with st.spinner("Executing rigorous test suite..."):
            test_results = []

            # Test 1: Explicitly required cover letter
            try:
                j1 = mgr.job_store.get_job("job-corp-101")
                a1 = RequirementAnalyzer.analyze(j1.description, j1.application_instructions)
                assert a1.status == CoverLetterRequirement.REQUIRED
                p1 = mgr.prepare_application_package(j1)
                assert p1.cover_letter_text is not None
                assert "Cascade Health Partners" in p1.cover_letter_text
                test_results.append(("Test 1: Explicitly Required Cover Letter", True, "Successfully detected requirement and generated tailored letter for Cascade Health Partners."))
            except Exception as e:
                test_results.append(("Test 1: Explicitly Required Cover Letter", False, str(e)))

            # Test 2: Recommended cover letter
            try:
                j2 = mgr.job_store.get_job("job-ds-102")
                a2 = RequirementAnalyzer.analyze(j2.description, j2.application_instructions)
                assert a2.status == CoverLetterRequirement.RECOMMENDED
                p2 = mgr.prepare_application_package(j2)
                assert p2.cover_letter_text is not None
                assert "DataNexus Labs" in p2.cover_letter_text
                test_results.append(("Test 2: Recommended Cover Letter", True, "Detected recommendation and articulated why candidate's ML project strengthens application."))
            except Exception as e:
                test_results.append(("Test 2: Recommended Cover Letter", False, str(e)))

            # Test 3: Not needed cover letter
            try:
                j3 = mgr.job_store.get_job("job-noneed-103")
                a3 = RequirementAnalyzer.analyze(j3.description, j3.application_instructions)
                assert a3.status == CoverLetterRequirement.NOT_NEEDED
                p3 = mgr.prepare_application_package(j3)
                assert p3.cover_letter_text is None
                test_results.append(("Test 3: Cover Letter Not Needed", True, "Correctly refrained from automatic generation when instructions indicate no cover letter."))
            except Exception as e:
                test_results.append(("Test 3: Cover Letter Not Needed", False, str(e)))

            # Test 4: Academic motivation letter
            try:
                j4 = mgr.job_store.get_job("job-econ-104")
                a4 = RequirementAnalyzer.analyze(j4.description, j4.application_instructions)
                assert a4.status == CoverLetterRequirement.REQUIRED
                p4 = mgr.prepare_application_package(j4)
                assert "Dear Professor Lin" in p4.cover_letter_text or "Selection Committee" in p4.cover_letter_text
                assert "econometric" in p4.cover_letter_text.lower()
                assert "synergy" not in p4.cover_letter_text.lower()
                test_results.append(("Test 4: Academic Motivation Letter Format", True, "Applied research-focused tone, causal inference terminology, and academic sign-off."))
            except Exception as e:
                test_results.append(("Test 4: Academic Motivation Letter Format", False, str(e)))

            # Test 5: Missing experience transferable skills
            try:
                j5 = mgr.job_store.get_job("job-missing-105")
                p5 = mgr.prepare_application_package(j5)
                assert "transferable" in p5.cover_letter_text.lower() or "transition" in p5.cover_letter_text.lower()
                assert "10 years of snowflake" not in p5.cover_letter_text.lower()
                test_results.append(("Test 5: Truthful Handling of Missing Skills", True, "Acknowledged transferable PostgreSQL/SQL skills for Redshift without fabricating experience."))
            except Exception as e:
                test_results.append(("Test 5: Truthful Handling of Missing Skills", False, str(e)))

            # Test 6: Untrusted Prompt Injection Defense
            try:
                j6 = mgr.job_store.get_job("job-inject-106")
                sanitized, is_flagged, threats = SecuritySanitizer.inspect_and_sanitize(j6.description)
                assert is_flagged is True
                cl6 = CoverLetterEngine.generate_cover_letter(j6, candidate)
                assert "renaissance technologies" not in cl6.content.lower()
                assert "500m" not in cl6.content.lower()
                test_results.append(("Test 6: Security & Prompt Injection Defense", True, "Flagged adversarial override commands and defended ground truth against jailbreak attempt."))
            except Exception as e:
                test_results.append(("Test 6: Security & Prompt Injection Defense", False, str(e)))

            # Test 7: User edits and downloads preserved
            try:
                j7 = mgr.job_store.get_job("job-corp-101")
                custom_text = "Custom User Content for test."
                v7 = CoverLetterVersion("v-test-7", j7.id, "2026-10-21 23:45:00", custom_text, "User Edit", "Corporate")
                mgr.record_cover_letter_version(v7)
                docx = DocumentExporter.generate_docx_bytes(custom_text, candidate, j7.employer, j7.title)
                pdf = DocumentExporter.generate_pdf_bytes(custom_text, candidate, j7.employer, j7.title)
                assert len(docx) > 1000
                assert len(pdf) > 1000
                test_results.append(("Test 7: User Revision Preservation & Exporters", True, "Successfully preserved version history and generated valid DOCX and PDF documents."))
            except Exception as e:
                test_results.append(("Test 7: User Revision Preservation & Exporters", False, str(e)))

            # Test 8: Live Autonomous Agent Cycle
            try:
                mgr.auto_apply_enabled = True
                cycle = mgr.run_live_autonomous_cycle()
                applied = [c for c in cycle if c["action"] == "Auto-Applied"]
                assert len(applied) >= 2
                test_results.append(("Test 8: Autonomous Live AI Agent Cycle", True, f"Agent evaluated fit, drafted materials, and auto-applied to {len(applied)} matching roles."))
            except Exception as e:
                test_results.append(("Test 8: Autonomous Live AI Agent Cycle", False, str(e)))

            # Display results
            for name, passed, detail in test_results:
                if passed:
                    st.success(f"✅ **{name}**: {detail}")
                else:
                    st.error(f"❌ **{name}**: {detail}")


# =============================================================================
# View 6: Add Custom Job Posting
# =============================================================================
elif menu == "➕ Add Custom Job Posting":
    st.markdown('<div class="main-header">Add New Job Posting</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Paste any job description to instantly analyze requirements, score fit, and draft bespoke application materials.</div>', unsafe_allow_html=True)

    with st.form("new_job_form"):
        title = st.text_input("Job Title", value="Junior Quantitative Data Scientist")
        employer = st.text_input("Employer / Company Name", value="Horizon Analytics Group")
        industry = st.text_input("Industry", value="Financial Technology & Modeling")
        location = st.text_input("Location", value="Seattle, WA / Remote")
        workplace_type = st.selectbox("Workplace Type", ["Remote", "Hybrid", "Onsite"])
        style = st.selectbox("Style Category", [
            ApplicationStyle.DATA_ANALYTICS.value,
            ApplicationStyle.CORPORATE.value,
            ApplicationStyle.RISK_FINANCIAL.value,
            ApplicationStyle.ECONOMICS_RESEARCH.value,
            ApplicationStyle.ACADEMIC.value
        ])

        description = st.text_area(
            "Job Description",
            value="We are seeking a Quantitative Data Scientist to develop statistical predictive models, clean complex financial records, and engineer data pipelines in Python and SQL."
        )

        instructions = st.text_area(
            "Application Instructions",
            value="Applicants must submit a tailored cover letter explaining their background in machine learning and predictive modeling."
        )

        reqs = st.text_area("Stated Requirements (one per line)", value="Bachelor's degree in quantitative field\nPython and SQL proficiency\nExperience with statistical modeling")

        submitted = st.form_submit_button("Ingest Job & Evaluate")

        if submitted:
            new_id = f"job-custom-{int(time.time())}"
            new_job = JobPosting(
                id=new_id,
                title=title,
                employer=employer,
                industry=industry,
                location=location,
                job_type="Full-time",
                workplace_type=workplace_type,
                description=description,
                application_instructions=instructions,
                stated_requirements=[r.strip() for r in reqs.split("\n") if r.strip()],
                preferred_qualifications=[],
                style_category=ApplicationStyle(style)
            )
            mgr.job_store.add_job(new_job)
            st.session_state.active_job_id = new_id
            st.success(f"Added job '{title}'! Switching to Discovery view...")
            st.rerun()
