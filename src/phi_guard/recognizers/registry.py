"""PHI Guard Recognizer Registry - Presidio engine setup."""

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from phi_guard.recognizers.ssn import build_ssn_recognizer
from phi_guard.recognizers.mrn import build_mrn_recognizer


_analyzer_engine: AnalyzerEngine | None = None


def get_analyzer_engine() -> AnalyzerEngine:
    """Get or create the Presidio AnalyzerEngine (singleton for performance)."""
    global _analyzer_engine

    if _analyzer_engine is not None:
        return _analyzer_engine

    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
    }
    nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()

    _analyzer_engine = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["en"],
    )

    # Register custom recognizers (Presidio defaults load automatically)
    _analyzer_engine.registry.add_recognizer(build_ssn_recognizer())
    _analyzer_engine.registry.add_recognizer(build_mrn_recognizer())

    return _analyzer_engine


def get_supported_entities() -> list[str]:
    """Return list of supported entity types."""
    engine = get_analyzer_engine()
    return engine.get_supported_entities(language="en")
