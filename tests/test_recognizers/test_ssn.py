"""SSN Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestSSNTruePositives:
    """Valid SSN patterns should be detected."""

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
        findings = scan_text(text)
        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) >= 1, f"SSN not detected in: {text}"
        assert ssn_findings[0].text == expected_ssn

    def test_ssn_score_above_threshold(self):
        findings = scan_text("123-45-6789")
        assert len(findings) == 1
        assert findings[0].score >= 0.5


class TestSSNTrueNegatives:
    """Invalid SSN patterns should not be detected."""

    @pytest.mark.parametrize(
        "invalid_ssn,reason",
        [
            ("000-45-6789", "000 area number is invalid"),
            ("666-45-6789", "666 area number is invalid"),
            ("123-00-6789", "00 group number is invalid"),
            ("123-45-0000", "0000 serial number is invalid"),
        ],
    )
    def test_invalid_ssn_not_detected(self, invalid_ssn: str, reason: str):
        findings = scan_text(invalid_ssn)
        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) == 0, f"Invalid SSN detected: {invalid_ssn}. {reason}"

    @pytest.mark.parametrize("itin", ["900-45-6789", "950-45-6789"])
    def test_itin_is_detected(self, itin: str):
        """ITINs (9xx) should be detected as sensitive data."""
        findings = scan_text(itin)
        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) >= 1, f"ITIN not detected: {itin}"

    @pytest.mark.parametrize(
        "malformed,reason",
        [
            ("12-345-6789", "Wrong format (XX-XXX-XXXX)"),
            ("1234-56-789", "Wrong format (XXXX-XX-XXX)"),
            ("123456789", "No hyphens"),
            ("123-456-789", "Wrong format (XXX-XXX-XXX)"),
            ("12345-6789", "Wrong format (XXXXX-XXXX)"),
        ],
    )
    def test_malformed_ssn_not_detected(self, malformed: str, reason: str):
        findings = scan_text(malformed)
        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) == 0, f"Malformed SSN detected: {malformed}. {reason}"


class TestSSNContextBoosting:
    """Context words should boost detection confidence."""

    def test_ssn_with_context_has_higher_score(self):
        findings_no_context = scan_text("random text 123-45-6789 here")
        findings_with_context = scan_text("SSN: 123-45-6789")

        assert len(findings_no_context) >= 1
        assert len(findings_with_context) >= 1

        score_no_context = findings_no_context[0].score
        score_with_context = findings_with_context[0].score
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
        findings = scan_text(context_text)
        assert len(findings) >= 1
        assert findings[0].entity_type == "US_SSN"


class TestSSNEdgeCases:
    """Edge cases."""

    def test_multiple_ssns_in_text(self):
        text = "SSN1: 123-45-6789, SSN2: 234-56-7890, SSN3: 345-67-8901"
        findings = scan_text(text)

        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) == 3

        detected_ssns = {f.text for f in ssn_findings}
        assert detected_ssns == {"123-45-6789", "234-56-7890", "345-67-8901"}

    def test_ssn_in_code_string(self):
        code = 'patient_ssn = "123-45-6789"'
        findings = scan_text(code)

        assert len(findings) >= 1
        assert findings[0].entity_type == "US_SSN"
        assert findings[0].text == "123-45-6789"

    def test_ssn_in_json(self):
        json_text = '{"ssn": "123-45-6789", "name": "John"}'
        findings = scan_text(json_text)

        assert len(findings) >= 1
        assert findings[0].entity_type == "US_SSN"

    def test_ssn_in_comment(self):
        code = "# Patient SSN: 123-45-6789"
        findings = scan_text(code)

        assert len(findings) >= 1
        assert findings[0].entity_type == "US_SSN"

    def test_empty_text(self):
        findings = scan_text("")
        assert len(findings) == 0

    def test_no_phi_text(self):
        findings = scan_text("Hello, this is a normal text without any PHI.")
        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) == 0


class TestSSNPositionTracking:
    """Position tracking tests."""

    def test_ssn_start_end_position(self):
        text = "My SSN is 123-45-6789 please"
        findings = scan_text(text)

        assert len(findings) >= 1
        finding = findings[0]
        assert text[finding.start:finding.end] == "123-45-6789"

    def test_multiple_ssns_positions(self):
        text = "First: 123-45-6789, Second: 234-56-7890"
        findings = scan_text(text)

        ssn_findings = [f for f in findings if f.entity_type == "US_SSN"]
        assert len(ssn_findings) == 2

        for finding in ssn_findings:
            assert text[finding.start:finding.end] == finding.text
