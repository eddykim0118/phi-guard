"""MRN Recognizer - HIPAA PHI #8: Medical Record Number."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_mrn_recognizer() -> PatternRecognizer:
    """
    Build MRN recognizer for Epic-style 7-8 digit numbers.

    Low base score (0.3) requires context words to pass threshold.
    This prevents false positives on random number sequences.
    """
    return PatternRecognizer(
        supported_entity="MRN",
        patterns=[
            Pattern(
                name="MRN (Epic style 7-8 digits)",
                regex=r"\b\d{7,8}\b",
                score=0.3,
            ),
        ],
        context=[
            "mrn", "medical record", "medical record number",
            "patient id", "patient number", "chart number",
            "record number", "chart",
            "MRN", "Medical Record Number", "Patient ID",
        ],
    )
