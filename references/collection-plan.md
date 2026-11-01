# Preflight and collection plan

Read this before any account read. It covers authentication, scope confirmation, browser setup, and evidence handling.

## Preflight checklist

- [ ] User has confirmed the system slug and authorised scope.
- [ ] User has confirmed identity via the runtime's normal authentication flow.
- [ ] CLI/connector and browser account/system match is confirmed.
- [ ] Python 3 is available if the CLI route will be used.
- [ ] `scripts/cli_read.py` is present and readable if the CLI route will be used.
- [ ] Browser is authenticated through user handoff; no auto-login.
- [ ] Host browser capabilities and OAuth scopes are recorded.
- [ ] Privacy gates are confirmed; sensitive fields will be redacted before exposure.

## Collection plan

For each check in the checklist:

1. Determine the primary read source (CLI, connector, browser, owner statement).
2. Verify the read is within the agreed scope.
3. Run the read through the approved mechanism (CLI reader, connector, browser).
4. Record the observation: UTC timestamp, scope alias, source kind, evidence reference, observed setting, visibility limits.
5. Assign a status using the vocabulary in [evidence assessment](evidence-assessment.md).
6. If evidence is insufficient, record the gap and move to the next check.

Do not present planned or failed reads as successful collection. Record missing access as unknown, not disabled.

## Owner round timing

Run the inline owner round after the planned collection pass and provisional assessment, before drafting the first report. The round asks only about checks still needs_confirmation or not_reviewed where an owner statement could help. It does not expand scope.
