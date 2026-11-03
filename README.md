# Twinthos AI Security Audit

**A scoped, evidence-led, read-only review of AI agent security configuration.**

Twinthos AI Security Audit is a read-only security review skill for AI agent systems. It inspects your platform configuration, connector permissions, agent definitions, deployment boundaries and monitoring setup through authenticated APIs, CLI tools and browser evidence. It produces an evidence-backed action plan and leaves your settings unchanged.

This is a Twinthos product. It is not affiliated with any AI platform vendor.

## What it audits

- **Identity and access** — API keys, service accounts, role assignments, least-privilege gaps
- **Agent configuration** — tool permissions, escalation rules, human-in-the-loop settings, decision boundaries
- **Data handling** — secrets storage, PII access, retrieval sources, knowledge base isolation
- **Deployment posture** — network exposure, CORS, firewall rules, environment separation
- **Governance** — audit logging, approval chains, incident response, change control
- **Integration surface** — MCP connectors, webhooks, third-party tool access, scope creep
- **Monitoring** — alert coverage, anomaly detection, failure modes, on-call escalation
- **Source control** — repository exposure, secret scanning, branch protection, CI/CD hygiene

24 core checks across 8 domains, plus 4 optional deeper checks for prompt-injection boundaries, repository governance, secret handling design and agent recovery.

## How it works

1. Confirm the account, authorised system, agents and review scope.
2. Discover installed AI platform tools, CLI support and connector permissions.
3. Run supported security checks and scoped inventory reads through authenticated APIs or the bundled CLI reader.
4. Use the browser to confirm dashboard-only settings, subscriptions and evidence gaps.
5. Record all checklist results with status, evidence and remediation guidance.
6. Produce `security-audit.md` and, where supported, sanitised `security-audit.json`.
7. Stop for human review. Changes and report delivery are separate actions.

The skill never modifies configuration, deploys changes, retrieves environment values or sends reports on your behalf.

## Install

```sh
npx skills add twinthos/ai-sec-audit --skill twinthos-ai-sec-audit
```

For agent-specific install:

```sh
npx skills add twinthos/ai-sec-audit --skill twinthos-ai-sec-audit --agent <agent-name>
```

Global install:

```sh
npx skills add twinthos/ai-sec-audit --skill twinthos-ai-sec-audit --global
```

## Requirements

- A host that loads standard SKILL.md instructions and reference files
- Your normal, authorised AI platform account access
- Platform plugin read capabilities and/or an installed CLI
- Python 3 (standard library only) for CLI-based audits and HTML export
- Browser tools for dashboard-only evidence and human authentication handoff

The skill uses verified read operations only. Its bundled CLI reader restricts supported command names and identifier/flag syntax; it does not make an unsafe CLI or excessive account permissions safe. Runtime permissions and account roles remain the actual security boundary.

## Output

- `security-audit.md` — Markdown report with findings, evidence and remediation steps
- `security-audit.json` — optional structured JSON for tooling integration
- Styled HTML report — printable, self-contained, no external assets

## Verification and scope

The current `tests_current/` suite covers packaging, CLI argument restrictions, evidence scope validation, safe report rendering, revision persistence, canonical checklist IDs and matrix/appendix consistency. It uses synthetic fixtures and does **not** prove the behaviour or permissions of a third-party CLI, browser, account or agent runtime.

The unrelated Vercel-derived `tests/` directory has been removed from the current branch. Its history remains in Git; those tests are not represented as Twinthos security coverage.

## Validate

```sh
python3 -m unittest discover -s tests_current -v
python3 scripts/render_report.py examples/security-audit.md -o /tmp/twinthos-audit.html
python3 scripts/check_report.py /tmp/twinthos-audit.html
```

The example report is entirely synthetic. The core checklist contains 24 unique IDs in eight domains, plus four separately authorised optional checks. Unobserved controls remain `not_reviewed`. Tests require only the Python 3 standard library; oldest tested version: Python 3.9.

## Licence

MIT. See `LICENSE` for details.

## Support

- Security vulnerabilities: `security@twinthos.com`
- Product questions: `hello@twinthos.com`
- Live site: [twinthos.com](https://twinthos.com)
