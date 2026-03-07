from presidio_analyzer import PatternRecognizer, Pattern


def build_ssn_recognizer() -> PatternRecognizer:
    """
    HIPAA PHI #7: Social Security Number

    기본 Presidio UsSsnRecognizer는 score 0.05 (very weak) 이라
    threshold에 걸려 탐지 실패 -> 강한 버전으로 교체

    패턴 설명:
    - 000, 666: SSA가 절대 발급 안 하는 area number
    - 9xx: ITIN (Individual Taxpayer ID) - SSN 아니지만 민감 정보라 탐지
    - 00 (group): 무효
    - 0000 (serial): 무효
    """
    return PatternRecognizer(
        supported_entity="US_SSN",
        patterns=[
            Pattern(
                name="SSN (strong)",
                # 9xx (ITIN) 포함 - 민감 정보이므로 같이 탐지
                regex=r"\b(?!000|666)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b",
                score=0.85,
            )
        ],
        context=["ssn", "social security", "social", "security", "SSN", "ss#"],
    )
