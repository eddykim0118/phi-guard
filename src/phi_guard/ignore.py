"""
PHI Guard Ignore Pattern Handler

.phiguardignore 파일을 읽어서 gitignore 스타일 패턴 매칭을 제공합니다.

사용법:
    .phiguardignore 파일에 다음과 같이 패턴 작성:
        # 테스트 데이터 무시
        tests/fixtures/
        **/test_data/

        # 로그 파일 무시
        *.log
        logs/

왜 이게 필요한가?
- PHI Guard는 "모든 것을 잡는다" 철학을 따름
- 하지만 테스트 데이터나 fixture는 의도적으로 포함된 가짜 PHI
- .phiguardignore로 이런 파일들을 스캔에서 제외할 수 있음
"""

from pathlib import Path

from pathspec import PathSpec


def load_ignore_patterns(directory: Path) -> PathSpec | None:
    """
    디렉토리에서 .phiguardignore 파일을 찾아 PathSpec을 반환합니다.

    Args:
        directory: .phiguardignore를 찾을 디렉토리

    Returns:
        PathSpec 객체 (패턴이 있는 경우) 또는 None (파일이 없는 경우)

    Note:
        - gitwildmatch 패턴을 사용 (gitignore와 동일한 문법)
        - 빈 줄과 #으로 시작하는 주석은 자동으로 무시됨
    """
    ignore_file = directory / ".phiguardignore"

    if not ignore_file.exists():
        return None

    with open(ignore_file, encoding="utf-8") as f:
        # gitignore: .gitignore와 동일한 패턴 매칭
        return PathSpec.from_lines("gitignore", f)


def should_ignore(
    file_path: Path,
    base_dir: Path,
    spec: PathSpec | None,
) -> bool:
    """
    파일이 ignore 패턴에 매칭되는지 확인합니다.

    Args:
        file_path: 체크할 파일의 절대 경로
        base_dir: .phiguardignore가 있는 디렉토리 (상대 경로 계산용)
        spec: load_ignore_patterns()로 로드한 PathSpec

    Returns:
        True면 이 파일을 무시해야 함

    Example:
        >>> spec = load_ignore_patterns(Path("./project"))
        >>> should_ignore(Path("./project/tests/data.py"), Path("./project"), spec)
        True  # tests/ 패턴이 있다면
    """
    if spec is None:
        return False

    # 절대 경로를 base_dir 기준 상대 경로로 변환
    # pathspec은 상대 경로로 매칭함
    relative_path = file_path.relative_to(base_dir)
    return spec.match_file(str(relative_path))
