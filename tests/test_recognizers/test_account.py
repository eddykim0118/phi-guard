"""Account Number Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestAccountWithContext:
    """Account number detection with context."""

    @pytest.mark.parametrize(
        "text",
        [
            "ACCT-12345678",
            "Account: 12345678901",
            "Account Number 1234567890",
            "Patient account 123456789012",
        ],
    )
    def test_account_with_context_detected(self, text: str):
        """Account numbers with context should be detected."""
        findings = scan_text(text)
        acct_findings = [f for f in findings if f.entity_type == "ACCOUNT_NUMBER"]
        assert len(acct_findings) >= 1, f"Account not detected in: {text}"

    def test_account_prefix_format(self):
        """ACCT- prefix format."""
        findings = scan_text("ACCT-12345678")
        acct_findings = [f for f in findings if f.entity_type == "ACCOUNT_NUMBER"]
        assert len(acct_findings) >= 1


class TestAccountWithoutContext:
    """Account numbers should not be detected without context."""

    @pytest.mark.parametrize(
        "text",
        [
            "12345678901",
            "The number is 123456789012",
        ],
    )
    def test_account_without_context_not_detected(self, text: str):
        """Numbers without context should not be detected as accounts."""
        findings = scan_text(text)
        acct_findings = [f for f in findings if f.entity_type == "ACCOUNT_NUMBER"]
        assert len(acct_findings) == 0, f"False positive account in: {text}"
