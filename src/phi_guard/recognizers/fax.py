"""Fax Number Recognizer - HIPAA PHI #5: Fax Numbers."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_fax_recognizer() -> PatternRecognizer:
    """
    Build fax number recognizer.

    HIPAA lists fax numbers separately from phone numbers, though the
    format is identical. This recognizer specifically looks for fax
    numbers using context words.

    Same format as phone: 10 digits with optional separators.
    """
    return PatternRecognizer(
        supported_entity="FAX_NUMBER",
        patterns=[
            Pattern(
                name="Fax (xxx) xxx-xxxx",
                regex=r"\(\d{3}\)\s*\d{3}[-.]?\d{4}",
                score=0.3,
            ),
            Pattern(
                name="Fax xxx-xxx-xxxx",
                regex=r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b",
                score=0.3,
            ),
        ],
        context=[
            "fax", "FAX", "facsimile", "fax number", "fax#",
            "fax:", "f:", "telefax",
        ],
    )
