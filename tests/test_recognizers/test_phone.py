"""
Phone Number Recognizer Tests

Presidio 기본 PHONE_NUMBER recognizer 테스트
미국 전화번호 형식들을 탐지하는지 확인

Note: Presidio 기본 recognizer는 모든 형식을 완벽하게 잡지 않음.
하이픈/점 형식은 잘 되지만, 괄호/연속숫자는 안 될 수 있음.
"""

import pytest

from phi_guard.engine import scan_text


class TestPhoneTruePositives:
    """유효한 전화번호 패턴은 탐지되어야 함"""

    @pytest.mark.parametrize(
        "text,expected_phone",
        [
            # Presidio는 하이픈/점 형식을 잘 탐지함
            ("Phone: 123-456-7890", "123-456-7890"),
            ("My number is 123.456.7890", "123.456.7890"),
        ],
    )
    def test_us_phone_detected(self, text: str, expected_phone: str):
        """미국 전화번호 형식이 탐지되는지 확인"""
        findings = scan_text(text)

        phone_findings = [f for f in findings if f.entity_type == "PHONE_NUMBER"]
        assert len(phone_findings) >= 1, f"Phone not detected in: {text}"
        # Presidio가 반환하는 형식이 다를 수 있으므로 숫자만 비교
        detected_digits = "".join(c for c in phone_findings[0].text if c.isdigit())
        expected_digits = "".join(c for c in expected_phone if c.isdigit())
        assert detected_digits == expected_digits


class TestPhoneInContext:
    """다양한 context에서 전화번호 탐지"""

    def test_phone_in_json(self):
        """JSON 형식 안의 전화번호 탐지"""
        json_text = '{"phone": "555-123-4567", "name": "John"}'
        findings = scan_text(json_text)

        phone_findings = [f for f in findings if f.entity_type == "PHONE_NUMBER"]
        assert len(phone_findings) >= 1

    def test_phone_in_code(self):
        """코드 문자열 안의 전화번호 탐지"""
        code = 'contact_phone = "555-123-4567"'
        findings = scan_text(code)

        phone_findings = [f for f in findings if f.entity_type == "PHONE_NUMBER"]
        assert len(phone_findings) >= 1


class TestPhoneEdgeCases:
    """Edge cases"""

    def test_no_phone_in_text(self):
        """전화번호가 없는 텍스트"""
        findings = scan_text("Hello, this is a normal text.")
        phone_findings = [f for f in findings if f.entity_type == "PHONE_NUMBER"]
        assert len(phone_findings) == 0
