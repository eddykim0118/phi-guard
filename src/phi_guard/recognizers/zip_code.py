"""Zip Code Recognizer - HIPAA PHI #3: Geographic Data Smaller Than State."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_zip_code_recognizer() -> PatternRecognizer:
    """
    Build ZIP code recognizer.

    HIPAA requires geographic data smaller than state to be de-identified.
    This includes ZIP codes (first 3 digits can be retained if population > 20,000).

    Formats:
    - 5-digit: 12345
    - 9-digit (ZIP+4): 12345-6789

    Note: Standalone ZIP codes have many false positives (any 5 digits).
    Context boosting is critical here.
    """
    return PatternRecognizer(
        supported_entity="ZIP_CODE",
        patterns=[
            Pattern(
                name="ZIP+4 (high confidence)",
                regex=r"\b\d{5}-\d{4}\b",
                score=0.7,
            ),
            Pattern(
                name="ZIP 5-digit (needs context)",
                regex=r"\b\d{5}\b",
                score=0.2,  # Low - needs context boost to reach 0.5
            ),
        ],
        context=[
            # Single words work best with Presidio
            "zip", "ZIP", "zipcode", "postal", "code",
            "address", "city", "state", "mailing", "location",
        ],
    )
