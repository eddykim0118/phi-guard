"""Date/Time Recognizer Tests (Presidio default) - HIPAA PHI #3."""

import pytest

from phi_guard.engine import scan_text


class TestDateTruePositives:
    """Valid date patterns should be detected."""

    @pytest.mark.parametrize(
        "text",
        [
            "DOB: 01/15/1990",
            "Date of birth: January 15, 1990",
            "Admission date: 2024-03-15",
            "discharged on 12/25/2023",
            "Patient born on March 5, 1985",
        ],
    )
    def test_date_detected(self, text: str):
        findings = scan_text(text)
        date_findings = [f for f in findings if f.entity_type == "DATE_TIME"]
        assert len(date_findings) >= 1, f"Date not detected in: {text}"


class TestDateInContext:
    """Date detection in various contexts."""

    def test_date_in_json(self):
        json_text = '{"dob": "1990-01-15", "name": "John"}'
        findings = scan_text(json_text)
        date_findings = [f for f in findings if f.entity_type == "DATE_TIME"]
        assert len(date_findings) >= 1

    def test_date_in_code(self):
        code = 'birth_date = "January 15, 1990"'
        findings = scan_text(code)
        date_findings = [f for f in findings if f.entity_type == "DATE_TIME"]
        assert len(date_findings) >= 1

    def test_multiple_dates(self):
        text = "Admitted: 2024-01-10, Discharged: 2024-01-15"
        findings = scan_text(text)
        date_findings = [f for f in findings if f.entity_type == "DATE_TIME"]
        assert len(date_findings) >= 2


class TestDateEdgeCases:
    """Edge cases."""

    def test_no_date_in_text(self):
        findings = scan_text("Hello, this is a normal text without dates.")
        date_findings = [f for f in findings if f.entity_type == "DATE_TIME"]
        assert len(date_findings) == 0
