#!/usr/bin/env python3
"""Structural QA for rendered, passive Twinthos security-audit HTML."""
import argparse
import html as html_lib
import json
import re
import sys
from pathlib import Path

CORE_IDS = tuple(p + "-" + str(i).zfill(2)
                 for p in ("IAM", "AGT", "SEC", "DEP", "GOV", "INT", "MON", "SRC")
                 for i in range(1, 4))
OPTIONAL_IDS = ("AGT-04", "SRC-04", "SEC-04", "OPS-04")
ALL_IDS = CORE_IDS + OPTIONAL_IDS
STATUSES = {"satisfactory", "action_recommended", "needs_confirmation",
            "not_reviewed", "not_applicable"}


def _plain(fragment: str) -> str:
    return html_lib.unescape(re.sub(r"<[^>]*>", "", fragment)).strip()


def _heading_matches(source: str, level: int):
    return list(re.finditer(r"<h" + str(level) + r"\b[^>]*>(.*?)</h" +
                           str(level) + r">", source, flags=re.IGNORECASE | re.DOTALL))


def _appendix(source: str):
    heads = _heading_matches(source, 3)
    outcomes = {}
    duplicates = []
    for i, match in enumerate(heads):
        heading = _plain(match.group(1))
        found = re.match(r"^([A-Z]{3}-\d{2})(?:\b|\s*-)", heading)
        if not found:
            continue
        tid = found.group(1)
        if tid in outcomes:
            duplicates.append(tid)
        until = heads[i + 1].start() if i + 1 < len(heads) else len(source)
        body = _plain(source[match.end():until])
        status_match = re.search(r"\bStatus:\s*([a-z_]+)\b", body, re.IGNORECASE)
        outcomes[tid] = status_match.group(1).lower() if status_match else None
    return outcomes, duplicates


def check_heading_structure(source: str) -> list:
    headers = [_plain(m.group(1)).lower() for m in _heading_matches(source, 2)]
    missing = [name for name in ("status at a glance", "review summary", "appendix: check outcomes")
               if name not in headers]
    return ["Missing second-level heading: " + name for name in missing]


def check_check_count(source: str) -> list:
    outcomes, duplicates = _appendix(source)
    errors = ["Duplicated appendix ID: " + name for name in sorted(set(duplicates))]
    for tid in ALL_IDS:
        if tid not in outcomes:
            errors.append("Missing required/optional check outcome: " + tid)
    for tid in outcomes:
        if tid not in ALL_IDS:
            errors.append("Unrecognized check ID: " + tid)
        elif outcomes[tid] not in STATUSES:
            errors.append("Missing or invalid status in appendix: " + tid)
    return errors


def _matrix(source: str):
    rows = {}
    errors = []
    for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", source, re.I | re.S):
        cells = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, re.I | re.S)
        if len(cells) < 4:
            continue
        tid = _plain(cells[0])
        if tid not in ALL_IDS:
            continue
        if tid in rows:
            errors.append("Repeated matrix check ID: " + tid)
        rows[tid] = _plain(cells[-1]).lower()
    return rows, errors


def check_status_matrix_parity(source: str) -> list:
    outcomes, _ = _appendix(source)
    rows, errors = _matrix(source)
    for tid in ALL_IDS:
        if tid not in rows:
            errors.append("Missing matrix row: " + tid)
        elif tid in outcomes and rows[tid] != outcomes[tid]:
            errors.append("Matrix/appendix status mismatch: " + tid)
    return errors


def check_passive_html(source: str) -> list:
    errors = []
    if re.search(r"<\s*(?:script|iframe|object|embed|form)\b", source, re.I):
        errors.append("Active HTML element in report")
    if re.search(r"\bon[a-z]{3,}\s*=", source, re.I):
        errors.append("Inline event handler present")
    if re.search(r"\b(?:src|href|action)\s*=\s*[\"']\s*(?:https?:|data:|javascript:|//)",
                 source, re.I):
        errors.append("External or executable resource URL in report")
    if re.search(r"@import\b|url\s*\(", source, re.I):
        errors.append("CSS resource import in report")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate rendered AI security report HTML")
    parser.add_argument("html", type=Path)
    parser.add_argument("--expected-summary", type=Path)
    args = parser.parse_args()
    try:
        source = args.html.read_text(encoding="utf-8")
        errors = (check_heading_structure(source) + check_check_count(source) +
                  check_status_matrix_parity(source) + check_passive_html(source))
        if args.expected_summary:
            expected = json.loads(args.expected_summary.read_text(encoding="utf-8"))
            if not isinstance(expected, dict):
                errors.append("Expected summary must be an object")
            else:
                if expected.get("core_total", len(CORE_IDS)) != len(CORE_IDS):
                    errors.append("Expected core total differs from canonical checklist")
                if expected.get("optional_total", len(OPTIONAL_IDS)) != len(OPTIONAL_IDS):
                    errors.append("Expected optional total differs from canonical checklist")
    except (OSError, ValueError, json.JSONDecodeError):
        print("QA FAILED: unreadable or invalid report input", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print("QA FAILED:", error)
        return 1
    print("QA PASSED: 24 core + 4 optional checks; matrix/appendix parity; passive HTML")
    return 0


if __name__ == "__main__":
    sys.exit(main())
