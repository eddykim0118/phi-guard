"""
.phiguardignore Pattern Matching Tests

.phiguardignore 파일을 통한 파일 무시 기능 테스트
"""

import pytest
from pathlib import Path

from phi_guard.ignore import load_ignore_patterns, should_ignore
from phi_guard.engine import scan_directory


class TestLoadIgnorePatterns:
    """load_ignore_patterns() 함수 테스트"""

    def test_returns_none_when_no_file(self, tmp_path: Path):
        """.phiguardignore 파일이 없으면 None 반환"""
        spec = load_ignore_patterns(tmp_path)
        assert spec is None

    def test_loads_patterns_from_file(self, tmp_path: Path):
        """.phiguardignore 파일이 있으면 PathSpec 반환"""
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("*.log\ntests/\n")

        spec = load_ignore_patterns(tmp_path)
        assert spec is not None

    def test_ignores_comments(self, tmp_path: Path):
        """#으로 시작하는 주석은 무시"""
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("# This is a comment\n*.log\n")

        spec = load_ignore_patterns(tmp_path)
        assert spec is not None
        # 주석은 패턴으로 취급되지 않음
        assert not spec.match_file("# This is a comment")


class TestShouldIgnore:
    """should_ignore() 함수 테스트"""

    def test_returns_false_when_no_spec(self, tmp_path: Path):
        """spec이 None이면 False 반환 (무시하지 않음)"""
        file_path = tmp_path / "test.py"
        result = should_ignore(file_path, tmp_path, None)
        assert result is False

    def test_matches_wildcard_pattern(self, tmp_path: Path):
        """*.log 패턴이 .log 파일과 매칭"""
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("*.log\n")

        spec = load_ignore_patterns(tmp_path)
        log_file = tmp_path / "debug.log"

        assert should_ignore(log_file, tmp_path, spec) is True

    def test_does_not_match_other_extensions(self, tmp_path: Path):
        """*.log 패턴이 .py 파일과 매칭 안 됨"""
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("*.log\n")

        spec = load_ignore_patterns(tmp_path)
        py_file = tmp_path / "main.py"

        assert should_ignore(py_file, tmp_path, spec) is False

    def test_matches_directory_pattern(self, tmp_path: Path):
        """tests/ 패턴이 tests 디렉토리 내 파일과 매칭"""
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("tests/\n")

        spec = load_ignore_patterns(tmp_path)

        # tests 디렉토리 생성
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_main.py"

        assert should_ignore(test_file, tmp_path, spec) is True

    def test_matches_double_star_pattern(self, tmp_path: Path):
        """**/temp/ 패턴이 중첩된 temp 디렉토리와 매칭"""
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("**/temp/\n")

        spec = load_ignore_patterns(tmp_path)

        # 중첩 디렉토리 생성
        nested_temp = tmp_path / "src" / "temp"
        nested_temp.mkdir(parents=True)
        temp_file = nested_temp / "cache.txt"

        assert should_ignore(temp_file, tmp_path, spec) is True


class TestScanDirectoryWithIgnore:
    """scan_directory()에서 .phiguardignore 통합 테스트"""

    def test_ignores_files_matching_pattern(self, tmp_path: Path):
        """패턴에 매칭되는 파일은 스캔에서 제외"""
        # .phiguardignore 생성
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("ignore_me.py\n")

        # PHI가 있는 파일 생성 (무시될 파일)
        ignored_file = tmp_path / "ignore_me.py"
        ignored_file.write_text("SSN: 123-45-6789")

        # PHI가 있는 파일 생성 (스캔될 파일)
        # Note: 987은 9xx라 우리 SSN 패턴에 안 잡힘. 유효한 패턴 사용
        scanned_file = tmp_path / "scan_me.py"
        scanned_file.write_text("SSN: 234-56-7890")

        findings = scan_directory(tmp_path)

        # ignore_me.py의 SSN은 탐지되지 않아야 함
        file_paths = [f.file_path for f in findings]
        assert not any("ignore_me.py" in str(p) for p in file_paths)
        # scan_me.py의 SSN은 탐지되어야 함
        assert any("scan_me.py" in str(p) for p in file_paths)

    def test_no_ignore_file_scans_all(self, tmp_path: Path):
        """.phiguardignore 파일이 없으면 모든 파일 스캔"""
        # PHI가 있는 파일 생성
        py_file = tmp_path / "data.py"
        py_file.write_text("SSN: 123-45-6789")

        findings = scan_directory(tmp_path)

        # 파일이 스캔되어야 함
        assert len(findings) >= 1
        assert any("data.py" in str(f.file_path) for f in findings)

    def test_ignores_directory_pattern(self, tmp_path: Path):
        """디렉토리 패턴으로 전체 디렉토리 제외"""
        # .phiguardignore 생성
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("fixtures/\n")

        # fixtures 디렉토리 생성
        fixtures_dir = tmp_path / "fixtures"
        fixtures_dir.mkdir()
        fixture_file = fixtures_dir / "test_data.py"
        fixture_file.write_text("SSN: 123-45-6789")

        # 다른 파일 생성
        main_file = tmp_path / "main.py"
        main_file.write_text("SSN: 234-56-7890")

        findings = scan_directory(tmp_path)

        # fixtures/ 내 파일은 스캔되지 않아야 함
        file_paths = [str(f.file_path) for f in findings]
        assert not any("fixtures" in p for p in file_paths)
        # main.py는 스캔되어야 함
        assert any("main.py" in p for p in file_paths)

    def test_multiple_patterns(self, tmp_path: Path):
        """여러 패턴이 모두 적용됨"""
        # .phiguardignore 생성
        ignore_file = tmp_path / ".phiguardignore"
        ignore_file.write_text("*.log\ntests/\n")

        # 여러 파일 생성
        log_file = tmp_path / "debug.log"
        log_file.write_text("SSN: 111-22-3333")

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_main.py"
        test_file.write_text("SSN: 444-55-6666")

        main_file = tmp_path / "main.py"
        main_file.write_text("SSN: 777-88-9999")

        findings = scan_directory(tmp_path)

        # main.py만 스캔되어야 함
        file_paths = [str(f.file_path) for f in findings]
        assert len([p for p in file_paths if "main.py" in p]) >= 1
        assert not any("debug.log" in p for p in file_paths)
        assert not any("test_main.py" in p for p in file_paths)
