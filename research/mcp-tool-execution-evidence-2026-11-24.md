# From MCP tool listings to actual calls: ICONIC's first execution-backed benchmark

*ICONIC research | November 24, 2026*

A tool's name and input schema do not establish that it works. ICONIC is developing a controlled way to distinguish advertised MCP capabilities, actual read-only tool execution, and agent tool-selection behavior.

## What we actually ran

On November 24, 2026, ICONIC issued six **real MCP tools/call requests**, using fixed, public documentation queries and no authentication or payment credentials:

| Provider | Tested public documentation capability | Observed result |
|---|---|---|
| Microsoft Learn | Fetch Azure Functions HTTP-trigger documentation | Topical smoke pass |
| Microsoft Learn | Search Azure Functions documentation | Topical smoke pass |
| Twilio | Search official SMS Messaging API documentation | Topical smoke pass |
| Context7 | Resolve the public React documentation library | Topical smoke pass |
| Context7 | Retrieve React useEffect cleanup documentation | Topical smoke pass |
| AWS Knowledge | Search AWS Lambda function URL documentation | Topical smoke pass |

**6/6** passed predetermined topic checks in the final strict run. Every case returned HTTP 200, did not report an MCP tool-level error, returned nontrivial content, and contained the expected task-specific terms. We preserved hashes and test criteria for later reproduction without retaining complete third-party documentation.

We also kept an important failed run: our first strict attempt passed only **2/6** because our client incorrectly handled valid server-sent-event responses as JSON. After fixing the **client-side** Content-Type handling, the exact same six scenarios passed **6/6**. This was not evidence of provider malfunction.

## Why this matters for MCP discovery

A separate ICONIC read-only survey inspected ten public MCP tool catalogs. Although they advertised web-search functionality, only six exposed an unambiguous required single-URL read input under conservative schema rules; two needed an adapter and two were inconclusive. Those are **metadata classifications**, not actual execution results for those ten services.

Together, the studies illustrate why an MCP publisher may need more than a registry listing or a tool-selection score. Selection, input compatibility, actual tool-call outcomes, and repeatability are separate questions.

## What we are not claiming

These six tasks span four distinct documentation services, **not competing providers doing the same job**. One execution per task is not a service-reliability estimate. Expected topical words are not an independent expert review of answer correctness. No customer or production paid server was tested, no third-party private data was accessed, and no causal change in agent adoption has been demonstrated.

ICONIC's original commercial hosted-model Selection Test remains paused pending additional model, competitor-equivalence, and payment-fulfillment verification. The execution benchmark does not change that status.

**Next research step:** Repeat independently verified, consented *same-job* task evaluations over time, preserve failures and schema/version changes, and test whether an actionable report actually improves a publisher's agent discoverability or task completion. ICONIC can run the public, read-only baseline without relying on a platform partnership.

*This is a public research note. Technical source, private holdout controls, exact execution metadata, and audit evidence remain in ICONIC's private research repository.*
