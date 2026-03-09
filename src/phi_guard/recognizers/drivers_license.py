"""Driver's License Recognizer - HIPAA PHI #13: Certificate/License Numbers."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_drivers_license_recognizer() -> PatternRecognizer:
    """
    Build Driver's License recognizer for common US formats.

    Different states have different formats. This covers the most common:
    - 7-9 digits (many states)
    - Letter + 7-12 digits (CA, FL, etc.)
    - Letter + 6 digits + letter (some states)

    Low base score requires context to avoid false positives.
    """
    return PatternRecognizer(
        supported_entity="DRIVERS_LICENSE",
        patterns=[
            Pattern(
                name="DL letter prefix (CA, FL, IL, etc.)",
                # Letter + 7-12 digits is specific enough for moderate confidence
                regex=r"\b[A-Z]\d{7,12}\b",
                score=0.5,  # Specific pattern - can pass threshold directly
            ),
            Pattern(
                name="DL numeric only (TX, NY, etc.)",
                regex=r"\b\d{8,9}\b",
                score=0.25,  # Lower score - too generic, high false positive risk
            ),
        ],
        context=[
            # Single words work best with Presidio context matching
            "driver", "drivers", "license", "DL", "DMV",
            "driving", "DL#", "state",
        ],
    )
