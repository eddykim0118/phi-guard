"""Age Recognizer - HIPAA PHI #17: Ages over 89."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_age_recognizer() -> PatternRecognizer:
    """
    Build recognizer for ages over 89.

    HIPAA considers ages over 89 as PHI because the population is small
    enough that combined with other data, individuals could be identified.

    Examples detected:
    - "age 92", "age: 95"
    - "90 years old", "91-year-old"
    - "aged 93", "93 y/o"
    """
    return PatternRecognizer(
        supported_entity="AGE_OVER_89",
        patterns=[
            Pattern(
                name="Age 90+ explicit",
                # "age 90", "age: 95", "age 102"
                regex=r"\bage[:\s]+(?:9[0-9]|1[0-4][0-9])\b",
                score=0.8,
            ),
            Pattern(
                name="Years old 90+",
                # "90 years old", "95-year-old", "101 year old"
                regex=r"\b(?:9[0-9]|1[0-4][0-9])[\s-]*(?:years?[\s-]*old|y/?o)\b",
                score=0.8,
            ),
            Pattern(
                name="Aged 90+",
                regex=r"\baged\s+(?:9[0-9]|1[0-4][0-9])\b",
                score=0.8,
            ),
        ],
        context=[
            "patient", "resident", "member", "client",
            "elderly", "geriatric", "senior",
            "birthday", "birth", "dob", "DOB",
        ],
    )
