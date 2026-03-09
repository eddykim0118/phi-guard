"""NPI Recognizer - HIPAA PHI #13: Certificate/License Numbers."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_npi_recognizer() -> PatternRecognizer:
    """
    Build NPI (National Provider Identifier) recognizer.

    NPI is a unique 10-digit identification number for healthcare providers.
    Required for all HIPAA transactions.
    Format: 10 digits, first digit is always 1 or 2.

    Note: NPI has a Luhn checksum but we don't validate it here to catch
    incorrectly transcribed numbers too.
    """
    return PatternRecognizer(
        supported_entity="NPI",
        patterns=[
            Pattern(
                name="NPI (10 digits starting with 1 or 2)",
                regex=r"\b[12]\d{9}\b",
                score=0.4,  # Context boost needed to reach 0.5
            ),
        ],
        context=[
            # Single words work best with Presidio
            "npi", "NPI", "provider", "Provider", "national", "National",
            "identifier", "NPI#", "npi#", "healthcare",
        ],
    )
