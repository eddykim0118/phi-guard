"""VIN (Vehicle Identification Number) Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestVINWithContext:
    """VIN detection with context words."""

    @pytest.mark.parametrize(
        "text",
        [
            "VIN: 1HGBH41JXMN109186",
            "Vehicle VIN 1HGBH41JXMN109186",
            "Car: 1HGBH41JXMN109186",
        ],
    )
    def test_vin_with_context_detected(self, text: str):
        """VIN with context word should be detected."""
        findings = scan_text(text)
        vin_findings = [f for f in findings if f.entity_type == "VIN"]
        assert len(vin_findings) >= 1, f"VIN not detected in: {text}"

    def test_vin_17_chars(self):
        findings = scan_text("VIN: 1HGBH41JXMN109186")
        vin_findings = [f for f in findings if f.entity_type == "VIN"]
        assert len(vin_findings) >= 1
        assert vin_findings[0].text == "1HGBH41JXMN109186"


class TestVINWithoutContext:
    """VIN should not be detected without context words."""

    @pytest.mark.parametrize(
        "text",
        [
            "1HGBH41JXMN109186",  # No context
            "The code is 1HGBH41JXMN109186",
        ],
    )
    def test_vin_without_context_not_detected(self, text: str):
        findings = scan_text(text)
        vin_findings = [f for f in findings if f.entity_type == "VIN"]
        assert len(vin_findings) == 0, f"False positive VIN detected in: {text}"


class TestVINInvalidFormats:
    """Invalid VINs should not be detected."""

    @pytest.mark.parametrize(
        "text",
        [
            "VIN: 1HGBH41JXMN10918",  # 16 chars (too short)
            "VIN: 1HGBH41JXMN1091867",  # 18 chars (too long)
            "VIN: 1HGBH41IXMN109186",  # Contains I (not allowed)
            "VIN: 1HGBH41OXMN109186",  # Contains O (not allowed)
            "VIN: 1HGBH41QXMN109186",  # Contains Q (not allowed)
        ],
    )
    def test_invalid_vin_not_detected(self, text: str):
        findings = scan_text(text)
        vin_findings = [f for f in findings if f.entity_type == "VIN"]
        assert len(vin_findings) == 0, f"Invalid VIN detected in: {text}"
