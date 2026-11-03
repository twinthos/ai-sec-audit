#!/usr/bin/env python3
"""Versioned, evidence-led audit report model (stdlib only).

Never assumes missing evidence is satisfactory. Does not collect platform data.
"""
import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

CORE_PREFIXES = ("IAM", "AGT", "SEC", "DEP", "GOV", "INT", "MON", "SRC")
CORE_IDS = tuple(prefix + "-" + str(number).zfill(2)
                 for prefix in CORE_PREFIXES for number in range(1, 4))
OPTIONAL_IDS = ("AGT-04", "SRC-04", "SEC-04", "OPS-04")
ALL_IDS = CORE_IDS + OPTIONAL_IDS
REQUIRED_KEYS = {"topic_id", "scope_alias", "observed_at", "source_kind", "status", "rationale"}
ALLOWED_STATUSES = {"satisfactory", "action_recommended", "needs_confirmation",
                    "not_reviewed", "not_applicable"}
HIGH_CONFIDENCE_SECRETS = (
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----"),
)


def _scope_ok(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", value))


def validate_observation(obs: dict) -> list:
    if not isinstance(obs, dict):
        return ["Expected an observation object"]
    errors = []
    missing = REQUIRED_KEYS - obs.keys()
    if missing:
        errors.append("Missing required fields: " + ", ".join(sorted(missing)))
    if obs.get("topic_id") not in ALL_IDS:
        errors.append("Unknown or obsolete checklist ID")
    if obs.get("status") not in ALLOWED_STATUSES:
        errors.append("Invalid status")
    if not _scope_ok(obs.get("scope_alias")):
        errors.append("Scope alias must be a short non-sensitive identifier")
    if not isinstance(obs.get("source_kind"), str) or not obs.get("source_kind", "").strip():
        errors.append("Source kind is missing")
    if not isinstance(obs.get("rationale"), str) or not obs.get("rationale", "").strip() or len(obs.get("rationale", "")) > 2000:
        errors.append("Rationale must be 1–2000 characters")
    if not isinstance(obs.get("observed_at"), str):
        errors.append("Observed time must be an ISO timestamp")
    else:
        try:
            observed = datetime.fromisoformat(obs["observed_at"].replace("Z", "+00:00"))
            if observed.tzinfo is None:
                errors.append("Observed time must include timezone")
        except ValueError:
            errors.append("Invalid observed timestamp")
    # A heuristic guard, not full DLP. Never expose matched text in errors.
    if any(pattern.search(json.dumps(obs, default=str)) for pattern in HIGH_CONFIDENCE_SECRETS):
        errors.append("Credential-like value in observation; submit metadata only")
    return errors


def load_model(path: Path) -> dict:
    if not path.exists():
        return {"revisions": []}
    model = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(model, dict):
        raise ValueError("Audit model must be a JSON object")
    return model


def save_model(path: Path, model: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # A private temp file and atomic replacement prevent partial report writes.
    fd, tmp = tempfile.mkstemp(prefix=".audit-", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(model, out, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _next_revision(model):
    numbers = []
    for key in model:
        match = re.fullmatch(r"revision_(\d+)", key)
        if match and isinstance(model[key], dict):
            numbers.append(int(match.group(1)))
    for value in model.get("revisions", []):
        if isinstance(value, int) and value > 0:
            numbers.append(value)
        elif isinstance(value, dict) and isinstance(value.get("revision"), int):
            numbers.append(value["revision"])
    return max(numbers, default=0) + 1


def _prepare(evidence, scope_alias):
    if not _scope_ok(scope_alias):
        raise ValueError("Invalid scope alias")
    if not isinstance(evidence, list):
        raise ValueError("Evidence must be a list")
    seen = set()
    for item in evidence:
        problems = validate_observation(item)
        if problems:
            raise ValueError("; ".join(problems))
        if item["scope_alias"] != scope_alias:
            raise ValueError("Evidence scope does not match selected review scope")
        if item["topic_id"] in seen:
            raise ValueError("Repeated checklist ID in the same revision")
        seen.add(item["topic_id"])
    return {item["topic_id"]: item for item in evidence}


def _summary(observations):
    summary = {"core_total": len(CORE_IDS), "core_reviewed": 0,
               "optional_total": len(OPTIONAL_IDS), "optional_reviewed": 0}
    for status in sorted(ALLOWED_STATUSES):
        summary["core_" + status] = sum(
            1 for tid in CORE_IDS if observations.get(tid, {}).get("status", "not_reviewed") == status
        )
    summary["core_reviewed"] = sum(
        1 for tid in CORE_IDS if tid in observations and
        observations[tid]["status"] not in ("not_reviewed",)
    )
    summary["optional_reviewed"] = sum(
        1 for tid in OPTIONAL_IDS if tid in observations and
        observations[tid]["status"] != "not_reviewed"
    )
    return summary


def append_revision(model_path: Path, evidence: list, scope_alias: str) -> dict:
    observations = _prepare(evidence, scope_alias)
    model = load_model(model_path)
    number = _next_revision(model)
    revision = {
        "revision": number,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scope_alias": scope_alias,
        "author": "agent",
        "summary": _summary(observations),
        "evidence": evidence,
    }
    # Preserve the existing public model format for previously generated reports.
    model.setdefault("revisions", []).append(number)
    model.setdefault("revision_records", []).append(number)
    model["revision_" + str(number)] = revision
    save_model(model_path, model)
    return revision


def _latest_revision(model):
    candidates = []
    for key, value in model.items():
        match = re.fullmatch(r"revision_(\d+)", key)
        if match and isinstance(value, dict):
            candidates.append((int(match.group(1)), value))
    return max(candidates, key=lambda item: item[0])[1] if candidates else None


def _plain(value) -> str:
    # Do not permit a model-provided rationale to insert report structure.
    return " ".join(str(value).replace("|", "/").split())


def rebuild_markdown(model_path: Path, output_path: Path) -> None:
    model = load_model(model_path)
    latest = _latest_revision(model)
    if latest is None:
        output_path.write_text("# Security configuration review\n\nNo evidence recorded.\n", encoding="utf-8")
        return
    observations = {item["topic_id"]: item for item in latest.get("evidence", [])}
    summary = _summary(observations)
    lines = [
        "# Security configuration review - " + _plain(latest["scope_alias"]),
        "",
        "## Status at a glance",
        "",
        "| Check | System | Agent | Status |",
        "| --- | --- | --- | --- |",
    ]
    for tid in ALL_IDS:
        row = observations.get(tid, {})
        lines.append("| " + tid + " | " + _plain(latest["scope_alias"]) + " | | " +
                     row.get("status", "not_reviewed") + " |")
    lines += ["", "## Review summary", "",
              "Core checks: " + str(summary["core_total"]) +
              "; reviewed: " + str(summary["core_reviewed"]) +
              "; needs confirmation or not reviewed: " +
              str(summary["core_needs_confirmation"] + summary["core_not_reviewed"]) + ".",
              "Optional checks: " + str(summary["optional_total"]) +
              "; reviewed: " + str(summary["optional_reviewed"]) + ".",
              "",
              "## Appendix: check outcomes", ""]
    for tid in ALL_IDS:
        row = observations.get(tid, {})
        lines += ["### " + tid + " - Review outcome",
                  "",
                  "Status: " + row.get("status", "not_reviewed"),
                  "- Rationale: " + _plain(row.get("rationale", "No authorised evidence was provided.")),
                  ""]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage a read-only Twinthos security audit model")
    subs = parser.add_subparsers(dest="command", required=True)
    val = subs.add_parser("validate")
    val.add_argument("file", type=Path)
    ap = subs.add_parser("append")
    ap.add_argument("model", type=Path)
    ap.add_argument("evidence", type=Path)
    ap.add_argument("--scope", required=True)
    reb = subs.add_parser("rebuild")
    reb.add_argument("model", type=Path)
    reb.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            data = json.loads(args.file.read_text(encoding="utf-8"))
            data = [data] if isinstance(data, dict) else data
            _prepare(data, data[0]["scope_alias"] if data else "demo")
            print("Validation passed")
        elif args.command == "append":
            data = json.loads(args.evidence.read_text(encoding="utf-8"))
            revision = append_revision(args.model, [data] if isinstance(data, dict) else data, args.scope)
            print("Appended revision", revision["revision"])
        elif args.command == "rebuild":
            rebuild_markdown(args.model, args.output)
            print("Rebuilt", args.output.name)
        return 0
    except (ValueError, KeyError, OSError, TypeError, json.JSONDecodeError):
        # Raw exceptions and JSON input may contain personal data; do not echo them.
        print("Audit operation failed: invalid, inaccessible or inconsistent input", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
