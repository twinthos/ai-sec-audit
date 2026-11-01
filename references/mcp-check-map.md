# MCP check map

Per-check routing map: authenticated MCP first where verified safe, documented CLI fallback where available, then safe browser evidence or an explicit gap.

## IAM-01 - Agent and user identity management
- MCP: `list_agents`, `get_member`
- CLI: `agent-ls`, `system-check`
- Browser: dashboard Members page
- Owner: role confirmation

## IAM-02 - Authentication and authorisation policy
- MCP: none
- CLI: none
- Browser: dashboard Security > Authentication
- Owner: MFA policy confirmation

## IAM-03 - API key and token inventory
- MCP: `list_tokens`
- CLI: `token-ls`
- Browser: dashboard Settings > API Keys
- Owner: token count confirmation

## AGT-01 - Agent job specification completeness
- MCP: `get_agent`
- CLI: `agent-get <id>`
- Browser: dashboard Agents > [agent] > Configuration
- Owner: job spec confirmation

## AGT-02 - Tool-call permission scope
- MCP: `list_tools`, `get_tool_permissions`
- CLI: `tool-ls`
- Browser: dashboard Agents > [agent] > Tools
- Owner: tool purpose confirmation

## AGT-03 - Prompt-injection defences
- MCP: none
- CLI: none
- Browser: dashboard Agents > [agent] > Prompts > Safety
- Owner: testing confirmation

## AGT-04 - Model and provider access controls
- MCP: `list_models`
- CLI: `model-ls`
- Browser: dashboard Settings > Models
- Owner: model allowlist confirmation

## SEC-01 - Secret storage and rotation
- MCP: `list_secrets` (metadata only)
- CLI: none (browser only for secrets)
- Browser: dashboard Settings > Environment Variables
- Owner: secret count and rotation confirmation

## SEC-02 - Data access and retention policy
- MCP: `get_data_policy`
- CLI: none
- Browser: dashboard Settings > Data
- Owner: retention and classification confirmation

## SEC-03 - Log access, export, and redaction
- MCP: `list_log_destinations`
- CLI: `log-ls`
- Browser: dashboard Settings > Logs
- Owner: log destination confirmation

## DEP-01 - Agent endpoint protection
- MCP: `get_deployment`
- CLI: none
- Browser: dashboard Deployments > [deployment] > Settings
- Owner: protection scope confirmation

## DEP-02 - Preview and test environment isolation
- MCP: `list_environments`
- CLI: none
- Browser: dashboard Deployments > Environments
- Owner: sharing policy confirmation

## DEP-03 - Agent versioning and rollback capability
- MCP: `list_deployments`
- CLI: none
- Browser: dashboard Deployments > History
- Owner: rollback test confirmation

## GOV-01 - Human-in-the-loop approval gates
- MCP: `get_approval_policy`
- CLI: none
- Browser: dashboard Agents > [agent] > Approvals
- Owner: threshold confirmation

## GOV-02 - Audit trail completeness
- MCP: `list_audit_events`
- CLI: none
- Browser: dashboard Activity
- Owner: review process confirmation

## GOV-03 - Incident response and escalation
- MCP: `get_alert_policy`
- CLI: none
- Browser: dashboard Settings > Alerts
- Owner: escalation confirmation

## INT-01 - Third-party tool permissions
- MCP: `list_integrations`
- CLI: `integration-ls`
- Browser: dashboard Integrations
- Owner: integration purpose confirmation

## INT-02 - Integration lifecycle accountability
- MCP: `get_integration`
- CLI: `integration-ls`
- Browser: dashboard Integrations > [integration]
- Owner: offboarding confirmation

## INT-03 - Supply chain integrity
- MCP: none
- CLI: none
- Browser: dashboard Settings > Security > Supply Chain
- Owner: contributor policy confirmation

## MON-01 - Observability and alerting coverage
- MCP: `get_monitoring`
- CLI: none
- Browser: dashboard Monitoring
- Owner: review cadence confirmation

## MON-02 - Rate limiting and abuse protection
- MCP: `get_rate_limits`
- CLI: none
- Browser: dashboard Settings > Rate Limits
- Owner: legitimate automation confirmation

## MON-03 - Error handling and graceful degradation
- MCP: none
- CLI: none
- Browser: dashboard Agents > [agent] > Error Handling
- Owner: test results confirmation
