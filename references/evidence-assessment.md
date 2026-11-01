# Evidence assessment

This reference defines the status vocabulary, owner statement handling, and deliberate configuration rules for the Twinthos AI Security Audit skill.

## Status vocabulary

Use exactly one status per check:

- `satisfactory`: observed evidence meets the stated requirement within the inspected scope; not a claim that the system is secure.
- `action_recommended`: evidence supports a specific improvement against an agreed requirement or documented risk.
- `needs_confirmation`: attempted review has missing, ambiguous, conflicting, or owner-dependent evidence.
- `not_reviewed`: collection was not performed or was unavailable; state why.
- `not_applicable`: the check genuinely does not apply; state a verified rationale.

## Evidence rules

- Keep evidence separate from interpretation.
- Distinguish owner statements from directly observed evidence.
- Record a missing field as unknown, not disabled.
- An optional policy being off is not automatically a vulnerability.
- A metadata change does not prove credential rotation; age does not prove an agent is unused.
- Code or Git organization names do not prove ownership.
- Platform API authentication does not establish application authentication.

## Owner statements from the inline round

Record each owner answer as a timestamped owner statement (`source_kind: owner_statement`). An answer never promotes a check status; it only resolves needs_confirmation or not_reviewed items where the owner's statement is sufficient evidence.

- Skipped or unknown answers leave the status unchanged.
- Reuse answers from the inline round without re-asking them.
- Unanswered questions remain explicitly not answered.

## Deliberate configuration and owner acceptance

Before recording action_recommended for a setting that could be deliberate:

1. Check the owner-controlled codebase for intent if agreed and within scope.
2. Ask the owner once if intent is not already explicit.
3. Record the owner's reason and date.

A setting counts as owner-accepted only when the owner gives a reason. It stays needs_confirmation with the reason and date recorded, and moves out of the initial priorities and recommendations into the report's deliberate or owner-accepted settings note. Source-code evidence of intent alone is not owner acceptance.

If the config-intent read is not allowed or not possible, record "codebase intent not checked" with the reason, and ask the owner about intent instead.

## Applicability decisions

A check is not_applicable only when verified, current feature-specific account facts and public documentation establish non-applicability. A 403, upgrade prompt or plan label alone does not establish not_applicable, but a structured plan entitlement field from a verified read can when current documentation agrees.
