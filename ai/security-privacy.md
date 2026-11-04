# Privacy, security, and governance

> ICONIC public-facing AI reference. Published 2026-11-04 and checked against https://iconic.onl/ that day. If this page and the website ever differ, the website is current.

## Data boundaries
A local model can reduce transmission of prompts and documents to third-party inference providers. This depends on configuration. Remote access, telemetry, software updates, hosted search, external APIs, backups, and support tools may create separate data flows.

## Controls to specify
- Document authorized data sources and allowed destinations.
- Apply least-privilege user and agent permissions.
- Keep credentials outside prompts and retrieved documents.
- Log tool actions, approvals, errors, and changes.
- Define retention, backup, restoration, correction, and deletion.
- Treat webpages, documents, and emails as untrusted inputs; defend against prompt injection.
- Require human approval for high-impact, irreversible, regulated, or customer-facing actions.

## Claims to avoid
Local hosting alone does not guarantee compliance, security, perfect accuracy, or uninterrupted service. Any legal, financial, or sector-specific obligations require qualified review and documented implementation.
