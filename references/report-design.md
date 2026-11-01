# Report design

This reference covers community identity, offline rendering, structural QA and print checks for the Twinthos AI Security Audit skill.

## Community identity

- This skill is community-maintained and unofficial.
- Do not add official Twinthos branding to rendered reports.
- The report must carry the disclaimer: "This is a community-maintained, unofficial review. It is not a penetration test, security certification, compliance assessment, or ongoing monitoring service."
- Do not imply endorsement by any AI platform or agent provider.

## Offline rendering

- The bundled renderer uses only local assets: `assets/report.html`, `assets/report.css`, and embedded fonts.
- The report does not fetch remote assets or use analytics.
- Font licensing is documented in `assets/fonts/`; retain provenance notices.

## Nonvisual structural QA

Run `scripts/check_report.py` on every rendered HTML. It enforces:

- Heading structure: `Appendix` headings must be second-level and begin with "Appendix".
- Check count: every one of the 24 core and four optional IDs must appear exactly once under an Appendix heading.
- Status matrix parity: each matrix row's least-favourable status must equal its appendix outcome.
- Passive HTML: no `<script>` tags, no external fetches, no form submissions.

## Print checks

- Verify rendered pages on A4 (595.28×841.89pt).
- Confirm margins do not clip content.
- Confirm page breaks do not split check outcomes across pages.
- Confirm colour contrast for status badges in grayscale.
