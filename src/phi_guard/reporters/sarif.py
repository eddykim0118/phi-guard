"""SARIF output format for GitHub Code Scanning."""

import json

from phi_guard.engine import Finding

SARIF_VERSION = "2.1.0"
SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"


def findings_to_sarif(findings: list[Finding]) -> dict:
    """Convert findings to SARIF format."""
    return {
        "$schema": SARIF_SCHEMA,
        "version": SARIF_VERSION,
        "runs": [{
            "tool": {
                "driver": {
                    "name": "PHI Guard",
                    "version": "0.1.0",
                    "informationUri": "https://github.com/eddykim/phi-guard",
                    "rules": _build_rules(findings),
                }
            },
            "results": [_finding_to_result(f) for f in findings],
        }]
    }


def _build_rules(findings: list[Finding]) -> list[dict]:
    """Build unique rules from findings."""
    seen = set()
    rules = []
    for f in findings:
        if f.entity_type not in seen:
            seen.add(f.entity_type)
            rules.append({
                "id": f.entity_type,
                "name": f.entity_type,
                "shortDescription": {"text": f"PHI: {f.entity_type}"},
                "fullDescription": {
                    "text": f"Protected Health Information detected: {f.entity_type}"
                },
                "defaultConfiguration": {"level": "error"},
            })
    return rules


def _finding_to_result(finding: Finding) -> dict:
    """Convert a single finding to SARIF result."""
    return {
        "ruleId": finding.entity_type,
        "level": "error",
        "message": {"text": f"PHI detected: {finding.entity_type}"},
        "locations": [{
            "physicalLocation": {
                "artifactLocation": {
                    "uri": finding.file_path,
                    "uriBaseId": "%SRCROOT%",
                },
                "region": {
                    "startLine": finding.line_number or 1,
                    "startColumn": 1,
                }
            }
        }],
        "partialFingerprints": {
            "primaryLocationLineHash": (
                f"{finding.file_path}:{finding.line_number}:{finding.entity_type}"
            )
        }
    }


def output_sarif(findings: list[Finding]) -> None:
    """Print SARIF JSON to stdout."""
    sarif = findings_to_sarif(findings)
    print(json.dumps(sarif, indent=2))
