from presidio_analyzer import PatternRecognizer, Pattern


def build_mrn_recognizer() -> PatternRecognizer:
    """
    HIPAA PHI #8: Medical Record Number
    Presidio에 기본 탑재 없음 -> PHI Guard 핵심 차별화 포인트
    """
    return PatternRecognizer(
        supported_entity="MEDICAL_RECORD_NUMBER",
        patterns=[
            Pattern(
                name="MRN (explicit label)",
                regex=r"\bMRN[:\s#]?\s*\d{6,10}\b",
                score=0.9,
            ),
            Pattern(
                name="MRN (generic)",
                regex=r"\b\d{6,10}\b",
                score=0.3,
            ),
        ],
        context=["mrn", "MRN", "medical record", "chart", "patient id", "record number"],
    )
