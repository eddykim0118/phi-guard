"""NPI (National Provider Identifier) Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestNPIWithContext:
    """NPI detection with context words."""

    @pytest.mark.parametrize(
        "text",
        [
            "NPI: 1234567890",
            "NPI 1234567890",
            "Provider ID: 1234567890",
            "National Provider Identifier 1234567890",
        ],
    )
    def test_npi_with_context_detected(self, text: str):
        """NPI with context word should be detected."""
        findings = scan_text(text)
        npi_findings = [f for f in findings if f.entity_type == "NPI"]
        assert len(npi_findings) >= 1, f"NPI not detected in: {text}"

    def test_npi_starting_with_1(self):
        findings = scan_text("NPI: 1234567890")
        npi_findings = [f for f in findings if f.entity_type == "NPI"]
        assert len(npi_findings) >= 1
        assert npi_findings[0].text == "1234567890"

    def test_npi_starting_with_2(self):
        findings = scan_text("NPI: 2345678901")
        npi_findings = [f for f in findings if f.entity_type == "NPI"]
        assert len(npi_findings) >= 1


class TestNPIWithoutContext:
    """NPI should not be detected without context."""

    @pytest.mark.parametrize(
        "text",
        [
            "1234567890",
            "The number is 1234567890",
        ],
    )
    def test_npi_without_context_not_detected(self, text: str):
        findings = scan_text(text)
        npi_findings = [f for f in findings if f.entity_type == "NPI"]
        assert len(npi_findings) == 0, f"False positive NPI detected in: {text}"


class TestNPIInvalidFormats:
    """Invalid NPIs should not be detected."""

    @pytest.mark.parametrize(
        "text",
        [
            "NPI: 0123456789",  # Starts with 0
            "NPI: 3234567890",  # Starts with 3
            "NPI: 123456789",   # 9 digits
            "NPI: 12345678901", # 11 digits
        ],
    )
    def test_invalid_npi_not_detected(self, text: str):
        findings = scan_text(text)
        npi_findings = [f for f in findings if f.entity_type == "NPI"]
        assert len(npi_findings) == 0, f"Invalid NPI detected in: {text}"
