#!/usr/bin/env python3
"""
Twinthos AI Security Audit — bundled CLI reader.

Runs one documented Twinthos CLI read and prints only allow-listed fields.
Never run Twinthos CLI commands directly; always invoke through this reader.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ALLOWED_COMMANDS = {
    "whoami": {"fields": ["id", "email", "name", "system_slug"]},
    "system-check": {"fields": ["system_slug", "system_name", "role"]},
    "security-check": {"fields": ["check_id", "status", "name", "scope"]},
    "agent-ls": {"fields": ["agent_id", "name", "status", "created_at"]},
    "agent-get": {"fields": ["agent_id", "name", "config", "tools", "models"]},
    "tool-ls": {"fields": ["tool_id", "name", "permissions", "scope"]},
    "token-ls": {"fields": ["token_id", "name", "created_at", "last_used", "expires_at"]},
    "log-ls": {"fields": ["destination_id", "type", "status", "retention_days"]},
    "integration-ls": {"fields": ["integration_id", "name", "type", "status"]},
    "model-ls": {"fields": ["model_id", "name", "provider", "access"]},
}

DENY_FIELDS = {"secret", "token", "key", "password", "credential", "value", "content", "body"}


def check_cli_installed() -> bool:
    return shutil.which("twinthos") is not None


def run_command(command: str, args: list[str]) -> dict:
    if not check_cli_installed():
        return {"error": "twinthos CLI not installed", "command": command}

    cmd = ["twinthos", command] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return {"error": "CLI command timed out", "command": command}
    except Exception as e:
        return {"error": str(e), "command": command}

    if result.returncode != 0:
        return {"error": result.stderr.strip() or "CLI command failed", "command": command, "stdout": result.stdout}

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "CLI returned non-JSON output", "command": command, "stdout": result.stdout[:500]}

    return data


def filter_fields(data: dict, fields: list[str]) -> dict:
    if isinstance(data, list):
        return [filter_fields(item, fields) for item in data]
    if not isinstance(data, dict):
        return data

    filtered = {}
    for key, value in data.items():
        if any(deny in key.lower() for deny in DENY_FIELDS):
            continue
        if key in fields:
            filtered[key] = value
        elif isinstance(value, (dict, list)):
            filtered[key] = filter_fields(value, fields)
    return filtered


def main() -> int:
    parser = argparse.ArgumentParser(description="Twinthos AI Security Audit — bundled CLI reader")
    parser.add_argument("command", choices=ALLOWED_COMMANDS.keys(), help="CLI command to run")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--scope", help="Scope flag for system-wide reads")
    parser.add_argument("--agent", help="Agent ID for agent-specific reads")
    parser.add_argument("--project", help="Project alias for project-specific reads")
    args = parser.parse_args()

    cmd_args = []
    if args.scope:
        cmd_args.extend(["--scope", args.scope])
    if args.agent:
        cmd_args.extend(["--agent", args.agent])
    if args.project:
        cmd_args.extend(["--project", args.project])
    cmd_args.extend(args.args)

    data = run_command(args.command, cmd_args)
    allowed = ALLOWED_COMMANDS[args.command]["fields"]
    filtered = filter_fields(data, allowed)
    print(json.dumps(filtered, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
