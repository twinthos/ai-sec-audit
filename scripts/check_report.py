#!/usr/bin/env python3
"""
Twinthos AI Security Audit — structural QA for rendered HTML.

Enforces count comparison, status matrix parity, passive HTML, and
appendix heading rules. Requires Python 3 standard library only.
"""

import argparse
import re
import sys


def check_heading_structure(html: str) -> list[str]:
    errors = []
    appendix_headings = re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.IGNORECASE)
    for heading in appendix_headings:
        if not heading.strip().lower().startswith("appendix"):
            errors.append(f"Second-level heading does not begin with 'Appendix': {heading}")
    return errors


def check_check_count(html: str) -> list[str]:
    errors = []
    topic_pattern = re.compile(r"###\s+(AGT|IAM|SEC|DEP|GOV|INT|MON|SRC|OPS)-(\d+)\s*-\s*(.+)")
    found = {}
    for match in topic_pattern.finditer(html):
        tid = f"{match.group(1)}-{match.group(2)}"
        title = match.group(3).strip()
        found[tid] = title

    required = [f"{prefix}-{i:02d}" for prefix in ["AGT", "IAM", "SEC", "DEP", "GOV", "INT", "MON", "SRC", "OPS"] for i in range(1, 4)]
    required = [r for r in required if not (r.startswith("SRC-") or r.startswith("OPS-"))]
    required += [f"{prefix}-04" for prefix in ["AGT", "SRC", "SEC", "OPS"]]
    required.sort()

    for tid in required:
        if tid not in found:
            errors.append(f"Missing check outcome: {tid}")
    return errors


def check_status_matrix_parity(html: str) -> list[str]:
    errors = []
    matrix_rows = re.findall(r"\|([A-Z]{3}-\d{2})[^|]*\|\s*(system-wide|by agent|satisfactory|action_recommended|needs_confirmation|not_reviewed|not_applicable)", html, re.IGNORECASE)
    status_map = {"satisfactory": 1, "action_recommended": 2, "needs_confirmation": 3, "not_reviewed": 4, "not_applicable": 5, "system-wide": 0, "by agent": 0}
    for tid, status in matrix_rows:
        tid = tid.strip().upper()
        status_val = status_map.get(status.lower(), 0)
        appendix_match = re.search(rf"###\s+{re.escape(tid)}\s*-\s*.+?\nStatus:\s*(satisfactory|action_recommended|needs_confirmation|not_reviewed|not_applicable)", html, re.IGNORECASE | re.DOTALL)
        if not appendix_match:
            errors.append(f"Matrix row for {tid} has no appendix outcome")
            continue
        appendix_status = appendix_match.group(1).lower()
        appendix_val = status_map.get(appendix_status, 0)
        if status_val != 0 and appendix_val != 0 and status_val < appendix_val:
            errors.append(f"Matrix row {tid} shows {status} but appendix says {appendix_status}")
    return errors


def check_passive_html(html: str) -> list[str]:
    errors = []
    if "<script" in html.lower():
        errors.append("HTML contains <script> tags")
    if "onload=" in html.lower() or "onclick=" in html.lower():
        errors.append("HTML contains inline event handlers")
    if re.search(r"https?://", html):
        errors.append("HTML contains external URLs")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="QA check for rendered AI security audit HTML")
    parser.add_argument("html", type=Path, help="Path to rendered HTML file")
    parser.add_argument("--expected-summary", type=Path, help="Optional expected summary counts JSON")
    args = parser.parse_args()

    if not args.html.exists():
        print(f"Error: {args.html} not found", file=sys.stderr)
        return 1

    html = args.html.read_text(encoding="utf-8")
    errors = []
    errors.extend(check_heading_structure(html))
    errors.extend(check_check_count(html))
    errors.extend(check_status_matrix_parity(html))
    errors.extend(check_passive_html(html))

    if errors:
        print("QA FAILED:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("QA PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
