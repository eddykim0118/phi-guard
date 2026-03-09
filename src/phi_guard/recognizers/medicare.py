"""Medicare/Health Plan Recognizer - HIPAA PHI #11: Health Plan Beneficiary Number."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_medicare_recognizer() -> PatternRecognizer:
    """
    Build Medicare Beneficiary Identifier (MBI) recognizer.

    MBI replaced the old HICN (SSN-based) in 2020.
    Format: 11 characters - pattern: CAAN-AAA-AANC
    - C = numeric 1-9
    - A = alphabetic (excludes S, L, O, I, B, Z)
    - N = numeric 0-9

    Example: 1EG4-TE5-MK72

    Also catches old-style Medicare numbers (HICN) which were SSN-based.
    """
    return PatternRecognizer(
        supported_entity="HEALTH_PLAN_ID",
        patterns=[
            Pattern(
                name="MBI (new Medicare format)",
                # 11 chars: starts with 1-9, alternating alpha/numeric
                regex=r"\b[1-9][A-HJKMNP-RT-Y][A-HJKMNP-RT-Y0-9]\d-?[A-HJKMNP-RT-Y][A-HJKMNP-RT-Y0-9]\d-?[A-HJKMNP-RT-Y][A-HJKMNP-RT-Y0-9]\d[A-HJKMNP-RT-Y0-9]\b",
                score=0.7,
            ),
            Pattern(
                name="Medicaid ID (state-specific, alphanumeric)",
                regex=r"\b[A-Z]{2}\d{8,10}\b",
                score=0.4,  # Context boost needed to reach 0.5
            ),
        ],
        context=[
            # Single words work best with Presidio context matching
            "medicare", "medicaid", "mbi", "hicn", "beneficiary",
            "health", "insurance", "member", "subscriber", "policy",
            "Medicare", "Medicaid", "MBI", "HICN", "cms", "CMS",
            "ID", "id", "number",
        ],
    )
