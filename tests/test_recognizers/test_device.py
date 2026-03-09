"""Device Identifier Recognizer Tests."""

import pytest

from phi_guard.engine import scan_text


class TestUDI:
    """Unique Device Identifier (UDI) detection."""

    def test_udi_gs1_format(self):
        """GS1 UDI format should be detected."""
        text = "UDI: (01)00884838000025"
        findings = scan_text(text)
        device_findings = [f for f in findings if f.entity_type == "DEVICE_ID"]
        assert len(device_findings) >= 1, f"UDI not detected in: {text}"


class TestDeviceSerial:
    """Device serial number detection."""

    @pytest.mark.parametrize(
        "text",
        [
            "Serial: ABC12345678",
            "S/N: XYZ987654321",
            "SN ABC12345DEF",
            "Device serial A1B2C3D4E5F6",
        ],
    )
    def test_serial_with_context_detected(self, text: str):
        """Serial numbers with context should be detected."""
        findings = scan_text(text)
        device_findings = [f for f in findings if f.entity_type == "DEVICE_ID"]
        assert len(device_findings) >= 1, f"Serial not detected in: {text}"


class TestDeviceWithoutContext:
    """Device IDs should not be detected without context."""

    def test_alphanumeric_without_context_not_detected(self):
        """Random alphanumeric strings should not be detected."""
        findings = scan_text("ABC12345678XYZ")
        device_findings = [f for f in findings if f.entity_type == "DEVICE_ID"]
        assert len(device_findings) == 0
