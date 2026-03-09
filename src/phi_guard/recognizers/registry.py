"""PHI Guard Recognizer Registry - Presidio engine setup."""

from enum import Enum

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


class ScanMode(str, Enum):
    """Scanning mode for PHI detection."""

    FAST = "fast"  # Regex-only, no NLP (for pre-commit)
    FULL = "full"  # Regex + NLP/spaCy (for CI/CD)


_analyzer_engine_fast: AnalyzerEngine | None = None
_analyzer_engine_full: AnalyzerEngine | None = None


def _register_custom_recognizers(engine: AnalyzerEngine) -> None:
    """Register all custom PHI recognizers on the given engine."""
    # Presidio built-in recognizers (PHONE_NUMBER, EMAIL_ADDRESS, DATE_TIME,
    # IP_ADDRESS, URL) load automatically

    # HIPAA identifiers
    engine.registry.add_recognizer(build_ssn_recognizer())      # PHI #7
    engine.registry.add_recognizer(build_mrn_recognizer())      # PHI #8
    engine.registry.add_recognizer(build_vin_recognizer())      # PHI #14
    engine.registry.add_recognizer(build_drivers_license_recognizer())  # PHI #13
    engine.registry.add_recognizer(build_dea_recognizer())      # PHI #13
    engine.registry.add_recognizer(build_npi_recognizer())      # PHI #13
    engine.registry.add_recognizer(build_medicare_recognizer()) # PHI #11
    engine.registry.add_recognizer(build_age_recognizer())      # PHI #17
    engine.registry.add_recognizer(build_zip_code_recognizer()) # PHI #3
    engine.registry.add_recognizer(build_account_recognizer())  # PHI #12
    engine.registry.add_recognizer(build_device_recognizer())   # PHI #15
    engine.registry.add_recognizer(build_fax_recognizer())      # PHI #5


def get_analyzer_engine(mode: ScanMode = ScanMode.FULL) -> AnalyzerEngine:
    """Get or create the Presidio AnalyzerEngine for the specified mode.

    Args:
        mode: ScanMode.FAST for regex-only (fast, no NLP context boosting)
              ScanMode.FULL for regex + NLP (slower, higher accuracy)

    Returns:
        Cached AnalyzerEngine for the requested mode.
    """
    global _analyzer_engine_fast, _analyzer_engine_full

    if mode == ScanMode.FAST:
        if _analyzer_engine_fast is None:
            # Fast mode: no NLP engine = regex patterns only
            # Context boosting won't work, but it's ~10x faster
            _analyzer_engine_fast = AnalyzerEngine(
                supported_languages=["en"],
            )
            _register_custom_recognizers(_analyzer_engine_fast)
        return _analyzer_engine_fast

    # Full mode: load spaCy NLP engine for context boosting
    if _analyzer_engine_full is None:
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        nlp_engine = NlpEngineProvider(
            nlp_configuration=nlp_configuration
        ).create_engine()

        _analyzer_engine_full = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=["en"],
        )
        _register_custom_recognizers(_analyzer_engine_full)

    return _analyzer_engine_full


def get_supported_entities(mode: ScanMode = ScanMode.FULL) -> list[str]:
    """Return list of supported entity types."""
    engine = get_analyzer_engine(mode)
    return engine.get_supported_entities(language="en")


def reset_analyzer_engine() -> None:
    """Reset all cached analyzer engines (for testing)."""
    global _analyzer_engine_fast, _analyzer_engine_full
    _analyzer_engine_fast = None
    _analyzer_engine_full = None
