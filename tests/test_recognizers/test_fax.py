"""Fax Number Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestFaxWithContext:
    """Fax number detection with context."""

    @pytest.mark.parametrize(
        "text",
        [
            "Fax: (555) 123-4567",
            "FAX: 555-123-4567",
            "Fax number 555.123.4567",
            "Facsimile: (555)123-4567",
        ],
    )
    def test_fax_with_context_detected(self, text: str):
        """Fax numbers with context should be detected."""
        findings = scan_text(text)
        fax_findings = [f for f in findings if f.entity_type == "FAX_NUMBER"]
        assert len(fax_findings) >= 1, f"Fax not detected in: {text}"


class TestFaxWithoutContext:
    """Fax numbers should not be detected without explicit fax context."""

    @pytest.mark.parametrize(
        "text",
        [
            "(555) 123-4567",  # Could be phone, not fax
            "555-123-4567",    # Generic phone format
        ],
    )
    def test_fax_without_context_not_detected(self, text: str):
        """Phone-format numbers without fax context should not be detected as fax."""
        findings = scan_text(text)
        fax_findings = [f for f in findings if f.entity_type == "FAX_NUMBER"]
        # These might be detected as PHONE_NUMBER instead, which is correct
        assert len(fax_findings) == 0, f"False positive fax in: {text}"


class TestFaxInMedicalContext:
    """Fax in healthcare documents."""

    def test_fax_in_letterhead(self):
        text = "Phone: (555) 111-2222  Fax: (555) 333-4444"
        findings = scan_text(text)
        fax_findings = [f for f in findings if f.entity_type == "FAX_NUMBER"]
        assert len(fax_findings) >= 1
