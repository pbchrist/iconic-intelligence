# MCP tool compatibility: why matching tool names is not enough

*ICONIC research note | 24 November 2026*

We tested a deterministic, model-independent metadata-contract checker against a **private, frozen corpus of synthetic MCP schemas**. We then inspected public tool catalogs using read-only MCP discovery. No remote tools were executed and no customers were involved.

## What the experiment actually measured

- **16/16** calibration schema cases passed.
- **15/16** sealed synthetic holdouts passed. The failed case was preserved, not tuned away.
- **10/10** live read-only public MCP tool catalogs were retrieved.
- Of those ten services, **six** exposed a direct, required single-public-URL retrieval contract under conservative static rules; **two** needed an adapter and **two** remained inconclusive.
- **2/3** previously selected rival services exposed both a direct general web-search contract and a direct single-URL retrieval contract by those rules.

## What we learned

Some tools advertise URL extraction but require **arrays of URLs**, need adapters, or have optional rather than mandatory URL parameters. Others perform structured extraction from *supplied text*, rather than retrieving a public URL at all. Descriptions and tool names alone can therefore exaggerate functional equivalence.

The evidence labels four states: **direct schema match**, **adapter required**, **inconclusive**, and **no metadata match**. None of these states proves a remote tool will work correctly or indicates that a provider is trustworthy.

## Important limitations

The synthetic cases and expected labels were designed by ICONIC, not externally adjudicated. There was **no permitted tools/call execution**, no third-party correctness labels, no paid hosted models, and no causal discovery-uplift test. Tool catalogs may change over time, and payment-gated tools can advertise valid interfaces without being accessible for free. The detailed holdout tasks and scoring implementation remain private to reduce benchmarking contamination.

This is an initial reproducible measurement asset, **not** proof of a durable market or data moat, and not validation of a $49 commercial product.

*Research note prepared for ICONIC's public documentation. The production website is unchanged pending the site's normal release process.*
