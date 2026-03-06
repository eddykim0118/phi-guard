"""
PHI Guard Recognizer Registry

이 모듈은 모든 PHI recognizer를 Presidio AnalyzerEngine에 등록합니다.

왜 이게 필요한가?
- Presidio는 AnalyzerEngine을 통해 텍스트를 분석함
- AnalyzerEngine은 RecognizerRegistry에서 recognizer들을 가져옴
- 우리가 만든 커스텀 recognizer를 여기서 등록해야 사용 가능

구조:
    AnalyzerEngine
        └── RecognizerRegistry
            ├── SSN Recognizer (우리 것)
            ├── MRN Recognizer (나중에 추가)
            └── ...
        └── NlpEngine (spaCy)
"""

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from phi_guard.recognizers.ssn import build_ssn_recognizer
from phi_guard.recognizers.mrn import build_mrn_recognizer


# 싱글톤 패턴: 엔진은 한 번만 생성하고 재사용
# (spaCy 모델 로딩이 느리기 때문)
_analyzer_engine: AnalyzerEngine | None = None


def get_analyzer_engine() -> AnalyzerEngine:
    """
    PHI 분석을 위한 Presidio AnalyzerEngine을 반환합니다.

    첫 호출 시 엔진을 생성하고, 이후에는 캐시된 인스턴스를 반환합니다.
    이렇게 하는 이유: spaCy 모델 로딩에 몇 초 걸리므로 매번 새로 만들면 느림.

    Returns:
        AnalyzerEngine: 모든 PHI recognizer가 등록된 분석 엔진
    """
    global _analyzer_engine

    if _analyzer_engine is not None:
        return _analyzer_engine

    # NLP 엔진 설정 (spaCy)
    # en_core_web_sm: 작은 영어 모델 (12MB), MVP에 적합
    # 나중에 정확도 높이려면 en_core_web_lg (500MB)로 교체 가능
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "en", "model_name": "en_core_web_sm"}
        ],
    }
    nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()

    # AnalyzerEngine 생성
    # supported_languages: 지원할 언어 (현재는 영어만)
    _analyzer_engine = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["en"],
    )

    # 커스텀 recognizer 등록
    # Presidio 기본 recognizer들은 자동으로 로드됨 (PHONE_NUMBER, EMAIL_ADDRESS 등)
    # 우리 것은 수동으로 추가해야 함
    _analyzer_engine.registry.add_recognizer(build_ssn_recognizer())
    _analyzer_engine.registry.add_recognizer(build_mrn_recognizer())

    return _analyzer_engine


def get_supported_entities() -> list[str]:
    """
    현재 지원하는 엔티티 타입 목록을 반환합니다.

    Returns:
        list[str]: ["US_SSN", "PERSON", "EMAIL_ADDRESS", ...] 같은 엔티티 타입들
    """
    engine = get_analyzer_engine()
    return engine.get_supported_entities(language="en")
