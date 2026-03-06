[🇺🇸 English](./README.md) | [🇰🇷 한국어](./README.ko.md)

# PHI Guard

> CI/CD 파이프라인을 위한 HIPAA PHI 스캐너 — gitleaks의 헬스케어 버전

<!-- Badges (배포 후 활성화) -->
<!-- ![PyPI](https://img.shields.io/pypi/v/phi-guard) -->
<!-- ![Python](https://img.shields.io/pypi/pyversions/phi-guard) -->
<!-- ![License](https://img.shields.io/github/license/eddykim/phi-guard) -->
<!-- ![CI](https://img.shields.io/github/actions/workflow/status/eddykim/phi-guard/ci.yml) -->

## 문제

헬스케어 애플리케이션을 개발하는 개발자들이 실수로 보호대상 건강정보(PHI)를 코드 저장소에 커밋합니다:

```python
# test_patient.py
def test_create_patient():
    patient = Patient(
        name="홍길동",
        ssn="123-45-6789",           # 테스트 픽스처에 실제 SSN
        mrn="MRN-00012345",          # 실제 의무기록번호
        email="patient@email.com"
    )
```

**이것은 HIPAA 위반입니다.** 벌금은 건당 $50,000에서 $1,500,000까지입니다.

GitHub의 Secret Scanning은 API 키와 비밀번호만 잡아냅니다 — **HIPAA의 18가지 PHI 식별자는 전혀 지원하지 않습니다.** PHI Guard가 이 공백을 채웁니다.

## PHI Guard가 하는 일

PHI Guard는 HIPAA에서 정의한 18가지 보호대상 건강정보(PHI)를 코드베이스에서 스캔합니다:

| # | PHI 유형 | 상태 |
|---|----------|--------|
| 1 | 이름 | 예정 |
| 2 | 지리 데이터 | 예정 |
| 3 | 날짜 (생년월일, 입원일 등) | 예정 |
| 4 | 전화번호 | 예정 |
| 5 | 팩스번호 | 예정 |
| 6 | 이메일 주소 | 예정 |
| 7 | **사회보장번호 (SSN)** | **지원** |
| 8 | 의무기록번호 (MRN) | 예정 |
| 9 | 건강보험 수혜자 번호 | 예정 |
| 10 | 계좌번호 | 예정 |
| 11 | 자격증/면허 번호 | 예정 |
| 12 | 차량 식별자 | 예정 |
| 13 | 의료기기 식별자 | 예정 |
| 14 | URL | 예정 |
| 15 | IP 주소 | 예정 |
| 16 | 생체 식별자 | 예정 |
| 17 | 전면 사진 | 범위 외 |
| 18 | 기타 고유 식별자 | 예정 |

## 사용 사례

### Pre-commit Hook (빠른 모드)
PHI가 저장소에 도달하기 전에 차단합니다. 정규식만 사용하는 스캔은 3초 이내에 완료됩니다.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/eddykim/phi-guard
    rev: v0.1.0
    hooks:
      - id: phi-guard
```

### CI/CD 파이프라인 (전체 모드)
NLP 기반 탐지로 모든 Pull Request를 스캔합니다. 정규식으로 잡을 수 없는 이름, 위치 및 기타 비정형 PHI를 잡아냅니다.

```yaml
# .github/workflows/phi-guard.yml
- uses: eddykim/phi-guard-action@v1
  with:
    mode: full
```

## 설치

> 곧 출시 예정 — 아직 PyPI에 배포되지 않음

```bash
pip install phi-guard
```

## 사용법

> 곧 출시 예정 — CLI 개발 중

```bash
# 현재 디렉토리 스캔
phi-guard scan ./

# 특정 파일 스캔
phi-guard scan ./tests/fixtures/sample.py

# SARIF 형식으로 출력 (GitHub Security 탭용)
phi-guard scan ./ --format sarif
```

## 작동 원리

PHI Guard는 PII 탐지를 위해 [Microsoft Presidio](https://github.com/microsoft/presidio)를 사용하며, 다음과 같이 향상되었습니다:

- **커스텀 인식기** — 헬스케어 특화 패턴 (MRN, 보험 ID)
- **강화된 SSN 탐지** — Presidio 기본값에는 유효한 SSN을 필터링하는 버그가 있음
- **듀얼 모드 아키텍처** — pre-commit용 빠른 정규식, CI/CD용 전체 NLP
- **SARIF 출력** — GitHub Security 탭과 통합

### 아키텍처

```
┌─────────────────────────────────────────────────┐
│                   PHI Guard                      │
├─────────────────────────────────────────────────┤
│  CLI (Typer)                                    │
│    └── phi-guard scan <path>                    │
├─────────────────────────────────────────────────┤
│  Engine                                          │
│    └── scan_text() / scan_file() / scan_dir()   │
├─────────────────────────────────────────────────┤
│  Recognizers                                     │
│    ├── SSN Recognizer (정규식, 점수 0.85)        │
│    ├── MRN Recognizer (예정)                    │
│    ├── Phone Recognizer (예정)                  │
│    └── ... 18가지 HIPAA 식별자                  │
├─────────────────────────────────────────────────┤
│  Presidio AnalyzerEngine                         │
│    ├── RecognizerRegistry                       │
│    └── SpacyNlpEngine (en_core_web_sm)          │
└─────────────────────────────────────────────────┘
```

## Presidio를 직접 사용하면 안 되나요?

사용해도 됩니다! 하지만 PHI Guard는 다음을 제공합니다:

1. **헬스케어 집중** — 일반 PII가 아닌 HIPAA PHI만
2. **CI/CD 통합** — Pre-commit hooks, GitHub Actions, SARIF 출력
3. **Presidio 버그 수정** — 기본 SSN 인식기의 점수가 0.05 (탐지하기에 너무 낮음)
4. **증분 스캔** — PR에서 변경된 파일만 스캔

## 개발

```bash
# 클론 및 설정
git clone https://github.com/eddykim/phi-guard.git
cd phi-guard
poetry install

# spaCy 모델 다운로드
poetry run python -m spacy download en_core_web_sm

# 테스트 실행
poetry run pytest

# CLI 실행
poetry run phi-guard scan ./
```

## 라이선스

Apache 2.0

## 기여

기여를 환영합니다! 가이드라인은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

---

Microsoft [Presidio](https://github.com/microsoft/presidio)와 [spaCy](https://spacy.io/)로 제작되었습니다.
