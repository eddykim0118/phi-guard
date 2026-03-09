"""Device Identifier Recognizer - HIPAA PHI #15: Device Identifiers."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_device_recognizer() -> PatternRecognizer:
    """
    Build medical device identifier recognizer.

    FDA UDI (Unique Device Identifier) format:
    - Device Identifier (DI): identifies device labeler and specific version
    - Production Identifier (PI): lot/batch, serial, expiration, manufacturing date

    Common formats:
    - UDI-DI: (01)00884838000025
    - Serial numbers: alphanumeric, usually 8-20 chars

    Also catches common medical device serial patterns.
    """
    return PatternRecognizer(
        supported_entity="DEVICE_ID",
        patterns=[
            Pattern(
                name="UDI (GS1 format)",
                # GS1 format: (01) followed by 14 digits
                regex=r"\(01\)\d{14}",
                score=0.85,
            ),
            Pattern(
                name="Device serial (alphanumeric)",
                regex=r"\b(?:SN|S/N|Serial)[-:\s]*[A-Z0-9]{8,20}\b",
                score=0.6,
            ),
        ],
        context=[
            "device", "serial", "serial number", "sn", "s/n",
            "udi", "UDI", "implant", "pacemaker", "pump",
            "medical device", "equipment", "model",
            "lot", "batch", "manufacturer",
        ],
    )
