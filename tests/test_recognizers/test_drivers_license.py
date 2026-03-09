"""Driver's License Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestDriversLicenseWithContext:
    """Driver's license detection with context words."""

    @pytest.mark.parametrize(
        "text",
        [
            "DL: A1234567",
            "Driver's License: B12345678",
            "License Number D123456789",
        ],
    )
    def test_dl_with_context_detected(self, text: str):
        """Driver's license with context word should be detected."""
        findings = scan_text(text)
        dl_findings = [f for f in findings if f.entity_type == "DRIVERS_LICENSE"]
        assert len(dl_findings) >= 1, f"DL not detected in: {text}"

    def test_dl_california_format(self):
        """California format: letter + 7 digits."""
        findings = scan_text("Driver's license: A1234567")
        dl_findings = [f for f in findings if f.entity_type == "DRIVERS_LICENSE"]
        assert len(dl_findings) >= 1
        assert dl_findings[0].text == "A1234567"

    def test_dl_florida_format(self):
        """Florida format: letter + 12 digits."""
        findings = scan_text("DL# K123456789012")
        dl_findings = [f for f in findings if f.entity_type == "DRIVERS_LICENSE"]
        assert len(dl_findings) >= 1


class TestDriversLicenseSpecificPattern:
    """Letter + 7-12 digits is specific enough for US DL format.

    This pattern is unlikely to appear randomly, so it's detected
    even without explicit context words.
    """

    @pytest.mark.parametrize(
        "text",
        [
            "A1234567",  # 1 letter + 7 digits
            "The code is B12345678",  # 1 letter + 8 digits
        ],
    )
    def test_dl_specific_pattern_detected(self, text: str):
        """Letter + 7-12 digits is specific - detection expected."""
        findings = scan_text(text)
        dl_findings = [f for f in findings if f.entity_type == "DRIVERS_LICENSE"]
        assert len(dl_findings) >= 1, f"DL not detected in: {text}"
