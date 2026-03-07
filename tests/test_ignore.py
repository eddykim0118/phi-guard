"""Tests for .phiguardignore pattern matching."""

import pytest
from pathlib import Path

from phi_guard.ignore import load_ignore_patterns, should_ignore
from phi_guard.engine import scan_directory


class TestLoadIgnorePatterns:
    """Tests for load_ignore_patterns()."""

    def test_returns_none_when_no_file(self, tmp_path: Path):
        spec = load_ignore_patterns(tmp_path)
        assert spec is None

    def test_loads_patterns_from_file(self, tmp_path: Path):
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("*.log\ntests/\n")

        spec = load_ignore_patterns(tmp_path)
        assert spec is not None

    def test_ignores_comments(self, tmp_path: Path):
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("# This is a comment\n*.log\n")

        spec = load_ignore_patterns(tmp_path)
        assert spec is not None
        assert not spec.match_file("# This is a comment")


class TestShouldIgnore:
    """Tests for should_ignore()."""

    def test_returns_false_when_no_spec(self, tmp_path: Path):
        file_path = tmp_path / "test.py"
        result = should_ignore(file_path, tmp_path, None)
        assert result is False

    def test_matches_wildcard_pattern(self, tmp_path: Path):
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("*.log\n")

        spec = load_ignore_patterns(tmp_path)
        log_file = tmp_path / "debug.log"

        assert should_ignore(log_file, tmp_path, spec) is True

    def test_does_not_match_other_extensions(self, tmp_path: Path):
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("*.log\n")

        spec = load_ignore_patterns(tmp_path)
        py_file = tmp_path / "main.py"

        assert should_ignore(py_file, tmp_path, spec) is False

    def test_matches_directory_pattern(self, tmp_path: Path):
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("tests/\n")

        spec = load_ignore_patterns(tmp_path)

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_main.py"

        assert should_ignore(test_file, tmp_path, spec) is True

    def test_matches_double_star_pattern(self, tmp_path: Path):
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("**/temp/\n")

        spec = load_ignore_patterns(tmp_path)

        nested_temp = tmp_path / "src" / "temp"
        nested_temp.mkdir(parents=True)
        temp_file = nested_temp / "cache.txt"

        assert should_ignore(temp_file, tmp_path, spec) is True


class TestScanDirectoryWithIgnore:
    """Integration tests for scan_directory() with .phiguardignore."""

    def test_ignores_files_matching_pattern(self, tmp_path: Path):
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("ignore_me.py\n")

        ignored_file = tmp_path / "ignore_me.py"
        ignored_file.write_text("SSN: 123-45-6789")

        scanned_file = tmp_path / "scan_me.py"
        scanned_file.write_text("SSN: 234-56-7890")

        findings = scan_directory(tmp_path)

        file_paths = [f.file_path for f in findings]
        assert not any("ignore_me.py" in str(p) for p in file_paths)
        assert any("scan_me.py" in str(p) for p in file_paths)

    def test_no_ignore_file_scans_all(self, tmp_path: Path):
        py_file = tmp_path / "data.py"
        py_file.write_text("SSN: 123-45-6789")

        findings = scan_directory(tmp_path)

        assert len(findings) >= 1
        assert any("data.py" in str(f.file_path) for f in findings)

    def test_ignores_directory_pattern(self, tmp_path: Path):
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("fixtures/\n")

        fixtures_dir = tmp_path / "fixtures"
        fixtures_dir.mkdir()
        fixture_file = fixtures_dir / "test_data.py"
        fixture_file.write_text("SSN: 123-45-6789")

        main_file = tmp_path / "main.py"
        main_file.write_text("SSN: 234-56-7890")

        findings = scan_directory(tmp_path)

        file_paths = [str(f.file_path) for f in findings]
        assert not any("fixtures" in p for p in file_paths)
        assert any("main.py" in p for p in file_paths)

    def test_multiple_patterns(self, tmp_path: Path):
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("*.log\ntests/\n")

        log_file = tmp_path / "debug.log"
        log_file.write_text("SSN: 111-22-3333")

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_main.py"
        test_file.write_text("SSN: 444-55-6666")

        main_file = tmp_path / "main.py"
        main_file.write_text("SSN: 777-88-9999")

        findings = scan_directory(tmp_path)

        file_paths = [str(f.file_path) for f in findings]
        assert len([p for p in file_paths if "main.py" in p]) >= 1
        assert not any("debug.log" in p for p in file_paths)
        assert not any("test_main.py" in p for p in file_paths)
