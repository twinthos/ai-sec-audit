# Report model

Optional JSON schema for versioned evidence records. Markdown remains the mandatory deliverable; this schema is for structured append/rebuild only.

## Observation record

```json
{
  "topic_id": "AGT-01",
  "scope_alias": "example-system",
  "observed_at": "2026-10-31T14:00:00Z",
  "source_kind": "browser",
  "source_description": "Owner-visible agent configuration",
  "evidence_ref": "example-evidence-01",
  "observed": {
    "job_spec_present": true,
    "approval_required": true,
    "escalation_defined": true
  },
  "status": "satisfactory",
  "rationale": "Job spec, approval gates and escalation are all documented and visible.",
  "limitation": "Behaviour not tested; policy not enforced under load."
}
```

## Revision record

```json
{
  "revision": 1,
  "created_at": "2026-10-31T14:00:00Z",
  "scope_alias": "example-system",
  "author": "agent",
  "summary": {
    "core_total": 24,
    "core_satisfactory": 18,
    "core_action_recommended": 3,
    "core_needs_confirmation": 2,
    "core_not_reviewed": 1,
    "optional_total": 4,
    "optional_accepted": 2,
    "optional_declined": 2
  },
  "evidence": [ ... ]
}
```

## Coverage feed record

```json
{
  "feed_alias": "browser-dashboard",
  "source_kind": "browser",
  "window": {
    "requested_start": "2026-10-31T13:00:00Z",
    "requested_end": "2026-10-31T15:00:00Z",
    "actual_start": "2026-10-31T13:05:00Z",
    "actual_end": "2026-10-31T14:55:00Z"
  },
  "reported_total": "unknown",
  "received": 42,
  "inspected": 42,
  "page_cap": "unknown",
  "truncation": "no",
  "cursor_availability": "unknown",
  "end_known": "yes",
  "missing_sources": "none",
  "timeouts_failures": "none",
  "retries": [],
  "assessment_effect": "bounded conclusions; one check needs_confirmation due to pagination gap"
}
```
