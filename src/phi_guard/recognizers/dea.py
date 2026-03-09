"""DEA Number Recognizer - HIPAA PHI #13: Certificate/License Numbers."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_dea_recognizer() -> PatternRecognizer:
    """
    Build DEA (Drug Enforcement Administration) number recognizer.

    DEA numbers identify practitioners authorized to prescribe controlled substances.
    Format: 2 letters + 7 digits where last digit is checksum.
    First letter indicates registrant type (A, B, F, G, M, P, R, X).
    Second letter is first letter of registrant's last name.

    Example: AB1234563 (valid DEA format)
    """
    return PatternRecognizer(
        supported_entity="DEA_NUMBER",
        patterns=[
            Pattern(
                name="DEA Number",
                # First letter: registrant type, second: last name initial, then 7 digits
                regex=r"\b[ABFGMPRX][A-Z]\d{7}\b",
                score=0.35,  # Low base - needs context to reach 0.5 threshold
            ),
        ],
        context=[
            "dea", "DEA", "dea number", "DEA#", "dea#",
            "drug enforcement", "prescriber", "controlled substance",
            "schedule", "prescription",
        ],
    )
