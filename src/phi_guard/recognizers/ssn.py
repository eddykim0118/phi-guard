"""SSN Recognizer - HIPAA PHI #7: Social Security Number."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_ssn_recognizer() -> PatternRecognizer:
    """
    Build SSN recognizer with high confidence score.

    Pattern rejects invalid SSNs (000, 666 area numbers) but includes
    9xx range (ITINs) since they're also sensitive identifiers.
    """
    return PatternRecognizer(
        supported_entity="US_SSN",
        patterns=[
            Pattern(
                name="SSN (strong)",
                regex=r"\b(?!000|666)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b",
                score=0.85,
            )
        ],
        context=["ssn", "social security", "social", "security", "SSN", "ss#"],
    )
