"""
IP Address Recognizer Tests

Presidio 기본 IP_ADDRESS recognizer 테스트
HIPAA PHI #15: IP 주소
"""

import pytest

from phi_guard.engine import scan_text


class TestIPTruePositives:
    """유효한 IP 주소는 탐지되어야 함"""

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
        """IP 주소가 탐지되는지 확인"""
        findings = scan_text(text)

        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        assert len(ip_findings) >= 1, f"IP not detected in: {text}"
        assert ip_findings[0].text == expected_ip


class TestIPInContext:
    """다양한 context에서 IP 탐지"""

    def test_ip_in_json(self):
        """JSON 형식 안의 IP 탐지"""
        json_text = '{"client_ip": "192.168.1.100", "port": 8080}'
        findings = scan_text(json_text)

        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        assert len(ip_findings) >= 1
        assert ip_findings[0].text == "192.168.1.100"

    def test_ip_in_code(self):
        """코드 문자열 안의 IP 탐지"""
        code = 'server_ip = "10.0.0.50"'
        findings = scan_text(code)

        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        assert len(ip_findings) >= 1

    def test_multiple_ips(self):
        """여러 IP 탐지"""
        text = "Source: 192.168.1.1, Destination: 192.168.1.2"
        findings = scan_text(text)

        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        assert len(ip_findings) >= 2


class TestIPEdgeCases:
    """Edge cases"""

    def test_no_ip_in_text(self):
        """IP가 없는 텍스트"""
        findings = scan_text("Hello, this is a normal text without IPs.")
        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        assert len(ip_findings) == 0

    def test_version_number_not_ip(self):
        """버전 번호는 IP가 아님"""
        findings = scan_text("Version 1.2.3")
        ip_findings = [f for f in findings if f.entity_type == "IP_ADDRESS"]
        # 버전 번호 형식은 IP가 아니어야 함 (옥텟이 3개뿐)
        assert len(ip_findings) == 0
