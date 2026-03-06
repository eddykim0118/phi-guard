"""
PHI Guard Engine Tests

Engine 함수 테스트:
- scan_text(): 텍스트 스캔
- scan_file(): 파일 스캔
- scan_directory(): 디렉토리 스캔
"""

import pytest
from pathlib import Path

from phi_guard.engine import scan_text, scan_file, scan_directory, Finding


class TestScanText:
    """scan_text() 함수 테스트"""

    def test_detects_ssn(self):
        """SSN이 포함된 텍스트에서 SSN 탐지"""
        findings = scan_text("My SSN is 123-45-6789")

        assert len(findings) == 1
        assert findings[0].entity_type == "US_SSN"
        assert findings[0].text == "123-45-6789"

    def test_no_phi_returns_empty(self):
        """PHI가 없는 텍스트는 빈 리스트 반환"""
        findings = scan_text("Hello world, this is clean text.")

        assert len(findings) == 0

    def test_returns_finding_objects(self):
        """Finding 객체가 올바른 속성을 가지는지 확인"""
        findings = scan_text("SSN: 123-45-6789")

        assert len(findings) == 1
        finding = findings[0]

        assert isinstance(finding, Finding)
        assert isinstance(finding.entity_type, str)
        assert isinstance(finding.text, str)
        assert isinstance(finding.start, int)
        assert isinstance(finding.end, int)
        assert isinstance(finding.score, float)
        # scan_text에서는 file_path와 line_number가 None
        assert finding.file_path is None
        assert finding.line_number is None

    def test_threshold_filtering(self):
        """threshold 설정이 동작하는지 확인"""
        text = "123-45-6789"

        # 낮은 threshold - 탐지됨
        findings_low = scan_text(text, score_threshold=0.1)
        assert len(findings_low) >= 1

        # 아주 높은 threshold - 탐지 안 됨 (score 0.85보다 높음)
        findings_high = scan_text(text, score_threshold=0.99)
        assert len(findings_high) == 0


class TestScanFile:
    """scan_file() 함수 테스트"""

    def test_detects_ssn_in_file(self, file_with_ssn: Path):
        """파일에서 SSN 탐지"""
        findings = scan_file(file_with_ssn)

        assert len(findings) == 1
        assert findings[0].entity_type == "US_SSN"
        assert findings[0].text == "123-45-6789"

    def test_includes_file_path(self, file_with_ssn: Path):
        """Finding에 파일 경로가 포함되는지 확인"""
        findings = scan_file(file_with_ssn)

        assert len(findings) == 1
        assert findings[0].file_path == str(file_with_ssn)

    def test_includes_line_number(self, file_with_ssn: Path):
        """Finding에 라인 번호가 포함되는지 확인"""
        findings = scan_file(file_with_ssn)

        assert len(findings) == 1
        assert findings[0].line_number == 1  # 첫 번째 줄

    def test_correct_line_number_multiline(self, tmp_path: Path):
        """여러 줄 파일에서 라인 번호가 정확한지 확인"""
        file_path = tmp_path / "multiline.py"
        content = """# Line 1
# Line 2
# Line 3
ssn = "123-45-6789"  # Line 4
# Line 5
"""
        file_path.write_text(content)

        findings = scan_file(file_path)

        assert len(findings) == 1
        assert findings[0].line_number == 4

    def test_multiple_ssns_different_lines(self, tmp_path: Path):
        """여러 줄에 SSN이 있을 때 각각의 라인 번호"""
        file_path = tmp_path / "multi_ssn.py"
        content = """ssn1 = "123-45-6789"
ssn2 = "234-56-7890"
ssn3 = "345-67-8901"
"""
        file_path.write_text(content)

        findings = scan_file(file_path)

        assert len(findings) == 3
        line_numbers = {f.line_number for f in findings}
        assert line_numbers == {1, 2, 3}

    def test_clean_file_returns_empty(self, file_without_phi: Path):
        """PHI가 없는 파일은 빈 리스트 반환"""
        findings = scan_file(file_without_phi)

        assert len(findings) == 0

    def test_file_not_found_raises(self, tmp_path: Path):
        """존재하지 않는 파일은 FileNotFoundError"""
        fake_path = tmp_path / "nonexistent.py"

        with pytest.raises(FileNotFoundError):
            scan_file(fake_path)


