# Browser evidence safety

This reference covers automatic full-viewport screenshots, sensitive destination classification, safe per-check owner questions and the accidental-exposure procedure.

## Pre-model browser gate

Before any browser navigation or capture:

1. Confirm the intended account/system and planned destination.
2. Verify the destination belongs to the authorised scope and contains no credentials or bypass values.
3. If pre-exposure selection cannot be established, do not automate sensitive views; use owner-supplied non-sensitive summaries or record not_reviewed.

## Sensitive destination classification

Classify every browser destination before navigation:

- **Safe**: public documentation, help pages, marketing pages, public status pages.
- **Sensitive**: dashboards, settings pages, member lists, credential metadata, log views, agent configurations.
- **Restricted**: pages containing raw secrets, personal identifiers, or bypass values.

Never navigate to a restricted destination without explicit owner confirmation and a verified pre-exposure selection mechanism.

## Safe per-check owner questions

When a check needs owner confirmation, ask only the safe questions from the inline owner round. Never request:

- Passwords, session cookies, tokens, API keys, or recovery codes.
- Personal identifiers beyond role aliases.
- Screenshots revealing credentials or bypass values.
- Raw URLs containing tokens or secrets.

## Accidental exposure procedure

If a secret or personal identifier is seen during collection:

1. Stop the read immediately.
2. Do not record the value.
3. Notify the owner that exposure occurred, what was seen, and the source.
4. Record the incident as a security finding in the report.
5. Do not continue automated collection on that page or field.

A lighter path applies to low-severity metadata (agent names, project aliases): redact and continue, noting the redaction.

## UI-state playbook

Before interpreting any browser state:

- Verify control semantics: a toggle may be disabled, loading, or hidden. Do not infer state from visibility alone.
- Use read-only switch/input semantics. Do not click settings buttons, form submissions or toggles.
- Bound loading attempts: at most one privacy-safe reload with no form changes.
- Follow observed navigation rather than guessed routes. If a control is missing, record unknown.

## Inline owner round before the first report

When the owner is present in an interactive session, ask one batched round of owner questions after the planned collection pass and provisional assessment, before drafting the first report. Group questions by domain in one message, and accept "skip" or "don't know" for any question.

Record each answer as a timestamped owner statement, labelled separately from observed evidence. An answer never becomes observed configuration and never authorises broader access.
