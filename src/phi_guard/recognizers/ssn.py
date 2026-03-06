from presidio_analyzer import PatternRecognizer, Pattern


def build_ssn_recognizer() -> PatternRecognizer:
    """
    HIPAA PHI #7: Social Security Number
    기본 Presidio UsSsnRecognizer는 score 0.05 (very weak) 이라
    threshold에 걸려 탐지 실패 -> 강한 버전으로 교체
    """
    return PatternRecognizer(
        supported_entity="US_SSN",
        patterns=[
            Pattern(
                name="SSN (strong)",
                regex=r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b",
                score=0.85,
            )
        ],
        context=["ssn", "social security", "social", "security", "SSN", "ss#"],
    )
