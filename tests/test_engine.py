"""PHI Guard Engine Tests."""

import pytest
from pathlib import Path

from phi_guard.engine import scan_text, scan_file, scan_directory, Finding


class TestScanText:
    """Tests for scan_text()."""

    def test_detects_ssn(self):
        findings = scan_text("My SSN is 123-45-6789")
        assert len(findings) == 1
        assert findings[0].entity_type == "US_SSN"
        assert findings[0].text == "123-45-6789"

    def test_no_phi_returns_empty(self):
        findings = scan_text("Hello world, this is clean text.")
        assert len(findings) == 0

    def test_returns_finding_objects(self):
        findings = scan_text("SSN: 123-45-6789")
        assert len(findings) == 1
        finding = findings[0]

        assert isinstance(finding, Finding)
        assert isinstance(finding.entity_type, str)
        assert isinstance(finding.text, str)
        assert isinstance(finding.start, int)
        assert isinstance(finding.end, int)
        assert isinstance(finding.score, float)
        assert finding.file_path is None
        assert finding.line_number is None

    def test_threshold_filtering(self):
        text = "123-45-6789"
        findings_low = scan_text(text, score_threshold=0.1)
        assert len(findings_low) >= 1

        findings_high = scan_text(text, score_threshold=0.99)
        assert len(findings_high) == 0


class TestScanFile:
    """Tests for scan_file()."""

    def test_detects_ssn_in_file(self, file_with_ssn: Path):
        findings = scan_file(file_with_ssn)
        assert len(findings) == 1
        assert findings[0].entity_type == "US_SSN"
        assert findings[0].text == "123-45-6789"

    def test_includes_file_path(self, file_with_ssn: Path):
        findings = scan_file(file_with_ssn)
        assert len(findings) == 1
        assert findings[0].file_path == str(file_with_ssn)

    def test_includes_line_number(self, file_with_ssn: Path):
        findings = scan_file(file_with_ssn)
        assert len(findings) == 1
        assert findings[0].line_number == 1

    def test_correct_line_number_multiline(self, tmp_path: Path):
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
        findings = scan_file(file_without_phi)
        assert len(findings) == 0

    def test_file_not_found_raises(self, tmp_path: Path):
        fake_path = tmp_path / "nonexistent.py"
        with pytest.raises(FileNotFoundError):
            scan_file(fake_path)


class TestScanDirectory:
    """Tests for scan_directory()."""

    def test_scans_all_files(self, dir_with_phi: Path):
        findings = scan_directory(dir_with_phi)
        assert len(findings) >= 2

    def test_recursive_scanning(self, dir_with_phi: Path):
        findings = scan_directory(dir_with_phi, recursive=True)
        file_paths = {f.file_path for f in findings}
        json_files = [p for p in file_paths if p.endswith(".json")]
        assert len(json_files) >= 1

    def test_non_recursive_option(self, dir_with_phi: Path):
        findings = scan_directory(dir_with_phi, recursive=False)
        file_paths = {f.file_path for f in findings}
        subdir_files = [p for p in file_paths if "/data/" in p]
        assert len(subdir_files) == 0

    def test_skips_hidden_directories(self, dir_with_hidden_files: Path):
        findings = scan_directory(dir_with_hidden_files)
        file_paths = {f.file_path for f in findings}
        hidden_files = [p for p in file_paths if "/.git/" in p]
        assert len(hidden_files) == 0
        main_files = [p for p in file_paths if "main.py" in p]
        assert len(main_files) == 1

    def test_skips_unsupported_extensions(self, dir_with_unsupported_files: Path):
        findings = scan_directory(dir_with_unsupported_files)
        file_paths = {f.file_path for f in findings}

        exe_files = [p for p in file_paths if p.endswith(".exe")]
        png_files = [p for p in file_paths if p.endswith(".png")]
        assert len(exe_files) == 0
        assert len(png_files) == 0

        py_files = [p for p in file_paths if p.endswith(".py")]
        assert len(py_files) >= 1

    def test_empty_directory(self, tmp_path: Path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        findings = scan_directory(empty_dir)
        assert len(findings) == 0


class TestFindingDataclass:
    """Tests for Finding dataclass."""

    def test_finding_attributes(self):
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
        finding = Finding(
            entity_type="US_SSN",
            text="123-45-6789",
            start=0,
            end=11,
            score=0.85,
        )
        assert finding.file_path is None
        assert finding.line_number is None
