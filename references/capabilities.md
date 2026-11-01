# Capabilities

This reference lists the supported reads, CLI commands, browser views and routing rules for the Twinthos AI Security Audit skill. Read this in full before any account read.

## CLI version

Minimum tested CLI version: 1.0.0 (help checked). Specific output shapes were also checked against CLI 1.2.0, and the security check slug list against the CLI 1.3.0 package source, without a further guided run. Updating to the latest CLI before an audit is recommended, not required. Older CLIs can lack the `security` command entirely (0.9.0 does); the skill then records that check as a capability gap with an "upgrade the CLI" note rather than guessing equivalent commands.

## Routing

The skill routes checks in this order:

1. **Authenticated MCP connector** — preferred for safe, scoped reads where the connector's schema and response contract are verified.
2. **Documented CLI fallback** — used when no MCP connector is available or the check is not mapped. Every CLI account read goes through the bundled reader, `scripts/cli_read.py`, never as a bare or ad-hoc filtered command.
3. **Safe browser evidence** — used for dashboard-only controls, conflicting evidence, and confirmation of actual UI state.
4. **Explicit gap** — recorded when no safe read path exists.

A read-only label is not an allowance. Deny unknown tools pending verified schema/response contracts.

## Supported CLI reads

The bundled reader `scripts/cli_read.py` supports these commands:

- `twinthos whoami` — confirm authenticated identity
- `twinthos system-check` — confirm system membership
- `twinthos security check` — run baseline security check
- `twinthos agent-ls` — list authorised agents
- `twinthos agent-get <id>` — inspect agent configuration
- `twinthos tool-ls` — list allowed tools
- `twinthos token-ls` — list API tokens (metadata only)
- `twinthos log-ls` — list log destinations (metadata only)
- `twinthos integration-ls` — list third-party integrations
- `twinthos model-ls` — list allowed models

The reader prints only allow-listed fields. Never run these commands directly; always invoke through `scripts/cli_read.py`.

## Pagination and bounded collection

- Record per-source/feed windows, totals, received/inspected counts, caps, truncation, cursor/end knowledge and missing/failed reads with retry outcomes.
- A count of 100 is not completeness. No cursor without a verified end, truncation, or a bounded retry after a failed wider query remains a coverage gap.
- State any verified conclusion that no limits remain and its basis explicitly.

## What counts as field selection before exposure

Only these mechanisms satisfy the pre-exposure gate:

- The bundled CLI reader (`scripts/cli_read.py`) — it selects allow-listed fields before printing.
- A verified metadata-only connector contract — the connector returns only approved fields.
- A named-field page script on a host with no automatic capture — the script selects fields before any automatic screenshot or text extraction.

Ad-hoc filters and after-the-fact redaction do not satisfy this gate. Some hosts capture a full page automatically on navigation. Where pre-exposure selection cannot be established, do not automate sensitive member, credential or environment views; use owner-supplied non-sensitive summaries, labelled as owner statements, or record not_reviewed.

## Important distinctions

- A `satisfactory` product check means the inspected subsetting passed within the verified scope. It does not mean the whole checklist ID or system is secure.
- A muted or unavailable product check is never passing: record it as `muted` or `unknown`, not `satisfactory`.
- An optional policy being off is not automatically a vulnerability; a plan lacking a feature is not a misconfiguration.
- A metadata change does not prove credential rotation; age does not prove an agent is unused.
