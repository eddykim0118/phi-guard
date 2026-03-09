"""Account Number Recognizer - HIPAA PHI #12: Account Numbers."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_account_recognizer() -> PatternRecognizer:
    """
    Build account number recognizer for healthcare/financial contexts.

    Healthcare account numbers vary widely:
    - Hospital account numbers (often 8-12 digits)
    - Insurance account/policy numbers
    - Patient account numbers

    These are highly context-dependent to avoid false positives.
    """
    return PatternRecognizer(
        supported_entity="ACCOUNT_NUMBER",
        patterns=[
            Pattern(
                name="Account number (alphanumeric)",
                # Common format: letters + numbers or all numbers
                regex=r"\b[A-Z]{0,3}\d{8,12}\b",
                score=0.2,  # Low score - needs context
            ),
            Pattern(
                name="Account with prefix (ACCT-123456)",
                regex=r"\b(?:ACCT|ACC|ACCOUNT)[-#:\s]*\d{6,12}\b",
                score=0.7,
            ),
        ],
        context=[
            "account", "account number", "account no", "acct",
            "acct#", "account#", "patient account",
            "billing", "invoice", "statement",
            "hospital account", "insurance account",
        ],
    )
