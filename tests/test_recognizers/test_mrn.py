"""
MRN (Medical Record Number) Recognizer Tests

커스텀 MRN recognizer 테스트
- Epic EHR 기준 7-8자리 숫자
- Context 단어가 있을 때만 탐지
"""

import pytest

from phi_guard.engine import scan_text


class TestMRNWithContext:
    """Context 단어가 있을 때 MRN 탐지"""

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
        """Context가 있는 MRN은 탐지되어야 함

        Note: Presidio context boosting은 단어 단위로 작동.
        "Medical Record Number" 같은 멀티 워드는 안 됨.
        """
        findings = scan_text(text)

        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 1, f"MRN not detected in: {text}"

    def test_mrn_7_digits(self):
        """7자리 MRN 탐지"""
        findings = scan_text("MRN: 1234567")

        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 1
        assert mrn_findings[0].text == "1234567"

    def test_mrn_8_digits(self):
        """8자리 MRN 탐지"""
        findings = scan_text("MRN: 12345678")

        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 1
        assert mrn_findings[0].text == "12345678"


class TestMRNWithoutContext:
    """Context 단어가 없을 때 MRN 탐지 안 됨"""

    @pytest.mark.parametrize(
        "text",
        [
            "12345678",              # 숫자만
            "The number is 12345678", # 일반 텍스트
            "ID: 12345678",          # 일반 ID (MRN context 아님)
            "Order #12345678",       # 주문번호
        ],
    )
    def test_mrn_without_context_not_detected(self, text: str):
        """Context 없는 7-8자리 숫자는 MRN으로 탐지되면 안 됨"""
        findings = scan_text(text)

        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) == 0, f"False positive MRN detected in: {text}"


class TestMRNEdgeCases:
    """Edge cases"""

    def test_mrn_in_json(self):
        """JSON 형식 안의 MRN 탐지"""
        json_text = '{"mrn": "12345678", "name": "John"}'
        findings = scan_text(json_text)

        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 1

    def test_mrn_in_code(self):
        """코드 문자열 안의 MRN 탐지"""
        code = 'patient_mrn = "12345678"'
        findings = scan_text(code)

        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 1

    def test_multiple_mrns(self):
        """여러 MRN 탐지"""
        text = "Patient 1 MRN: 12345678, Patient 2 MRN: 87654321"
        findings = scan_text(text)

        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) >= 2

    def test_6_digits_not_mrn(self):
        """6자리 숫자는 MRN이 아님 (너무 짧음)"""
        findings = scan_text("MRN: 123456")

        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) == 0

    def test_9_digits_not_mrn(self):
        """9자리 숫자는 MRN이 아님 (너무 김, SSN일 수 있음)"""
        findings = scan_text("MRN: 123456789")

        mrn_findings = [f for f in findings if f.entity_type == "MRN"]
        assert len(mrn_findings) == 0
