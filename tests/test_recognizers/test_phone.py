"""Phone Number Recognizer Tests (Presidio default)."""

import pytest

from phi_guard.engine import scan_text


class TestPhoneTruePositives:
    """Valid phone number patterns should be detected."""

    @pytest.mark.parametrize(
        "text,expected_phone",
        [
            ("Phone: 123-456-7890", "123-456-7890"),
            ("My number is 123.456.7890", "123.456.7890"),
        ],
    )
    def test_us_phone_detected(self, text: str, expected_phone: str):
        findings = scan_text(text)
        phone_findings = [f for f in findings if f.entity_type == "PHONE_NUMBER"]
        assert len(phone_findings) >= 1, f"Phone not detected in: {text}"
        # Compare digits only (Presidio may return different formats)
        detected_digits = "".join(c for c in phone_findings[0].text if c.isdigit())
        expected_digits = "".join(c for c in expected_phone if c.isdigit())
        assert detected_digits == expected_digits


class TestPhoneInContext:
    """Phone detection in various contexts."""

    def test_phone_in_json(self):
        json_text = '{"phone": "555-123-4567", "name": "John"}'
        findings = scan_text(json_text)
        phone_findings = [f for f in findings if f.entity_type == "PHONE_NUMBER"]
        assert len(phone_findings) >= 1

    def test_phone_in_code(self):
        code = 'contact_phone = "555-123-4567"'
        findings = scan_text(code)
        phone_findings = [f for f in findings if f.entity_type == "PHONE_NUMBER"]
        assert len(phone_findings) >= 1


class TestPhoneEdgeCases:
    """Edge cases."""

    def test_no_phone_in_text(self):
        findings = scan_text("Hello, this is a normal text.")
        phone_findings = [f for f in findings if f.entity_type == "PHONE_NUMBER"]
        assert len(phone_findings) == 0
