"""Age Over 89 Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestAgeOver89:
    """Ages over 89 should be detected as PHI."""

    @pytest.mark.parametrize(
        "text,expected_text",
        [
            ("age 90", "age 90"),
            ("age: 95", "age: 95"),
            ("aged 92", "aged 92"),
            ("90 years old", "90 years old"),
            ("95-year-old", "95-year-old"),
            ("91 y/o", "91 y/o"),
            ("100 years old", "100 years old"),
        ],
    )
    def test_age_over_89_detected(self, text: str, expected_text: str):
        """Ages 90+ should be detected."""
        findings = scan_text(text)
        age_findings = [f for f in findings if f.entity_type == "AGE_OVER_89"]
        assert len(age_findings) >= 1, f"Age not detected in: {text}"

    def test_age_102(self):
        findings = scan_text("Patient is 102 years old")
        age_findings = [f for f in findings if f.entity_type == "AGE_OVER_89"]
        assert len(age_findings) >= 1


class TestAgeUnder90:
    """Ages under 90 should NOT be detected."""

    @pytest.mark.parametrize(
        "text",
        [
            "age 89",
            "age: 65",
            "aged 45",
            "89 years old",
            "75-year-old",
            "30 y/o",
        ],
    )
    def test_age_under_90_not_detected(self, text: str):
        """Ages under 90 should not be detected."""
        findings = scan_text(text)
        age_findings = [f for f in findings if f.entity_type == "AGE_OVER_89"]
        assert len(age_findings) == 0, f"False positive age in: {text}"


class TestAgeEdgeCases:
    """Edge cases for age detection."""

    def test_age_in_medical_context(self):
        text = "The patient, age 92, was admitted yesterday."
        findings = scan_text(text)
        age_findings = [f for f in findings if f.entity_type == "AGE_OVER_89"]
        assert len(age_findings) >= 1

    def test_multiple_ages(self):
        text = "Patient 1: 95 years old. Patient 2: 91 y/o."
        findings = scan_text(text)
        age_findings = [f for f in findings if f.entity_type == "AGE_OVER_89"]
        assert len(age_findings) >= 2
