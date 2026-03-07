"""Email Address Recognizer Tests (Presidio default)."""

import pytest

from phi_guard.engine import scan_text


class TestEmailTruePositives:
    """Valid email addresses should be detected."""

    @pytest.mark.parametrize(
        "text,expected_email",
        [
            ("Email me at user@example.com", "user@example.com"),
            ("Contact: john.doe@hospital.org", "john.doe@hospital.org"),
            ("patient_info@healthcare.io", "patient_info@healthcare.io"),
            ("admin@sub.domain.com", "admin@sub.domain.com"),
        ],
    )
    def test_email_detected(self, text: str, expected_email: str):
        findings = scan_text(text)
        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) >= 1, f"Email not detected in: {text}"
        assert email_findings[0].text == expected_email


class TestEmailInContext:
    """Email detection in various contexts."""

    def test_email_in_json(self):
        json_text = '{"email": "patient@hospital.com", "name": "Jane"}'
        findings = scan_text(json_text)
        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) >= 1
        assert email_findings[0].text == "patient@hospital.com"

    def test_email_in_code(self):
        code = 'contact_email = "admin@clinic.org"'
        findings = scan_text(code)
        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) >= 1

    def test_multiple_emails(self):
        text = "CC: alice@example.com, bob@example.com"
        findings = scan_text(text)
        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) >= 2


class TestEmailEdgeCases:
    """Edge cases."""

    def test_no_email_in_text(self):
        findings = scan_text("Hello, this is a normal text without email.")
        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) == 0

    def test_at_sign_not_email(self):
        findings = scan_text("Twitter: @username")
        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) == 0
