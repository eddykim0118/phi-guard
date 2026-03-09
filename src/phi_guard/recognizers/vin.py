"""VIN Recognizer - HIPAA PHI #14: Vehicle Identifiers."""

from presidio_analyzer import PatternRecognizer, Pattern


def build_vin_recognizer() -> PatternRecognizer:
    """
    Build VIN (Vehicle Identification Number) recognizer.

    VINs are 17 characters: letters and digits, excluding I, O, Q.
    Low base score requires context words to pass threshold.
    """
    return PatternRecognizer(
        supported_entity="VIN",
        patterns=[
            Pattern(
                name="VIN (17 chars)",
                # VIN: 17 chars, alphanumeric excluding I, O, Q
                regex=r"\b[A-HJ-NPR-Z0-9]{17}\b",
                score=0.3,
            ),
        ],
        context=[
            "vin", "vehicle identification", "vehicle id",
            "VIN", "Vehicle Identification Number",
            "car", "vehicle", "automobile", "truck",
        ],
    )
