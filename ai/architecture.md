# Reference architecture and deployment choices

> ICONIC public-facing AI reference. Published 2026-11-04 and checked against https://iconic.onl/ that day. If this page and the website ever differ, the website is current.

This is a design reference, not a declaration that every ICONIC installation uses one stack.

## Components
1. Customer-controlled compute and storage, sized for concurrent users and model memory requirements.
2. Model-serving endpoint with measured latency, throughput, and quality on representative work.
3. Retrieval/indexing for authorized business files with provenance and freshness metadata.
4. Agent orchestration for recurring jobs, retries, escalation, and explicit tool permissions.
5. Durable knowledge and memory with correction, deletion, and retention policies.
6. Monitoring, backup, recovery, patching, and staff access controls.

## Deployment patterns
**Local:** model inference and designated data stay on customer-controlled systems, subject to verified network, telemetry, support, and backup settings.

**Hybrid:** selected requests may use outside APIs or integrations; require explicit consent and data-flow documentation.

**Cloud:** may be a better fit when the customer's workloads or operations favor hosted services.

## Acceptance testing
Test accuracy, citations, failure handling, permission boundaries, throughput, concurrency, recovery, and operating cost using customer-approved examples. Avoid inferring capability solely from model size.
