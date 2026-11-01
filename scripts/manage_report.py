#!/usr/bin/env python3
"""
Twinthos AI Security Audit — optional JSON report model.

Validates, appends evidence to a new revision, and rebuilds Markdown.
Markdown remains the mandatory deliverable.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_KEYS = {"topic_id", "scope_alias", "observed_at", "source_kind", "status", "rationale"}
ALLOWED_STATUSES = {"satisfactory", "action_recommended", "needs_confirmation", "not_reviewed", "not_applicable"}


def validate_observation(obs: dict) -> list[str]:
    errors = []
    missing = REQUIRED_KEYS - obs.keys()
    if missing:
        errors.append(f"Missing keys: {missing}")
    if obs.get("status") not in ALLOWED_STATUSES:
        errors.append(f"Invalid status: {obs.get('status')}")
    return errors


def load_model(path: Path) -> dict:
    if not path.exists():
        return {"revisions": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_model(path: Path, model: dict) -> None:
    path.write_text(json.dumps(model, indent=2, default=str), encoding="utf-8")


def append_revision(model_path: Path, evidence: list[dict], scope_alias: str) -> dict:
    model = load_model(model_path)
    revision = max([r.get("revision", 0) for r in model.get("revisions", [])] + [0]) + 1
    summary = {
        "revision": revision,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scope_alias": scope_alias,
        "author": "agent",
        "summary": {
            "core_total": 24,
            "core_satisfactory": sum(1 for e in evidence if e.get("status") == "satisfactory" and e.get("topic_id", "").startswith(tuple("AGT IAM SEC DEP GOV INT MON".split()))),
            "core_action_recommended": sum(1 for e in evidence if e.get("status") == "action_recommended"),
            "core_needs_confirmation": sum(1 for e in evidence if e.get("status") == "needs_confirmation"),
            "core_not_reviewed": sum(1 for e in evidence if e.get("status") == "not_reviewed"),
            "optional_total": 4,
            "optional_accepted": sum(1 for e in evidence if e.get("topic_id") in {"AGT-04", "SRC-04", "SEC-04", "OPS-04"} and e.get("status") != "not_reviewed"),
            "optional_declined": sum(1 for e in evidence if e.get("topic_id") in {"AGT-04", "SRC-04", "SEC-04", "OPS-04"} and e.get("status") == "not_reviewed"),
        },
        "evidence": evidence,
    }
    model.setdefault("revisions", []).append(revision)
    model["revisions"][-1] = revision
    # Actually store the revision dict separately
    if "revision_records" not in model:
        model["revision_records"] = []
    model["revision_records"].append(revision)
    model[f"revision_{revision}"] = revision_dict = {"revision": revision, "created_at": datetime.now(timezone.utc).isoformat(), "scope_alias": scope_alias, "author": "agent", "summary": summary["summary"], "evidence": evidence}
    save_model(model_path, model)
    return revision_dict


def rebuild_markdown(model_path: Path, output_path: Path) -> None:
    model = load_model(model_path)
    latest = None
    for key in sorted(model.keys(), reverse=True):
        if key.startswith("revision_"):
            latest = model[key]
            break
    if not latest:
        output_path.write_text("# Security configuration review - [scope alias]\n\nNo evidence recorded.\n", encoding="utf-8")
        return

    lines = [f"# Security configuration review - {latest['scope_alias']}", ""]
    lines.append("## Status at a glance")
    lines.append("")
    lines.append("| Check | System | Agent | Status |")
    lines.append("| --- | --- | --- | --- |")
    for e in latest.get("evidence", []):
        lines.append(f"| {e.get('topic_id', '')} | | | {e.get('status', '')} |")
    lines.append("")
    lines.append("## Review summary")
    lines.append("")
    lines.append(f"Core coverage: {latest['summary']['core_satisfactory']} satisfactory, {latest['summary']['core_action_recommended']} action_recommended, {latest['summary']['core_needs_confirmation']} needs_confirmation, {latest['summary']['core_not_reviewed']} not_reviewed.")
    lines.append("")
    lines.append("## Appendix: check outcomes")
    lines.append("")
    for e in latest.get("evidence", []):
        lines.append(f"### {e.get('topic_id', '')}")
        lines.append("")
        lines.append(f"Status: {e.get('status', '')}")
        lines.append(f"- Rationale: {e.get('rationale', '')}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage Twinthos AI security audit JSON model")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate an observation JSON file")
    validate_parser.add_argument("file", type=Path)

    append_parser = subparsers.add_parser("append", help="Append evidence as a new revision")
    append_parser.add_argument("model", type=Path)
    append_parser.add_argument("evidence", type=Path)
    append_parser.add_argument("--scope", required=True)

    rebuild_parser = subparsers.add_parser("rebuild", help="Rebuild Markdown from latest revision")
    rebuild_parser.add_argument("model", type=Path)
    rebuild_parser.add_argument("output", type=Path)

    args = parser.parse_args()

    if args.command == "validate":
        data = json.loads(args.file.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = [data]
        all_errors = []
        for obs in data:
            all_errors.extend(validate_observation(obs))
        if all_errors:
            for error in all_errors:
                print(f"ERROR: {error}")
            return 1
        print("Validation passed")
        return 0

    if args.command == "append":
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
        if isinstance(evidence, dict):
            evidence = [evidence]
        for obs in evidence:
            errors = validate_observation(obs)
            if errors:
                for error in errors:
                    print(f"ERROR: {error}")
                return 1
        revision = append_revision(args.model, evidence, args.scope)
        print(f"Appended revision {revision['revision']}")
        return 0

    if args.command == "rebuild":
        rebuild_markdown(args.model, args.output)
        print(f"Rebuilt {args.output}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
