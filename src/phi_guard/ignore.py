"""PHI Guard Ignore Pattern Handler - .phiguardignore support."""

from pathlib import Path

from pathspec import PathSpec


def load_ignore_patterns(directory: Path) -> PathSpec | None:
    """Load .phiguardignore patterns from directory. Returns None if file doesn't exist."""
    ignore_file = directory / ".phiguardignore"
    if not ignore_file.exists():
        return None

    with open(ignore_file, encoding="utf-8") as f:
        return PathSpec.from_lines("gitignore", f)


def should_ignore(file_path: Path, base_dir: Path, spec: PathSpec | None) -> bool:
    """Check if file matches any ignore pattern."""
    if spec is None:
        return False
    relative_path = file_path.relative_to(base_dir)
    return spec.match_file(str(relative_path))
