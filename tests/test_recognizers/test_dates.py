"""
Date/Time Recognizer Tests

Presidio 기본 DATE_TIME recognizer 테스트
HIPAA PHI #3: 날짜 (생년월일, 입원일, 퇴원일, 사망일 등)

Note: 날짜는 코드에서 흔해서 false positive가 많을 수 있음.
나중에 .phiguardignore로 관리 예정.
"""

import pytest

from phi_guard.engine import scan_text


class TestDateTruePositives:
    """유효한 날짜 패턴은 탐지되어야 함"""

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
        """날짜가 탐지되는지 확인"""
        findings = scan_text(text)

        date_findings = [f for f in findings if f.entity_type == "DATE_TIME"]
        assert len(date_findings) >= 1, f"Date not detected in: {text}"


class TestDateInContext:
    """다양한 context에서 날짜 탐지"""

    def test_date_in_json(self):
        """JSON 형식 안의 날짜 탐지"""
        json_text = '{"dob": "1990-01-15", "name": "John"}'
        findings = scan_text(json_text)

        date_findings = [f for f in findings if f.entity_type == "DATE_TIME"]
        assert len(date_findings) >= 1

    def test_date_in_code(self):
        """코드 문자열 안의 날짜 탐지"""
        code = 'birth_date = "January 15, 1990"'
        findings = scan_text(code)

        date_findings = [f for f in findings if f.entity_type == "DATE_TIME"]
        assert len(date_findings) >= 1

    def test_multiple_dates(self):
        """여러 날짜 탐지"""
        text = "Admitted: 2024-01-10, Discharged: 2024-01-15"
        findings = scan_text(text)

        date_findings = [f for f in findings if f.entity_type == "DATE_TIME"]
        assert len(date_findings) >= 2


class TestDateEdgeCases:
    """Edge cases"""

    def test_no_date_in_text(self):
        """날짜가 없는 텍스트"""
        findings = scan_text("Hello, this is a normal text without dates.")
        date_findings = [f for f in findings if f.entity_type == "DATE_TIME"]
        assert len(date_findings) == 0
