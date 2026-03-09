"""ZIP Code Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestZIPPlus4:
    """ZIP+4 format (high confidence)."""

    @pytest.mark.parametrize(
        "text",
        [
            "ZIP: 12345-6789",
            "Postal code 12345-6789",
            "Address: 123 Main St, City, ST 12345-6789",
        ],
    )
    def test_zip_plus_4_detected(self, text: str):
        """ZIP+4 should be detected with or without context."""
        findings = scan_text(text)
        zip_findings = [f for f in findings if f.entity_type == "ZIP_CODE"]
        assert len(zip_findings) >= 1, f"ZIP+4 not detected in: {text}"


class TestZIP5WithContext:
    """5-digit ZIP with context."""

    @pytest.mark.parametrize(
        "text",
        [
            "ZIP: 12345",
            "Zip code 90210",
            "postal code 10001",
        ],
    )
    def test_zip_5_with_context_detected(self, text: str):
        """5-digit ZIP with context should be detected."""
        findings = scan_text(text)
        zip_findings = [f for f in findings if f.entity_type == "ZIP_CODE"]
        assert len(zip_findings) >= 1, f"ZIP not detected in: {text}"


class TestZIP5WithoutContext:
    """5-digit ZIP without context should NOT be detected (false positive risk)."""

    @pytest.mark.parametrize(
        "text",
        [
            "12345",
            "The number is 90210",
            "Order #10001",
        ],
    )
    def test_zip_5_without_context_not_detected(self, text: str):
        """5-digit numbers without context should not be detected as ZIP."""
        findings = scan_text(text)
        zip_findings = [f for f in findings if f.entity_type == "ZIP_CODE"]
        assert len(zip_findings) == 0, f"False positive ZIP in: {text}"


class TestZIPInAddress:
    """ZIP code in full address."""

    def test_zip_in_address_with_zip_plus_4(self):
        """ZIP+4 in address is detected (high confidence pattern)."""
        text = "Patient address: 123 Main St, Boston, MA 02101-1234"
        findings = scan_text(text)
        zip_findings = [f for f in findings if f.entity_type == "ZIP_CODE"]
        assert len(zip_findings) >= 1

    def test_zip_5_near_context(self):
        """5-digit ZIP with nearby context word."""
        text = "City, State ZIP 02101"
        findings = scan_text(text)
        zip_findings = [f for f in findings if f.entity_type == "ZIP_CODE"]
        assert len(zip_findings) >= 1
