"""MRN (Medical Record Number) Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestMRNWithContext:
    """MRN detection with context words."""

    @pytest.mark.parametrize(
        "text",
        [
            "MRN: 12345678",
            "MRN 12345678",
            "mrn 12345678",
            "Chart: 1234567",
            "chart 12345678",
        ],
    )
    def test_mrn_with_context_detected(self, text: str):
        """MRN with context word should be detected.

        Note: Presidio context boosting works on single words only.
        Multi-word phrases like "Medical Record Number" don't work.
        """
        findings = scan_text(text)
        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 1, f"MRN not detected in: {text}"

    def test_mrn_7_digits(self):
        findings = scan_text("MRN: 1234567")
        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 1
        assert mrn_findings[0].text == "1234567"

    def test_mrn_8_digits(self):
        findings = scan_text("MRN: 12345678")
        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 1
        assert mrn_findings[0].text == "12345678"


class TestMRNWithoutContext:
    """MRN should not be detected without context words."""

    @pytest.mark.parametrize(
        "text",
        [
            "12345678",
            "The number is 12345678",
            "ID: 12345678",
            "Order #12345678",
        ],
    )
    def test_mrn_without_context_not_detected(self, text: str):
        findings = scan_text(text)
        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) == 0, f"False positive MRN detected in: {text}"


class TestMRNEdgeCases:
    """Edge cases."""

    def test_mrn_in_json(self):
        json_text = '{"mrn": "12345678", "name": "John"}'
        findings = scan_text(json_text)
        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 1

    def test_mrn_in_code(self):
        code = 'patient_mrn = "12345678"'
        findings = scan_text(code)
        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 1

    def test_multiple_mrns(self):
        text = "Patient 1 MRN: 12345678, Patient 2 MRN: 87654321"
        findings = scan_text(text)
        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 2

    def test_6_digits_not_mrn(self):
        """6 digits is too short for MRN."""
        findings = scan_text("MRN: 123456")
        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) == 0

    def test_9_digits_not_mrn(self):
        """9 digits is too long (could be SSN)."""
        findings = scan_text("MRN: 123456789")
        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) == 0
