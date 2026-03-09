"""Medicare/Health Plan ID Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestMBIWithContext:
    """Medicare Beneficiary Identifier (MBI) detection."""

    @pytest.mark.parametrize(
        "text",
        [
            "Medicare: 1EG4TE5MK72",
            "MBI: 1EG4-TE5-MK72",
            "Beneficiary ID 1EG4TE5MK72",
        ],
    )
    def test_mbi_with_context_detected(self, text: str):
        """MBI with context word should be detected."""
        findings = scan_text(text)
        hp_findings = [f for f in findings if f.entity_type == "HEALTH_PLAN_ID"]
        assert len(hp_findings) >= 1, f"MBI not detected in: {text}"

    def test_mbi_format(self):
        findings = scan_text("Medicare ID: 1EG4TE5MK72")
        hp_findings = [f for f in findings if f.entity_type == "HEALTH_PLAN_ID"]
        assert len(hp_findings) >= 1


class TestMedicaidWithContext:
    """Medicaid ID detection."""

    @pytest.mark.parametrize(
        "text",
        [
            "Medicaid: CA12345678",
            "Member ID: NY1234567890",
        ],
    )
    def test_medicaid_with_context_detected(self, text: str):
        """Medicaid ID with context should be detected."""
        findings = scan_text(text)
        hp_findings = [f for f in findings if f.entity_type == "HEALTH_PLAN_ID"]
        assert len(hp_findings) >= 1, f"Medicaid ID not detected in: {text}"


class TestHealthPlanWithoutContext:
    """Health plan IDs should not be detected without context."""

    def test_no_context_not_detected(self):
        findings = scan_text("CA12345678")
        hp_findings = [f for f in findings if f.entity_type == "HEALTH_PLAN_ID"]
        assert len(hp_findings) == 0
