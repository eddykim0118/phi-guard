"""
SSN Recognizer Tests

SSN 패턴 탐지 테스트:
- True Positives: 유효한 SSN 형식은 탐지되어야 함
- True Negatives: 유효하지 않은 SSN 형식은 탐지되면 안 됨
- Context Boosting: context 단어가 있으면 점수가 높아야 함
- Edge Cases: 여러 SSN, 코드 안 SSN 등
"""

import pytest

from phi_guard.engine import scan_text


class TestSSNTruePositives:
    """유효한 SSN 패턴은 탐지되어야 함"""

    @pytest.mark.parametrize(
        "text,expected_ssn",
        [
            ("123-45-6789", "123-45-6789"),
            ("001-01-0001", "001-01-0001"),
            ("My SSN is 123-45-6789", "123-45-6789"),
            ("SSN: 234-56-7890", "234-56-7890"),
        ],
    )
    def test_valid_ssn_detected(self, text: str, expected_ssn: str):
        """유효한 SSN 형식이 탐지되는지 확인"""
        findings = scan_text(text)

        # Filter for US_SSN specifically (other types like DATE_TIME might also match)
        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) >= 1, f"SSN not detected in: {text}"
        assert ssn_findings[0].text == expected_ssn

    def test_ssn_score_above_threshold(self):
        """SSN 탐지 점수가 threshold 이상인지 확인"""
        findings = scan_text("123-45-6789")

        assert len(findings) == 1
        # 우리 recognizer는 0.85 점수를 줌
        assert findings[0].score >= 0.5


class TestSSNTrueNegatives:
    """유효하지 않은 SSN 패턴은 탐지되면 안 됨"""

    @pytest.mark.parametrize(
        "invalid_ssn,reason",
        [
            ("000-45-6789", "000으로 시작하는 SSN은 유효하지 않음"),
            ("666-45-6789", "666으로 시작하는 SSN은 유효하지 않음"),
            # 9xx (ITIN)은 탐지됨 - 민감 정보이므로 잡는 게 맞음
            ("123-00-6789", "중간 그룹이 00인 SSN은 유효하지 않음"),
            ("123-45-0000", "마지막 그룹이 0000인 SSN은 유효하지 않음"),
        ],
    )
    def test_invalid_ssn_not_detected(self, invalid_ssn: str, reason: str):
        """유효하지 않은 SSN 패턴은 탐지되지 않아야 함"""
        findings = scan_text(invalid_ssn)

        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) == 0, f"Invalid SSN detected: {invalid_ssn}. {reason}"

    @pytest.mark.parametrize(
        "itin",
        [
            "900-45-6789",
            "950-45-6789",
        ],
    )
    def test_itin_is_detected(self, itin: str):
        """ITIN (9xx)도 민감 정보이므로 탐지되어야 함"""
        findings = scan_text(itin)

        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) >= 1, f"ITIN not detected: {itin}"

    @pytest.mark.parametrize(
        "malformed,reason",
        [
            ("12-345-6789", "형식이 맞지 않음 (XX-XXX-XXXX)"),
            ("1234-56-789", "형식이 맞지 않음 (XXXX-XX-XXX)"),
            ("123456789", "하이픈 없는 9자리 숫자"),
            ("123-456-789", "형식이 맞지 않음 (XXX-XXX-XXX)"),
            ("12345-6789", "형식이 맞지 않음 (XXXXX-XXXX)"),
        ],
    )
    def test_malformed_ssn_not_detected(self, malformed: str, reason: str):
        """형식이 맞지 않는 문자열은 SSN으로 탐지되지 않아야 함"""
        findings = scan_text(malformed)

        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) == 0, f"Malformed SSN detected: {malformed}. {reason}"


class TestSSNContextBoosting:
    """Context 단어가 있으면 점수가 높아져야 함"""

    def test_ssn_with_context_has_higher_score(self):
        """'SSN' 같은 context 단어가 있으면 점수가 더 높음"""
        # Context 없음
        findings_no_context = scan_text("random text 123-45-6789 here")
        # Context 있음
        findings_with_context = scan_text("SSN: 123-45-6789")

        assert len(findings_no_context) >= 1
        assert len(findings_with_context) >= 1

        score_no_context = findings_no_context[0].score
        score_with_context = findings_with_context[0].score

        # Context가 있을 때 점수가 같거나 높아야 함
        # (Presidio의 context boosting 동작)
        assert score_with_context >= score_no_context

    @pytest.mark.parametrize(
        "context_text",
        [
            "SSN: 123-45-6789",
            "social security 123-45-6789",
            "Social Security Number: 123-45-6789",
            "ss# 123-45-6789",
        ],
    )
    def test_various_context_words(self, context_text: str):
        """다양한 context 단어가 있을 때 SSN이 탐지됨"""
        findings = scan_text(context_text)

        assert len(findings) >= 1
        assert findings[0].entity_type == "US_SSN"


class TestSSNEdgeCases:
    """Edge cases 테스트"""

    def test_multiple_ssns_in_text(self):
        """텍스트에 여러 SSN이 있을 때 모두 탐지"""
        text = "SSN1: 123-45-6789, SSN2: 234-56-7890, SSN3: 345-67-8901"
        findings = scan_text(text)

        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) == 3

        detected_ssns = {f.text for f in ssn_findings}
        assert detected_ssns == {"123-45-6789", "234-56-7890", "345-67-8901"}

    def test_ssn_in_code_string(self):
        """코드 문자열 안의 SSN 탐지"""
        code = 'patient_ssn = "123-45-6789"'
        findings = scan_text(code)

        assert len(findings) >= 1
        assert findings[0].entity_type == "US_SSN"
        assert findings[0].text == "123-45-6789"

    def test_ssn_in_json(self):
        """JSON 형식 안의 SSN 탐지"""
        json_text = '{"ssn": "123-45-6789", "name": "John"}'
        findings = scan_text(json_text)

        assert len(findings) >= 1
        assert findings[0].entity_type == "US_SSN"

    def test_ssn_in_comment(self):
        """코드 주석 안의 SSN 탐지"""
        code = "# Patient SSN: 123-45-6789"
        findings = scan_text(code)

        assert len(findings) >= 1
        assert findings[0].entity_type == "US_SSN"

    def test_empty_text(self):
        """빈 텍스트 처리"""
        findings = scan_text("")
        assert len(findings) == 0

    def test_no_phi_text(self):
        """PHI가 없는 텍스트"""
        findings = scan_text("Hello, this is a normal text without any PHI.")
        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) == 0


class TestSSNPositionTracking:
    """SSN 위치 추적 테스트"""

    def test_ssn_start_end_position(self):
        """SSN의 시작/끝 위치가 정확한지 확인"""
        text = "My SSN is 123-45-6789 please"
        findings = scan_text(text)

        assert len(findings) >= 1
        finding = findings[0]

        # 위치 확인
        assert text[finding.start : finding.end] == "123-45-6789"

    def test_multiple_ssns_positions(self):
        """여러 SSN의 위치가 각각 정확한지 확인"""
        text = "First: 123-45-6789, Second: 234-56-7890"
        findings = scan_text(text)

        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) == 2

        for finding in ssn_findings:
            # 각 finding의 위치에서 추출한 텍스트가 finding.text와 일치
            assert text[finding.start : finding.end] == finding.text
