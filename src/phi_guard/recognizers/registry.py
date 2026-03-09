"""PHI Guard Recognizer Registry - Presidio engine setup."""

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from phi_guard.recognizers.ssn import build_ssn_recognizer
from phi_guard.recognizers.mrn import build_mrn_recognizer
from phi_guard.recognizers.vin import build_vin_recognizer
from phi_guard.recognizers.drivers_license import build_drivers_license_recognizer
from phi_guard.recognizers.dea import build_dea_recognizer
from phi_guard.recognizers.npi import build_npi_recognizer
from phi_guard.recognizers.medicare import build_medicare_recognizer
from phi_guard.recognizers.age import build_age_recognizer
from phi_guard.recognizers.zip_code import build_zip_code_recognizer
from phi_guard.recognizers.account import build_account_recognizer
from phi_guard.recognizers.device import build_device_recognizer
from phi_guard.recognizers.fax import build_fax_recognizer


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

    # Register custom PHI recognizers
    # Presidio built-in recognizers (PHONE_NUMBER, EMAIL_ADDRESS, DATE_TIME,
    # IP_ADDRESS, URL) load automatically

    # HIPAA identifiers
    _analyzer_engine.registry.add_recognizer(build_ssn_recognizer())      # PHI #7
    _analyzer_engine.registry.add_recognizer(build_mrn_recognizer())      # PHI #8
    _analyzer_engine.registry.add_recognizer(build_vin_recognizer())      # PHI #14
    _analyzer_engine.registry.add_recognizer(build_drivers_license_recognizer())  # PHI #13
    _analyzer_engine.registry.add_recognizer(build_dea_recognizer())      # PHI #13
    _analyzer_engine.registry.add_recognizer(build_npi_recognizer())      # PHI #13
    _analyzer_engine.registry.add_recognizer(build_medicare_recognizer()) # PHI #11
    _analyzer_engine.registry.add_recognizer(build_age_recognizer())      # PHI #17
    _analyzer_engine.registry.add_recognizer(build_zip_code_recognizer()) # PHI #3
    _analyzer_engine.registry.add_recognizer(build_account_recognizer())  # PHI #12
    _analyzer_engine.registry.add_recognizer(build_device_recognizer())   # PHI #15
    _analyzer_engine.registry.add_recognizer(build_fax_recognizer())      # PHI #5

    return _analyzer_engine


def get_supported_entities() -> list[str]:
    """Return list of supported entity types."""
    engine = get_analyzer_engine()
    return engine.get_supported_entities(language="en")


def reset_analyzer_engine() -> None:
    """Reset the cached analyzer engine (for testing)."""
    global _analyzer_engine
    _analyzer_engine = None
