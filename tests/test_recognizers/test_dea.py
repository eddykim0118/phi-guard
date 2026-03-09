"""DEA Number Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestDEAWithContext:
    """DEA number detection with context words."""

    @pytest.mark.parametrize(
        "text",
        [
            "DEA: AB1234563",
            "DEA Number AB1234563",
            "DEA# AB1234563",
        ],
    )
    def test_dea_with_context_detected(self, text: str):
        """DEA number with context word should be detected."""
        findings = scan_text(text)
        dea_findings = [f for f in findings if f.entity_type == "DEA_NUMBER"]
        assert len(dea_findings) >= 1, f"DEA not detected in: {text}"

    def test_dea_format(self):
        """DEA format: 2 letters + 7 digits."""
        findings = scan_text("DEA: AB1234563")
        dea_findings = [f for f in findings if f.entity_type == "DEA_NUMBER"]
        assert len(dea_findings) >= 1
        assert dea_findings[0].text == "AB1234563"


class TestDEAWithoutContext:
    """DEA should not be detected without context."""

    def test_dea_without_context_not_detected(self):
        findings = scan_text("AB1234563")
        dea_findings = [f for f in findings if f.entity_type == "DEA_NUMBER"]
        assert len(dea_findings) == 0


class TestDEAInvalidFormats:
    """Invalid DEA numbers should not be detected."""

    @pytest.mark.parametrize(
        "text",
        [
            "DEA: CB1234563",  # Invalid first letter (C not in ABFGMPRX)
            "DEA: AB123456",   # Too few digits (6)
            "DEA: AB12345678", # Too many digits (8)
        ],
    )
    def test_invalid_dea_not_detected(self, text: str):
        findings = scan_text(text)
        dea_findings = [f for f in findings if f.entity_type == "DEA_NUMBER"]
        assert len(dea_findings) == 0, f"Invalid DEA detected in: {text}"
