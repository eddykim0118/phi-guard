"""
pytest fixtures for PHI Guard tests

pytest의 tmp_path fixture를 활용해서 임시 파일/디렉토리를 생성합니다.
각 테스트가 끝나면 자동으로 정리됩니다.
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_ssn() -> str:
    """유효한 SSN 샘플"""
    return "123-45-6789"


@pytest.fixture
def file_with_ssn(tmp_path: Path, sample_ssn: str) -> Path:
    """SSN이 포함된 임시 파일 생성"""
    file_path = tmp_path / "test_file.py"
    file_path.write_text(f'patient_ssn = "{sample_ssn}"\n')
    return file_path


@pytest.fixture
def file_with_multiple_ssns(tmp_path: Path) -> Path:
    """여러 SSN이 포함된 임시 파일 생성"""
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
    """PHI가 없는 임시 파일 생성"""
    file_path = tmp_path / "clean_file.py"
    file_path.write_text('print("Hello, World!")\n')
    return file_path


@pytest.fixture
def dir_with_phi(tmp_path: Path, sample_ssn: str) -> Path:
    """PHI가 포함된 임시 디렉토리 구조 생성"""
    # 루트에 파일
    (tmp_path / "config.py").write_text(f'SSN = "{sample_ssn}"\n')

    # 서브 디렉토리에 파일
    subdir = tmp_path / "data"
    subdir.mkdir()
    (subdir / "patients.json").write_text(
        '{"patient": {"ssn": "234-56-7890"}}\n'
    )

    # PHI 없는 파일
    (tmp_path / "readme.txt").write_text("This is a readme file.\n")

    return tmp_path


@pytest.fixture
def dir_with_hidden_files(tmp_path: Path, sample_ssn: str) -> Path:
    """숨김 파일/디렉토리가 있는 임시 디렉토리"""
    # 일반 파일
    (tmp_path / "main.py").write_text(f'ssn = "{sample_ssn}"\n')

    # 숨김 디렉토리 (.git 시뮬레이션)
    hidden_dir = tmp_path / ".git"
    hidden_dir.mkdir()
    (hidden_dir / "config").write_text(f'secret_ssn = "{sample_ssn}"\n')

    return tmp_path


@pytest.fixture
def dir_with_unsupported_files(tmp_path: Path, sample_ssn: str) -> Path:
    """지원하지 않는 확장자 파일이 있는 디렉토리"""
    # 지원하는 파일
    (tmp_path / "code.py").write_text(f'ssn = "{sample_ssn}"\n')

    # 지원하지 않는 파일 (바이너리 시뮬레이션)
    (tmp_path / "data.exe").write_text(f'ssn = "{sample_ssn}"\n')
    (tmp_path / "image.png").write_text(f'ssn = "{sample_ssn}"\n')

    return tmp_path
