"""
MRN (Medical Record Number) Recognizer

HIPAA PHI #8: Medical Record Number
병원에서 환자를 식별하는 고유 번호입니다.

문제점:
- 병원마다 MRN 형식이 다름 (Epic, Cerner, etc.)
- 단순 숫자열이라 false positive 위험 높음

해결책:
- Epic EHR 기준 7-8자리 숫자 패턴 사용
- 낮은 기본 점수(0.3)로 context 없이는 탐지 안 됨
- "MRN", "patient id" 등 context 단어가 있으면 점수 상승
"""

from presidio_analyzer import PatternRecognizer, Pattern


def build_mrn_recognizer() -> PatternRecognizer:
    """
    HIPAA PHI #8: Medical Record Number

    Epic EHR 기준 7-8자리 숫자 패턴
    Context 단어가 있을 때만 threshold(0.5)를 넘어서 탐지됨

    Returns:
        PatternRecognizer: MRN 탐지기
    """
    return PatternRecognizer(
        supported_entity="MRN",
        patterns=[
            Pattern(
                name="MRN (Epic style 7-8 digits)",
                regex=r"\b\d{7,8}\b",
                score=0.3,  # 낮은 점수 - context 없으면 threshold 못 넘음
            ),
        ],
        context=[
            # 영어 context words
            "mrn",
            "medical record",
            "medical record number",
            "patient id",
            "patient number",
            "chart number",
            "record number",
            "chart",
            # 대문자 버전
            "MRN",
            "Medical Record Number",
            "Patient ID",
        ],
    )
