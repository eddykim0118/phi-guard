"""IP Address Recognizer Tests (Presidio default) - HIPAA PHI #15."""

import pytest

from phi_guard.engine import scan_text


class TestIPTruePositives:
    """Valid IP addresses should be detected."""

    @pytest.mark.parametrize(
        "text,expected_ip",
        [
            ("IP: 192.168.1.1", "192.168.1.1"),
            ("Server at 10.0.0.1", "10.0.0.1"),
            ("Client IP: 172.16.0.100", "172.16.0.100"),
            ("Localhost: 127.0.0.1", "127.0.0.1"),
            ("Public IP 8.8.8.8", "8.8.8.8"),
        ],
    )
    def test_ip_detected(self, text: str, expected_ip: str):
        findings = scan_text(text)
        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        assert len(ip_findings) >= 1, f"IP not detected in: {text}"
        assert ip_findings[0].text == expected_ip


class TestIPInContext:
    """IP detection in various contexts."""

    def test_ip_in_json(self):
        json_text = '{"client_ip": "192.168.1.100", "port": 8080}'
        findings = scan_text(json_text)
        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        assert len(ip_findings) >= 1
        assert ip_findings[0].text == "192.168.1.100"

    def test_ip_in_code(self):
        code = 'server_ip = "10.0.0.50"'
        findings = scan_text(code)
        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        assert len(ip_findings) >= 1

    def test_multiple_ips(self):
        text = "Source: 192.168.1.1, Destination: 192.168.1.2"
        findings = scan_text(text)
        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        assert len(ip_findings) >= 2


class TestIPEdgeCases:
    """Edge cases."""

    def test_no_ip_in_text(self):
        findings = scan_text("Hello, this is a normal text without IPs.")
        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        assert len(ip_findings) == 0

    def test_version_number_not_ip(self):
        """Version numbers (3 octets) should not be detected as IP."""
        findings = scan_text("Version 1.2.3")
        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        assert len(ip_findings) == 0
