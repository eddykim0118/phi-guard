"""pytest fixtures for PHI Guard tests."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_ssn() -> str:
    return "123-45-6789"


@pytest.fixture
def file_with_ssn(tmp_path: Path, sample_ssn: str) -> Path:
    file_path = tmp_path / "test_file.py"
    file_path.write_text(f'patient_ssn = "{sample_ssn}"\n')
    return file_path


@pytest.fixture
def file_with_multiple_ssns(tmp_path: Path) -> Path:
    file_path = tmp_path / "patients.py"
    content = '''
# Patient records
patients = [
    {"name": "John", "ssn": "123-45-6789"},
    {"name": "Jane", "ssn": "234-56-7890"},
    {"name": "Bob", "ssn": "345-67-8901"},
]
'''
    file_path.write_text(content)
    return file_path


@pytest.fixture
def file_without_phi(tmp_path: Path) -> Path:
    file_path = tmp_path / "clean_file.py"
    file_path.write_text('print("Hello, World!")\n')
    return file_path


@pytest.fixture
def dir_with_phi(tmp_path: Path, sample_ssn: str) -> Path:
    (tmp_path / "config.py").write_text(f'SSN = "{sample_ssn}"\n')

    subdir = tmp_path / "data"
    subdir.mkdir()
    (subdir / "patients.json").write_text('{"patient": {"ssn": "234-56-7890"}}\n')

    (tmp_path / "readme.txt").write_text("This is a readme file.\n")
    return tmp_path


@pytest.fixture
def dir_with_hidden_files(tmp_path: Path, sample_ssn: str) -> Path:
    (tmp_path / "main.py").write_text(f'ssn = "{sample_ssn}"\n')

    hidden_dir = tmp_path / ".git"
    hidden_dir.mkdir()
    (hidden_dir / "config").write_text(f'secret_ssn = "{sample_ssn}"\n')
    return tmp_path


@pytest.fixture
def dir_with_unsupported_files(tmp_path: Path, sample_ssn: str) -> Path:
    (tmp_path / "code.py").write_text(f'ssn = "{sample_ssn}"\n')
    (tmp_path / "data.exe").write_text(f'ssn = "{sample_ssn}"\n')
    (tmp_path / "image.png").write_text(f'ssn = "{sample_ssn}"\n')
    return tmp_path
