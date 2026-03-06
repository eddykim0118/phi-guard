"""
Email Address Recognizer Tests

Presidio 기본 EMAIL_ADDRESS recognizer 테스트
이메일 주소 형식들을 탐지하는지 확인
"""

import pytest

from phi_guard.engine import scan_text


class TestEmailTruePositives:
    """유효한 이메일 주소는 탐지되어야 함"""

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
        """이메일 주소가 탐지되는지 확인"""
        findings = scan_text(text)

        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) >= 1, f"Email not detected in: {text}"
        assert email_findings[0].text == expected_email


class TestEmailInContext:
    """다양한 context에서 이메일 탐지"""

    def test_email_in_json(self):
        """JSON 형식 안의 이메일 탐지"""
        json_text = '{"email": "patient@hospital.com", "name": "Jane"}'
        findings = scan_text(json_text)

        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) >= 1
        assert email_findings[0].text == "patient@hospital.com"

    def test_email_in_code(self):
        """코드 문자열 안의 이메일 탐지"""
        code = 'contact_email = "admin@clinic.org"'
        findings = scan_text(code)

        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) >= 1

    def test_multiple_emails(self):
        """여러 이메일 탐지"""
        text = "CC: alice@example.com, bob@example.com"
        findings = scan_text(text)

        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) >= 2


class TestEmailEdgeCases:
    """Edge cases"""

    def test_no_email_in_text(self):
        """이메일이 없는 텍스트"""
        findings = scan_text("Hello, this is a normal text without email.")
        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) == 0

    def test_at_sign_not_email(self):
        """@가 있지만 이메일이 아닌 경우"""
        findings = scan_text("Twitter: @username")
        email_findings = [f for f in findings if f.entity_type == "EMAIL_ADDRESS"]
        assert len(email_findings) == 0
