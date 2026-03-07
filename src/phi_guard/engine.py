"""PHI Guard Scan Engine - Core scanning functions."""

from dataclasses import dataclass
from pathlib import Path

from phi_guard.ignore import load_ignore_patterns, should_ignore
from phi_guard.recognizers.registry import get_analyzer_engine


SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".json", ".yaml", ".yml", ".toml",
    ".env", ".ini", ".cfg",
    ".csv", ".sql",
    ".log", ".txt", ".md",
    ".xml", ".html",
}

# PHI entity types to detect (excludes generic spaCy NER entities)
PHI_ENTITY_TYPES = {
    "US_SSN",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "MRN",
    "DATE_TIME",
    "IP_ADDRESS",
}


@dataclass
class Finding:
    """A detected PHI instance."""
    entity_type: str
    text: str
    start: int
    end: int
    score: float
    file_path: str | None = None
    line_number: int | None = None


def scan_text(text: str, score_threshold: float = 0.5) -> list[Finding]:
    """Scan text for PHI and return findings above the score threshold."""
    analyzer = get_analyzer_engine()
    results = analyzer.analyze(text=text, language="en", score_threshold=score_threshold)

    findings = []
    for result in results:
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


def scan_file(file_path: Path, score_threshold: float = 0.5) -> list[Finding]:
    """Scan a file for PHI. Returns findings with file_path and line_number."""
    file_path = Path(file_path)
    content = file_path.read_text(encoding="utf-8")
    findings = scan_text(content, score_threshold=score_threshold)

    for finding in findings:
        finding.file_path = str(file_path)
        finding.line_number = content[:finding.start].count("\n") + 1

    return findings


def scan_directory(
    directory: Path,
    score_threshold: float = 0.5,
    recursive: bool = True,
) -> list[Finding]:
    """Scan all files in a directory for PHI."""
    directory = Path(directory)
    all_findings: list[Finding] = []
    ignore_spec = load_ignore_patterns(directory)
    pattern = "**/*" if recursive else "*"

    for file_path in directory.glob(pattern):
        if file_path.is_dir():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if any(part.startswith(".") for part in file_path.parts):
            continue
        if should_ignore(file_path, directory, ignore_spec):
            continue

        try:
            findings = scan_file(file_path, score_threshold=score_threshold)
            all_findings.extend(findings)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Warning: Could not scan {file_path}: {e}")
            continue

    return all_findings
