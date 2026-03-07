"""
PHI Guard Scan Engine

메인 스캔 로직을 담당합니다.
- scan_text(): 텍스트 문자열에서 PHI 찾기
- scan_file(): 파일에서 PHI 찾기
- scan_directory(): 디렉토리 전체에서 PHI 찾기

사용 예시:
    from phi_guard.engine import scan_text, scan_file

    # 텍스트 스캔
    findings = scan_text("My SSN is 123-45-6789")

    # 파일 스캔
    findings = scan_file(Path("./test.py"))
"""

from dataclasses import dataclass
from pathlib import Path

from phi_guard.ignore import load_ignore_patterns, should_ignore
from phi_guard.recognizers.registry import get_analyzer_engine


# 스캔할 파일 확장자
# 이 확장자들만 스캔함 (바이너리 파일 등은 제외)
SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",  # 코드
    ".json", ".yaml", ".yml", ".toml",     # 설정
    ".env", ".ini", ".cfg",                # 환경설정
    ".csv", ".sql",                        # 데이터
    ".log", ".txt", ".md",                 # 텍스트
    ".xml", ".html",                       # 마크업
}


# 우리가 탐지할 PHI entity 타입들
# spaCy NER의 일반적인 entity (ORGANIZATION, PERSON 등)는 제외
# 새 recognizer 만들 때마다 여기에 추가해야 함
PHI_ENTITY_TYPES = {
    "US_SSN",           # 사회보장번호
    "PHONE_NUMBER",     # 전화번호 (Presidio 기본)
    "EMAIL_ADDRESS",    # 이메일 (Presidio 기본)
    "MRN",              # 의무기록번호 (커스텀)
    "DATE_TIME",        # 날짜/시간 (Presidio 기본) - HIPAA PHI #3
    "IP_ADDRESS",       # IP 주소 (Presidio 기본) - HIPAA PHI #15
}


@dataclass
class Finding:
    """
    PHI 탐지 결과를 나타내는 데이터 클래스

    Attributes:
        entity_type: PHI 종류 (예: "US_SSN", "PERSON", "EMAIL_ADDRESS")
        text: 탐지된 실제 텍스트 (예: "123-45-6789")
        start: 텍스트 내 시작 위치
        end: 텍스트 내 끝 위치
        score: 신뢰도 점수 (0.0 ~ 1.0)
        file_path: 파일 경로 (텍스트 스캔 시 None)
        line_number: 라인 번호 (1부터 시작, 텍스트 스캔 시 None)
    """
    entity_type: str
    text: str
    start: int
    end: int
    score: float
    file_path: str | None = None
    line_number: int | None = None


def scan_text(
    text: str,
    score_threshold: float = 0.5,
) -> list[Finding]:
    """
    텍스트에서 PHI를 찾습니다.

    Args:
        text: 스캔할 텍스트
        score_threshold: 이 점수 이상인 결과만 반환 (기본값 0.5)

    Returns:
        Finding 객체 리스트

    Example:
        >>> findings = scan_text("Call me at 555-123-4567")
        >>> for f in findings:
        ...     print(f"{f.entity_type}: {f.text}")
    """
    analyzer = get_analyzer_engine()

    # Presidio로 분석
    results = analyzer.analyze(
        text=text,
        language="en",
        score_threshold=score_threshold,
    )

    # Presidio 결과를 우리 Finding 객체로 변환
    # PHI_ENTITY_TYPES에 있는 것만 필터링 (spaCy NER 일반 entity 제외)
    findings = []
    for result in results:
        # 우리가 정의한 PHI entity만 포함
        if result.entity_type not in PHI_ENTITY_TYPES:
            continue

        findings.append(Finding(
            entity_type=result.entity_type,
            text=text[result.start:result.end],
            start=result.start,
            end=result.end,
            score=result.score,
        ))

    return findings


def scan_file(
    file_path: Path,
    score_threshold: float = 0.5,
) -> list[Finding]:
    """
    파일에서 PHI를 찾습니다.

    Args:
        file_path: 스캔할 파일 경로
        score_threshold: 이 점수 이상인 결과만 반환

    Returns:
        Finding 객체 리스트 (각각 file_path와 line_number 포함)

    Raises:
        FileNotFoundError: 파일이 없을 때
        UnicodeDecodeError: 바이너리 파일일 때
    """
    file_path = Path(file_path)

    # 파일 읽기
    content = file_path.read_text(encoding="utf-8")

    # 텍스트 스캔
    findings = scan_text(content, score_threshold=score_threshold)

    # 각 finding에 파일 정보 추가
    # 라인 번호 계산: start 위치까지의 줄바꿈 개수 + 1
    for finding in findings:
        finding.file_path = str(file_path)
        finding.line_number = content[:finding.start].count("\n") + 1

    return findings


def scan_directory(
    directory: Path,
    score_threshold: float = 0.5,
    recursive: bool = True,
) -> list[Finding]:
    """
    디렉토리 내 모든 파일에서 PHI를 찾습니다.

    Args:
        directory: 스캔할 디렉토리 경로
        score_threshold: 이 점수 이상인 결과만 반환
        recursive: True면 하위 디렉토리도 스캔

    Returns:
        모든 파일의 Finding 객체 리스트
    """
    directory = Path(directory)
    all_findings: list[Finding] = []

    # .phiguardignore 패턴 로드
    ignore_spec = load_ignore_patterns(directory)

    # 파일 패턴 설정
    pattern = "**/*" if recursive else "*"

    for file_path in directory.glob(pattern):
        # 디렉토리 스킵
        if file_path.is_dir():
            continue

        # 지원하지 않는 확장자 스킵
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        # 숨김 파일/디렉토리 스킵 (.git, .venv 등)
        if any(part.startswith(".") for part in file_path.parts):
            continue

        # .phiguardignore 패턴 체크
        if should_ignore(file_path, directory, ignore_spec):
            continue

        try:
            findings = scan_file(file_path, score_threshold=score_threshold)
            all_findings.extend(findings)
        except UnicodeDecodeError:
            # 바이너리 파일은 조용히 스킵
            continue
        except Exception as e:
            # 다른 에러는 경고만 하고 계속 진행
            print(f"Warning: Could not scan {file_path}: {e}")
            continue

    return all_findings
