# ICONIC pay-per-crawl x402: edge adapter (not activated)

**Current infrastructure, verified 2026-11-16:** iconic.onl is hosted on GitHub Pages and resolves through Namecheap's registrar nameservers, **not Cloudflare**. GitHub Pages cannot execute request middleware or emit conditional 402 responses. This Worker is a deployable adapter **after** an edge proxy is installed. Committing this folder does not turn on charging or change production traffic.

## What it does

- Handles only GET requests under `/research/`, excluding the research index, static assets, and discovery files.
- Keeps real visitors and AI *search/answer* crawlers free: Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User, Applebot, DuckAssistBot.
- In charge mode, challenges four known training crawler user agents: GPTBot, ClaudeBot, CCBot, Bytespider. No anonymous-IP guessing.
- Proxies paid retries to the AIPayGen x402 gateway, which is responsible for verifying payment, fetching the original page with the configured bypass secret, and settlement. ICONIC's Worker must never trust a payment header by itself.
- Requests with the matching gateway secret pass to the original GitHub Pages site to avoid recursion.
- `AIPAYGEN_MODE=observe` writes crawler/path entries to Worker logs and forwards requests unchanged. `off` forwards everything unchanged.
- `charge` requires BOTH `AIPAYGEN_GATEWAY_ID` and `AIPAYGEN_SECRET`. If either is missing, the Worker forwards requests unchanged; it will never claim that charging is active.
- If the payment gateway fails, charged crawler requests get 503; human and search access still uses the origin. Redirects from the gateway are refused.

## Activation prerequisites

1. Move iconic.onl traffic behind an edge proxy. Cloudflare Worker routes require an active Cloudflare zone. **Preserve all current apex/WWW, mail MX, SPF, DKIM, DMARC, and business verification TXT records before changing nameservers.** Recheck HTTPS, Gmail routing, GitHub Pages, and the live Qwen demo. This repo alone cannot migrate DNS and has no Cloudflare account credentials.
2. Register a gateway at https://aipaygen.com/pay-per-crawl. Choose `https://iconic.onl` as the upstream, a USDC-on-Base **receiving** address that ICONIC controls, and `$0.002` per page as an initial price. The resulting gateway route ID is public; the gateway secret and API key are confidential. Validate the provider and its settlement policy before accepting real payments.
3. From this folder, create `wrangler.toml` from `wrangler.toml.example`. With a Cloudflare-authenticated Wrangler CLI, set `AIPAYGEN_SECRET` via `npx wrangler secret put AIPAYGEN_SECRET`, then deploy in `observe` mode and verify that origin and search crawlers still receive 200.
4. Test a GPTBot request in `charge` mode for a research article: expect HTTP 402 with a Payment-Required challenge. An x402 client with a properly funded wallet must produce a confirmed receipt, and a paid retry must return the original content. Verify the receiver wallet balance and duplicate-replay behavior. Do not claim receipts before this test.
5. Switch `AIPAYGEN_MODE` from `observe` to `charge` only after successful tests. Retain the original Namecheap DNS snapshot and a rollback plan.

AIPayGen currently reports that major model-company crawlers have not paid its site; use a pilot, not projected revenue, to evaluate results. Some agents can pay using x402 or a prepaid paid_fetch tool. User-agent spoofing and alternative content fetching remain possible; this is not a DRM system. The paid gateway is a third party.

## Verify

`node --test ops/pay-per-crawl/worker.test.mjs`

Live checks once installed:

```sh
curl -I https://iconic.onl/robots.txt
curl -i -A 'OAI-SearchBot' https://iconic.onl/research/dealership-pricing-intelligence/
curl -i -A 'GPTBot' https://iconic.onl/research/dealership-pricing-intelligence/
curl -i -A 'Mozilla/5.0' https://iconic.onl/research/dealership-pricing-intelligence/
```

**Expected:** discovery and ordinary visitors remain free; AI search bots remain free; targeted training crawlers get 402 only in charged mode. Because anyone can claim a user agent, these are functional checks, not a proof of crawler identity.

**Do not install generic AIPayGen crawler regexes unchanged.** Its example charges OAI-SearchBot and ChatGPT-User, which would cut ICONIC's AI answer/search access. Keep the short targeted list until crawl analytics justify broadening it.

## No live change in this commit

No DNS changes, no wallet creation, no registration with AIPayGen, no vendor secrets or payment, no alteration to robots.txt, no production Worker deployment.