class TestScanDirectory:
    """scan_directory() 함수 테스트"""

    def test_scans_all_files(self, dir_with_phi: Path):
        """디렉토리 내 모든 파일 스캔"""
        findings = scan_directory(dir_with_phi)

        # config.py와 data/patients.json에서 SSN 탐지
        assert len(findings) >= 2

    def test_recursive_scanning(self, dir_with_phi: Path):
        """하위 디렉토리도 스캔하는지 확인"""
        findings = scan_directory(dir_with_phi, recursive=True)

        # data/patients.json의 SSN도 탐지되어야 함
        file_paths = {f.file_path for f in findings}
        json_files = [p for p in file_paths if p.endswith(".json")]
        assert len(json_files) >= 1

    def test_non_recursive_option(self, dir_with_phi: Path):
        """recursive=False면 하위 디렉토리 스캔 안 함"""
        findings = scan_directory(dir_with_phi, recursive=False)

        # 루트의 config.py만 스캔됨, data/ 하위는 제외
        file_paths = {f.file_path for f in findings}
        subdir_files = [p for p in file_paths if "/data/" in p]
        assert len(subdir_files) == 0

    def test_skips_hidden_directories(self, dir_with_hidden_files: Path):
        """숨김 디렉토리 (.git 등)는 스캔하지 않음"""
        findings = scan_directory(dir_with_hidden_files)

        # .git/config의 SSN은 탐지되지 않아야 함
        file_paths = {f.file_path for f in findings}
        hidden_files = [p for p in file_paths if "/.git/" in p]
        assert len(hidden_files) == 0

        # main.py의 SSN은 탐지되어야 함
        main_files = [p for p in file_paths if "main.py" in p]
        assert len(main_files) == 1

    def test_skips_unsupported_extensions(self, dir_with_unsupported_files: Path):
        """지원하지 않는 확장자 (.exe, .png 등)는 스캔하지 않음"""
        findings = scan_directory(dir_with_unsupported_files)

        # code.py만 스캔됨
        file_paths = {f.file_path for f in findings}

        exe_files = [p for p in file_paths if p.endswith(".exe")]
        png_files = [p for p in file_paths if p.endswith(".png")]

        assert len(exe_files) == 0
        assert len(png_files) == 0

        # .py 파일은 스캔됨
        py_files = [p for p in file_paths if p.endswith(".py")]
        assert len(py_files) >= 1

    def test_empty_directory(self, tmp_path: Path):
        """빈 디렉토리 스캔"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        findings = scan_directory(empty_dir)

        assert len(findings) == 0


class TestFindingDataclass:
    """Finding 데이터 클래스 테스트"""

    def test_finding_attributes(self):
        """Finding 객체 생성 및 속성 확인"""
        finding = Finding(
            entity_type="US_SSN",
            text="123-45-6789",
            start=10,
            end=21,
            score=0.85,
            file_path="/path/to/file.py",
            line_number=5,
        )

        assert finding.entity_type == "US_SSN"
        assert finding.text == "123-45-6789"
        assert finding.start == 10
        assert finding.end == 21
        assert finding.score == 0.85
        assert finding.file_path == "/path/to/file.py"
        assert finding.line_number == 5

    def test_finding_optional_fields(self):
        """Finding의 optional 필드 기본값"""
        finding = Finding(
            entity_type="US_SSN",
            text="123-45-6789",
            start=0,
            end=11,
            score=0.85,
        )

        assert finding.file_path is None
        assert finding.line_number is None
