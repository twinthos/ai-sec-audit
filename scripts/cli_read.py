#!/usr/bin/env python3
"""
Twinthos AI Security Audit — bundled CLI reader.

Runs one documented Twinthos CLI read and prints only allow-listed fields.
Never run Twinthos CLI commands directly; always invoke through this reader.
"""

import argparse
import json
import re
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

# The CLI is a separate trust boundary. A pre-approved read command must not
# receive arbitrary flags such as write/export/delete controls via positional args.
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_./:@-]{0,127}\\Z")
SCOPED_FLAGS = {"--scope", "--agent", "--project"}


def safe_cli_args(args: list[str]) -> bool:
    if not isinstance(args, list) or len(args) > 8:
        return False
    seen = set()
    positional = 0
    index = 0
    while index < len(args):
        arg = args[index]
        if not isinstance(arg, str):
            return False
        if arg in SCOPED_FLAGS:
            if arg in seen or index + 1 >= len(args):
                return False
            seen.add(arg)
            value = args[index + 1]
            if not isinstance(value, str) or not IDENTIFIER.fullmatch(value) or ".." in value:
                return False
            index += 2
            continue
        if arg.startswith("-") or not IDENTIFIER.fullmatch(arg) or ".." in arg:
            return False
        positional += 1
        if positional > 1:
            return False
        index += 1
    return True


def check_cli_installed() -> bool:
    return shutil.which("twinthos") is not None


def run_command(command: str, args: list[str]) -> dict:
    if command not in ALLOWED_COMMANDS or not safe_cli_args(args):
        return {"error_code": "invalid_cli_arguments", "command": command}
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
        # CLI diagnostics may contain credentials or personal information.
        return {"error_code": "cli_failed", "command": command, "exit_code": result.returncode}

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error_code": "non_json_output", "command": command}

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
            if isinstance(value, (dict, list)):
                # Never return nested objects wholesale: these may contain secrets.
                filtered[key] = filter_fields(value, fields)
            elif value is None or isinstance(value, (str, int, float, bool)):
                filtered[key] = value
        elif isinstance(value, (dict, list)):
            nested = filter_fields(value, fields)
            if nested:
                filtered[key] = nested
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
    if isinstance(data, dict) and ("error" in data or "error_code" in data):
        print(json.dumps({"status": "unavailable", "error_code": data.get("error_code", "cli_unavailable")}, indent=2))
        return 1
    allowed = ALLOWED_COMMANDS[args.command]["fields"]
    filtered = filter_fields(data, allowed)
    print(json.dumps(filtered, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
