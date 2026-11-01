# MCP boundary

This reference defines the MCP tool denylist and conditional metadata allowlist for the Twinthos AI Security Audit skill.

## Denylist

Never invoke these MCP tools during an audit, regardless of their read-only label:

- Any tool that writes, updates, deletes or deploys configuration.
- Any tool that sends messages, emails, webhooks or notifications.
- Any tool that retrieves secret values, environment variables, log contents, or raw credentials.
- Any tool that bypasses access controls or escalates privileges.
- Any tool that runs arbitrary code, builds, tests or scans against live systems.
- Any tool that modifies agent behaviour, tool permissions, or approval policies.

## Conditional allowlist

These tools are allowed only when all conditions are met:

- `list_tokens` — allowed only when the connector returns metadata (count, alias, expiry visibility) and never secret values. If the connector returns token strings, deny it and use the browser route instead.
- `list_secrets` — allowed only when the connector returns metadata (count, alias, protection attributes) and never secret values. If the connector returns secret values, deny it and use the browser route instead.
- `list_audit_events` — allowed only when the connector returns sanitised event metadata (timestamp, event type, actor alias) and never log bodies or personal identifiers.
- `get_agent` — allowed only for configuration metadata; never invoke tools that execute the agent or retrieve conversation history.
- `list_integrations` — allowed only for metadata; never invoke tools that test or modify integrations.

## Unknown tools

If an MCP tool is not listed here, deny it by default. A read-only label is not an allowance. Record the denial as a capability gap and continue with the next available route.
