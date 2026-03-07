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


def build_ignore_spec(patterns: list[str]) -> PathSpec | None:
    """Build PathSpec from list of pattern strings. Returns None if empty."""
    if not patterns:
        return None
    return PathSpec.from_lines("gitignore", patterns)


def merge_ignore_specs(specs: list[PathSpec | None]) -> PathSpec | None:
    """Merge multiple PathSpecs into one. Returns None if all specs are None."""
    valid_specs = [s for s in specs if s is not None]
    if not valid_specs:
        return None
    all_patterns = []
    for spec in valid_specs:
        all_patterns.extend(spec.patterns)
    return PathSpec(all_patterns)


def should_ignore(file_path: Path, base_dir: Path, spec: PathSpec | None) -> bool:
    """Check if file matches any ignore pattern."""
    if spec is None:
        return False
    relative_path = file_path.relative_to(base_dir)
    return spec.match_file(str(relative_path))
