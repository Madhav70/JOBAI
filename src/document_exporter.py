"""
JOBAI Document Exporter
Generates executive-quality DOCX and PDF documents from cover letter text.
Includes professional letterheads, clean typography, and calibrated margins.
"""

import io
import re
from typing import Optional
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.models import CandidateProfile


class DocumentExporter:
    """
    Exporters for converting cover letter markdown/plain-text into formatted DOCX and PDF documents.
    """

    @staticmethod
    def generate_docx_bytes(text: str, profile: CandidateProfile, employer: str, job_title: str) -> bytes:
        """
        Creates a professionally formatted Microsoft Word (.docx) document.
        """
        doc = Document()

        # Page setup: 0.8 inch margins
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.85)
            section.right_margin = Inches(0.85)

        # Style base font
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)
        font.color.rgb = RGBColor(0x22, 0x22, 0x22)

        # Candidate Header
        name_p = doc.add_paragraph()
        name_run = name_p.add_run(profile.full_name)
        name_run.font.size = Pt(18)
        name_run.font.bold = True
        name_run.font.color.rgb = RGBColor(0x11, 0x2E, 0x51)
        name_p.paragraph_format.space_after = Pt(2)

        contact_p = doc.add_paragraph()
        contact_text = f"{profile.location} | {profile.email} | {profile.phone} | {profile.linkedin}"
        contact_run = contact_p.add_run(contact_text)
        contact_run.font.size = Pt(9.5)
        contact_run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        contact_p.paragraph_format.space_after = Pt(14)

        # Horizontal accent line can be simulated with bottom border or paragraph
        rule_p = doc.add_paragraph()
        rule_p.paragraph_format.space_after = Pt(14)

        # Parse text into paragraphs
        # If the generated letter contains candidate name/header already, avoid duplicating
        clean_text = text.strip()
        lines = clean_text.split("\n\n")

        for para in lines:
            para = para.strip()
            if not para:
                continue
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.15
            p.add_run(para)

        # Save to buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_pdf_bytes(text: str, profile: CandidateProfile, employer: str, job_title: str) -> bytes:
        """
        Creates a clean, publication-ready PDF document using ReportLab.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.8 * inch,
            leftMargin=0.8 * inch,
            topMargin=0.8 * inch,
            bottomMargin=0.8 * inch
        )

        styles = getSampleStyleSheet()

        name_style = ParagraphStyle(
            'CandidateName',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#112E51'),
            spaceAfter=3
        )

        contact_style = ParagraphStyle(
            'CandidateContact',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#555555'),
            spaceAfter=12
        )

        body_style = ParagraphStyle(
            'CoverLetterBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14.5,
            textColor=colors.HexColor('#222222'),
            spaceAfter=10
        )

        story = []

        # Header
        story.append(Paragraph(profile.full_name, name_style))
        contact_line = f"{profile.location}  •  {profile.email}  •  {profile.phone}  •  {profile.linkedin}"
        story.append(Paragraph(contact_line, contact_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#112E51'), spaceAfter=14))

        # Body paragraphs
        paragraphs = text.strip().split("\n\n")
        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue
            # Escape HTML characters for ReportLab Paragraph
            safe_text = p_clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            # Support single newlines inside paragraph (like date / address block)
            safe_text = safe_text.replace("\n", "<br/>")
            story.append(Paragraph(safe_text, body_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
