"""
JOBAI Requirement Analyzer
Determines whether a cover letter is Required, Recommended, Optional, Not needed, or Unclear.
Provides confidence metrics, explanation, and constraint extraction (e.g. word limits).
"""

import re
from typing import Optional, List, Tuple
from src.models import CoverLetterRequirement, RequirementAssessment


class RequirementAnalyzer:
    """
    Analyzes job descriptions and application instructions to assess cover letter requirement.
    """

    # Explicit positive signals for REQUIRED
    REQUIRED_PATTERNS = [
        r"(?i)\b(?:cover|motivation)\s+letter\s+(?:is\s+)?(?:required|mandatory|essential|must\s+be\s+submitted|is\s+necessary)\b",
        r"(?i)\bmust\s+(?:submit|attach|include|provide)\s+(?:an?\s+)?(?:[\w\-]+\s+)*(?:cover|motivation)\s+letter\b",
        r"(?i)\bplease\s+(?:submit|attach|include|provide)\s+(?:an?\s+)?(?:[\w\-]+\s+)*(?:cover|motivation)\s+letter\b",
        r"(?i)\bapplications\s+without\s+(?:an?\s+)?(?:[\w\-]+\s+)*(?:cover|motivation)\s+letter\s+will\s+not\s+be\s+considered\b",
        r"(?i)\ba\s+(?:[\w\-]+\s+)*motivation\s+letter\s+is\s+(?:required|mandatory|essential)\b",
        r"(?i)\bsubmit\s+your\s+resume\s+and\s+(?:an?\s+)?(?:[\w\-]+\s+)*(?:cover|motivation)\s+letter\b",
        r"(?i)\brequired\s+documents\s*:\s*.*(?:cover|motivation)\s+letter\b",
        r"(?i)\bcandidates\s+are\s+required\s+to\s+submit\s+(?:an?\s+)?(?:[\w\-]+\s+)*(?:cover|motivation)\s+letter\b"
    ]

    # Positive signals for RECOMMENDED
    RECOMMENDED_PATTERNS = [
        r"(?i)\b(?:cover|motivation)\s+letter\s+(?:is\s+)?(?:strongly\s+)?(?:recommended|encouraged|preferred|appreciated)\b",
        r"(?i)\b(?:an?\s+)?(?:[\w\-]+\s+)*(?:cover|motivation)\s+letter\s+is\s+strongly\s+preferred\b",
        r"(?i)\bwill\s+strengthen\s+your\s+application\b",
        r"(?i)\bapplicants\s+are\s+(?:strongly\s+)?encouraged\s+to\s+(?:include|submit)\s+(?:an?\s+)?(?:[\w\-]+\s+)*(?:cover|motivation)\s+letter\b",
        r"(?i)\bwhile\s+not\s+mandatory,?\s+(?:an?\s+)?(?:[\w\-]+\s+)*(?:cover|motivation)\s+letter\s+is\s+(?:highly\s+)?recommended\b",
        r"(?i)\b(?:cover|motivation)\s+letter\s+welcome\s+and\s+recommended\b"
    ]

    # Signals for OPTIONAL
    OPTIONAL_PATTERNS = [
        r"(?i)\b(?:cover|motivation)\s+letter\s+(?:is\s+)?optional\b",
        r"(?i)\byou\s+may\s+(?:optionally\s+)?(?:include|attach|submit)\s+(?:an?\s+)?(?:[\w\-]+\s+)*(?:cover|motivation)\s+letter\b",
        r"(?i)\boptional\s*:\s*(?:cover|motivation)\s+letter\b",
        r"(?i)\b(?:cover|motivation)\s+letter\s+accepted\s+but\s+not\s+required\b",
        r"(?i)\bif\s+you\s+wish,\s+you\s+may\s+submit\s+(?:an?\s+)?(?:[\w\-]+\s+)*(?:cover|motivation)\s+letter\b"
    ]

    # Signals for NOT NEEDED
    NOT_NEEDED_PATTERNS = [
        r"(?i)\bdo\s+not\s+(?:submit|attach|include|send)\s+(?:an?\s+)?(?:cover|motivation)\s+letter\b",
        r"(?i)\b(?:cover|motivation)\s+letters?\s+(?:are\s+)?not\s+(?:accepted|read|reviewed|required|needed)\b",
        r"(?i)\bplease\s+do\s+not\s+send\s+(?:an?\s+)?(?:cover|motivation)\s+letter\b",
        r"(?i)\bno\s+(?:cover|motivation)\s+letter\s+needed\b",
        r"(?i)\bno\s+(?:cover|motivation)\s+letter\s+(?:is\s+)?required\b",
        r"(?i)\bonly\s+submit\s+your\s+resume\b",
        r"(?i)\bresume\s+only\b",
        r"(?i)\bwe\s+do\s+not\s+accept\s+(?:cover|motivation)\s+letters\b"
    ]

    # Word count constraint extraction
    WORD_LIMIT_PATTERNS = [
        r"(?i)(?:maximum|max|under|up\s+to|no\s+more\s+than)\s+(\d{2,4})\s+words",
        r"(?i)(\d{2,4})\s*-\s*(\d{2,4})\s+words",
        r"(?i)limit\s+(?:of\s+)?(\d{2,4})\s+words",
        r"(?i)one\s+page\s+(?:maximum|limit)?"
    ]

    @classmethod
    def analyze(cls, description: str, instructions: str) -> RequirementAssessment:
        combined_text = f"{instructions}\n\n{description}"
        clues: List[str] = []

        # 1. Check NOT NEEDED first to avoid false positives
        for pattern in cls.NOT_NEEDED_PATTERNS:
            match = re.search(pattern, combined_text)
            if match:
                clue = match.group(0).strip()
                clues.append(f"Found negative instruction: '{clue}'")
                word_limit = cls._extract_word_limit(combined_text)
                return RequirementAssessment(
                    status=CoverLetterRequirement.NOT_NEEDED,
                    confidence="High",
                    confidence_score=0.95,
                    explanation="The employer explicitly specifies that a cover letter is not required or not accepted.",
                    extracted_clues=clues,
                    word_limit=word_limit
                )

        # 2. Check REQUIRED
        for pattern in cls.REQUIRED_PATTERNS:
            match = re.search(pattern, combined_text)
            if match:
                clue = match.group(0).strip()
                clues.append(f"Found explicit mandate: '{clue}'")
                word_limit = cls._extract_word_limit(combined_text)
                return RequirementAssessment(
                    status=CoverLetterRequirement.REQUIRED,
                    confidence="High",
                    confidence_score=0.96,
                    explanation="The employer explicitly requests or mandates a cover letter / motivation letter.",
                    extracted_clues=clues,
                    word_limit=word_limit
                )

        # 3. Check RECOMMENDED
        for pattern in cls.RECOMMENDED_PATTERNS:
            match = re.search(pattern, combined_text)
            if match:
                clue = match.group(0).strip()
                clues.append(f"Found recommendation statement: '{clue}'")
                word_limit = cls._extract_word_limit(combined_text)
                return RequirementAssessment(
                    status=CoverLetterRequirement.RECOMMENDED,
                    confidence="High",
                    confidence_score=0.90,
                    explanation="The job description indicates that submitting a cover letter is preferred and will strengthen the application.",
                    extracted_clues=clues,
                    word_limit=word_limit
                )

        # 4. Check OPTIONAL
        for pattern in cls.OPTIONAL_PATTERNS:
            match = re.search(pattern, combined_text)
            if match:
                clue = match.group(0).strip()
                clues.append(f"Found optional field notice: '{clue}'")
                word_limit = cls._extract_word_limit(combined_text)
                return RequirementAssessment(
                    status=CoverLetterRequirement.OPTIONAL,
                    confidence="High",
                    confidence_score=0.88,
                    explanation="The employer states that a cover letter is optional and welcome if submitted.",
                    extracted_clues=clues,
                    word_limit=word_limit
                )

        # 5. Check if mentions cover letter at all in ambiguous context
        mention_pattern = r"(?i)\b(cover\s+letter|motivation\s+letter|letter\s+of\s+interest)\b"
        if re.search(mention_pattern, combined_text):
            clues.append("Found incidental mention of 'cover letter' or 'motivation letter' without clear directive.")
            return RequirementAssessment(
                status=CoverLetterRequirement.UNCLEAR,
                confidence="Medium",
                confidence_score=0.55,
                explanation="The application instructions mention a cover letter, but do not clearly specify whether it is required, recommended, or optional. Candidate decision advised.",
                extracted_clues=clues,
                word_limit=cls._extract_word_limit(combined_text)
            )

        # 6. Completely silent on cover letters
        return RequirementAssessment(
            status=CoverLetterRequirement.UNCLEAR,
            confidence="Low",
            confidence_score=0.40,
            explanation="No instructions or mentions regarding a cover letter were found in the job posting. Marked as 'Unclear' for user discretion.",
            extracted_clues=["No cover letter keywords detected in posting."],
            word_limit=None
        )

    @classmethod
    def _extract_word_limit(cls, text: str) -> Optional[int]:
        for pattern in cls.WORD_LIMIT_PATTERNS:
            m = re.search(pattern, text)
            if m:
                # If group 1 matched a number
                for grp in m.groups():
                    if grp and grp.isdigit():
                        return int(grp)
                if "one page" in m.group(0).lower():
                    return 450
        return None
