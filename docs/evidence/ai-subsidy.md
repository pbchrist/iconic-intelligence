# Evidence: is frontier AI inference subsidized?

Compiled 2026-11-13. Every link below was fetched on that date and the quoted figure was read on the page. Quotes are verbatim fragments. Nothing here is used in site copy yet.

Ratings used in the tables:

- **STRONG**: a primary statement (the company itself, its CEO, or its SEC filing) or a financial figure reported by a major outlet from company documents.
- **LIST-PRICE**: a number computed from API list prices. It measures what the usage would cost a customer at retail, not what the lab spends to serve it.
- **SECONDARY**: commentary, an analyst model, or a report of a report.

## 1. Read this first: what the evidence does not support

1. **No source states what a lab actually spends to serve a $200 subscriber.** The "$200 plan costs them $2,000" line cannot be cited as fact. The closest text is Tom's Guide calling "$2,000 of usage" on a $200 plan a "long-standing rule of thumb", which is usage at list price, not cost. The $8,000 and $14,000 figures are also list price, and Tom's Guide says so: "these are API-equivalent figures, not what the companies actually spend."
2. **Anthropic's June 15, 2026 move of automated work off flat plans did not take effect.** It was announced in May and paused on the day. The Decoder, 16 June 2026: "Anthropic has paused the billing overhaul it had announced for June 15, 2026." Do not cite it as a squeeze that happened. It can be cited as a squeeze that was announced and withdrawn.
3. **Anthropic reports an adjusted profit.** Its amended S-1 (2 November 2026) shows adjusted operating income for Q2 and Q3 2026, and the FT reports "$1.70 in revenue for every $1 spent on computing power" in Q3. A skeptic will lead with this.
4. **OpenAI's margin on paying users is reported at about 70%.** That is the share of revenue left after server costs for paying users, per The Information.
5. **No source found gives a date for a price jump or predicts a vendor collapse.**

What the evidence does support: the labs lose money overall, the heaviest subscription users get far more than they pay for at list price, three vendors have said in their own words that flat pricing was not covering cost, and the labs carry compute commitments in the hundreds of billions that must be paid regardless of usage.

## 2. Per-user cost versus plan price

| Rating | Claim | Source and date | Link |
|---|---|---|---|
| STRONG | OpenAI's CEO said the $200 ChatGPT Pro plan loses money. Altman: "I personally chose the price" "and thought we would make some money." The loss is TechCrunch's summary of his posts; no dollar amount is given. | TechCrunch, 5 January 2025 | https://techcrunch.com/2025/01/05/openai-is-losing-money-on-its-pricey-chatgpt-pro-plan-ceo-sam-altman-says/ |
| STRONG | Anthropic, in its own post on X: "one user consumed tens of thousands in model usage on a $200 plan." It added "a few outlying cases are very costly to support." This is one outlier, measured in model usage, not cost. | Simon Willison's Weblog quoting Anthropic, 28 July 2025 | https://simonwillison.net/2025/Jul/28/anthropic/ |
| LIST-PRICE | SemiAnalysis estimate: a $200 ChatGPT Pro plan used to its limit "could represent around $14,000 of compute a month if you bought the same volume through the API", "roughly 70 times the sticker price". "Claude's top tier lands near $8,000, about 40x." | Tom's Guide, 17 June 2026 | https://www.tomsguide.com/ai/the-math-doesnt-work-why-your-usd200-ai-subscription-is-secretly-worth-thousands |
| LIST-PRICE | Same SemiAnalysis estimate of where plans stop making money: "OpenAI starts losing money on its cheaper plans once a user crosses roughly 11.4% of the allowance", and on the top tier "the margin vanishes at around 5.7%." Anthropic breaks "even closer to 20% on lower tiers and about 10% at the top." These rest on an assumed 75% gross margin on API sales (stated by Gigazine, below). | Tom's Guide, 17 June 2026 | same link as above |
| LIST-PRICE | Corroboration of the same figures: "ChatGPT Pro 20x, which is also $200 monthly, has a maximum possible spend of around $14,000", described as "the approximate maximum possible spend (assuming API pricing)". | Tom's Hardware, 13 June 2026 | https://www.tomshardware.com/tech-industry/artificial-intelligence/ai-costs-spike-as-subscriptions-hit-pricing-wall-firms-turn-towards-chinese-llms-open-source-models-to-extend-budget |
| LIST-PRICE | Corroboration, and the assumption behind the breakeven figures: "assuming both companies have a 75% gross profit margin on APIs". | Gigazine, 12 June 2026 | https://gigazine.net/gsc_news/en/20260612-anthropic-openai-subscription-margin |
| SECONDARY | One Claude Code user "had been able to get the equivalent of more than $1,000 worth of API usage in a single day with the $200 per month Max plan" (LeadDev citing TechCrunch). A marketing lecturer quoted in the piece: "The cost for these AI coding platforms to the consumer has always been artificially low." | LeadDev, 27 August 2025 | https://leaddev.com/ai/the-great-ai-coding-assistant-bait-and-switch |
| SECONDARY | "those low-cost subscriptions are among the most heavily subsidized." Writer CEO May Habib: "These LLM companies are going to go public and they're going to raise prices because they have to". | Axios, "Don't get used to cheap AI". Date 12 March 2026 is taken from the URL; it was not in the fetched text. | https://www.axios.com/2026/03/12/ai-models-costs-ipo-pricing |

How to say it honestly: "A $200 plan run flat out delivers $8,000 to $14,000 of usage at the labs' own list prices (SemiAnalysis, June 2026)" is supportable. "The lab spends $2,000 on you" is not.

## 3. Lab losses and compute commitments

| Rating | Claim | Source and date | Link |
|---|---|---|---|
| STRONG | Anthropic 2025, from its leaked IPO filing: "losing $42 billion last year—while bringing in $4.6 billion in revenue." "Anthropic also spent $7.33 billion on computing and infrastructure last year, up threefold from 2024." "its operating loss widened to $8.06 billion from $2.98 billion a year earlier." Compute spend alone was about 1.6 times revenue. | Fortune, 29 September 2026 | https://fortune.com/2026/09/29/anthropic-leaked-ipo-prospectus-losses-growth-ai-end-humanity/ |
| STRONG | The same filing via Reuters. Caveat that must travel with the $42B: "The near-$42 billion net loss included a roughly $34 billion accounting charge." The cash-relevant number is the operating loss of about $8B. | Reuters, published in The Star, 29 September 2026 | https://www.thestar.com.my/tech/tech-news/2026/09/29/exclusive-anthropic039s-ipo-prospectus-shows-sweeping-ai-vision-surging-costs |
| STRONG | Commitments: "Anthropic expects to spend at least $518bn over a decade on infrastructure with six partners." "Anthropic cannot cancel about 80% of that sum, or must pay it whatever its usage, the filing says." On the Google deal, Anthropic wrote: "If our actual spend falls short, we must pay Google the difference". | The Next Web (reporting Reuters), 29 September 2026 | https://thenextweb.com/news/anthropic-ipo-prospectus-42bn-loss-518bn-compute |
| STRONG | The figure has since grown. Anthropic's amended S-1 states "aggregate committed spend of approximately $895.4 billion". Only the first third of the filing was read verbatim. | SEC filing, Anthropic S-1/A, filed 2 November 2026 | https://www.sec.gov/Archives/edgar/data/2130357/000162828026068676/anthropicpbc-sx1ax1.htm |
| STRONG | Anthropic Q3 2026: revenue of $16.956 billion and a "reported operating loss of $0.567 billion", after a Q2 operating profit of $0.974 billion. Compute and infrastructure expense was $9.863 billion in Q3, up from $5.558 billion in Q2. Figures are the article's reading of the S-1/A. | INDmoney, 3 November 2026 | https://www.indmoney.com/blog/us-stocks/anthropic-q3-results-breakdown-ahead-of-anthropic-ipo |
| STRONG | OpenAI: "OpenAI burned $3.7 billion during the first three months of 2026, The Information reported Tuesday (June 16)." "OpenAI had forecast it would burn through $25 billion this year and $57 billion in 2027." Source is company documents shared with investors. | PYMNTS, June 2026 | https://www.pymnts.com/?p=3859081 |
| STRONG | OpenAI raised its forecast: "cumulative cash burn to jump by roughly $111 billion more than previously estimated through 2030." "In total, OpenAI expects to spend $665 billion training and operating AI models." It "doesn't expect to become cash-flow positive until 2030." | The Decoder (reporting The Information), 21 February 2026 | https://the-decoder.com/openai-adds-111-billion-to-its-cash-burn-forecast-as-ai-costs-spiral-beyond-projections/ |
| SECONDARY | HSBC analyst model: OpenAI faces "a $207 billion funding shortfall that must be filled through additional debt, equity, or more aggressive revenue generation", and "OpenAI still won't be profitable by 2030." | Fortune, 26 November 2025 | https://fortune.com/2025/11/26/is-openai-profitable-forecast-data-center-200-billion-shortfall-hsbc/ |
| SECONDARY | "OpenAI is projected to burn $14 billion in 2026, up from $8 to $9 billion in 2025." Note this is lower than the $25B forecast above; the two reports use different documents. "Even with those discounts, OpenAI and Anthropic are still losing money." | Axios, 12 March 2026 (date from URL) | https://www.axios.com/2026/03/12/ai-models-costs-ipo-pricing |

## 4. Squeezes already visible

| Rating | What happened | Source and date | Link |
|---|---|---|---|
| STRONG | **GitHub Copilot ended flat request pricing.** GitHub's own words: "all GitHub Copilot plans will transition to usage-based billing on June 1, 2026." "GitHub has absorbed much of the escalating inference cost behind that usage" and "the current premium request model is no longer sustainable." This is the cleanest vendor admission found. | GitHub Blog, 27 April 2026 | https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/ |
| SECONDARY | The Register's reading of the same change: complex prompts "often cost GitHub more than the company earned in subscription fees." | The Register, 28 April 2026 | https://www.theregister.com/2026/04/28/microsofts_github_shifts_to_metered/ |
| STRONG | **Anthropic added weekly limits.** "We're rolling out new weekly rate limits for Claude Pro and Max in late August." Anthropic estimated they would "apply to less than 5% of subscribers". | Simon Willison's Weblog quoting Anthropic, 28 July 2025 | https://simonwillison.net/2025/Jul/28/anthropic/ |
| STRONG | Same event, press report: "Anthropic has introduced new weekly rate limits on its Claude Code tool". Extra usage for Max users is sold "at standard API rates." | Engadget, 28 July 2025 | https://www.engadget.com/ai/anthropic-is-rate-limiting-claude-code-blaming-some-users-for-never-turning-it-off-211134730.html |
| STRONG | **Cursor replaced 500 requests with $20 of usage.** "Instead of Pro users getting 500 fast responses on advanced AI models", "subscribers would now get $20 worth of usage per month, billed at API rates." CEO: "We recognize that we didn't handle this pricing rollout well and we're sorry". TechCrunch: "Cursor was eating those costs under its old Pro plan, but now it's passing them along to users." | TechCrunch, 7 July 2025 | https://techcrunch.com/2025/07/07/cursor-apologizes-for-unclear-pricing-changes-that-upset-users/ |
| STRONG, but announced only | **Anthropic announced separate credits for automated use, then paused it.** The May announcement: "programmatic usage is no longer subsidized by the general subscription pool" and is "restricted to a fixed, non-rollover monthly credit, also worth $20-$200 depending on your Claude plan." It followed an April 4, 2026 ban on using subscriptions to power third-party agents. | VentureBeat, 13 May 2026 | https://venturebeat.com/ai/anthropic-reinstates-openclaw-and-third-party-agent-usage-on-claude-subscriptions-with-a-catch/ |
| STRONG | The pause: "Anthropic has paused the billing overhaul it had announced for June 15, 2026." "The Agent SDK, `claude -p`, and third-party apps still draw from regular subscription limits, Anthropic says." The article adds: "The billing change may only come once Anthropic can offer tokens at lower prices." No later status was found. | The Decoder, 16 June 2026 | https://the-decoder.com/anthropic-backs-off-unpopular-billing-overhaul-as-price-war-with-openai-looms/ |
| SECONDARY | Enterprises are already reacting to cost. "One unnamed company even blew through $500 million in one month". Lindy moved to a cheaper open model that proved "as capable as Sonnet while costing ten times less" (the company's own claim, via WSJ). | Tom's Hardware, 13 June 2026 | https://www.tomshardware.com/tech-industry/artificial-intelligence/ai-costs-spike-as-subscriptions-hit-pricing-wall-firms-turn-towards-chinese-llms-open-source-models-to-extend-budget |

## 5. Price versus cost studies

| Rating | Claim | Source and date | Link |
|---|---|---|---|
| STRONG | Peer-level academic study (MIT authors). It cuts both ways. Price for a fixed level of benchmark performance falls "around 5x to 10x per year". But "the price of running frontier models is rising between 3x to 18x per year". The second half supports the thesis: staying at the frontier keeps getting more expensive. | arXiv 2511.23455, Gundlach, Lynch, Mertens, Thompson, submitted 28 November 2025, revised 23 March 2026 | https://arxiv.org/abs/2511.23455 |
| SECONDARY | "Frontier models are getting more expensive, not cheaper." "Per-token costs are falling. But total costs per task are rising." Anthropic's gross margin was "negative 94% last year" (2024), expected to reach 50% in 2025; no source cited for the Anthropic figures. | SaaStr, Jason Lemkin, 24 December 2025 | https://www.saastr.com/have-ai-gross-margins-really-turned-the-corner/ |
| SECONDARY | Open-model price comparison: DeepSeek-V4-Pro "usually costs around 1.74 per 1 million input tokens and $3.48 per 1 million output tokens with neutral vendors", against leading labs at "$2-5 per million input tokens, to $12-25 per million output tokens." The author uses this to argue API prices are above cost (see section 6). | LessWrong, Yair Halberstadt, 11 May 2026 | https://www.lesswrong.com/posts/Rz9ubmfyDxTzaoYFL/ai-companies-are-already-profitable-in-the-way-that-matters |

## 6. Counter-evidence a skeptic will cite

| Strength of the objection | Claim | Source and date | Link |
|---|---|---|---|
| Strong | **Anthropic is adjusted-profitable and compute is covered by revenue.** It "achieved adjusted profitability for a second consecutive quarter" and earned "$1.70 in revenue for every $1 spent on computing power during the third quarter". The article's own caveat: "adjusted profitability and positive cash flow do not necessarily establish profitability under standard accounting measures". | Yahoo Finance (reporting the Financial Times), 15 October 2026 | https://finance.yahoo.com/technology/ai/articles/anthropic-reports-45-revenue-growth-102235753.html |
| Strong | Q3 2026 adjusted operating profit of $2.463 billion at a 15% margin. "the adjusted result excludes stock-based pay and a large non-cash donation-matching charge." The GAAP result for the same quarter was the $0.567 billion operating loss in section 3. | INDmoney, 3 November 2026 | https://www.indmoney.com/blog/us-stocks/anthropic-q3-results-breakdown-ahead-of-anthropic-ipo |
| Strong | **OpenAI makes money on the compute for paying users.** Compute margin "jumped from around 35 percent in January 2024 to roughly 70 percent by October 2025." Defined as "the share of revenue left after paying for server costs from paying users." It excludes free users and training. "Anthropic is expected to reach 53 percent by year's end." | The Decoder (reporting The Information), 22 December 2025 | https://the-decoder.com/openai-reportedly-dramatically-improved-its-compute-profit-margins/ |
| Strong | Same report: "As of October, that margin came to 70%", "up from 52% at the end of 2024". | PYMNTS, 21 December 2025 | https://www.pymnts.com/artificial-intelligence-2/2025/openai-compute-margin-doubles-over-nearly-two-years/ |
| Strong | **Inference keeps getting cheaper.** "For an LLM of equivalent performance, the cost is decreasing by 10x every year." "The cost of LLM inference has dropped by a factor of 1,000 in 3 years." Author's caveat: "its rate may slow down." | a16z, Guido Appenzeller, 12 November 2024 | https://a16z.com/llmflation-llm-inference-cost/ |
| Strong | "the price to achieve GPT-4's performance on a set of PhD-level science questions fell by 40x per year." Range "from 9x to 900x per year." | Epoch AI, 12 March 2025 | https://epoch.ai/data-insights/llm-inference-price-trends |
| Medium | Independent estimate that API prices are far above raw compute cost: "$3/15 per million tokens vs ~$0.01/3 actual costs", "80-95%+ gross margins", and Claude Max plans priced at a markup over cost. The author: "This is really napkin math. I don't have any experience at running frontier models at scale." Uses an open model as a proxy and ignores training. | Martin Alderson, 27 August 2025 | https://martinalderson.com/posts/are-openai-and-anthropic-really-losing-money-on-inference/ |
| Medium | "the marginal cost to respond to an AI API call is significantly lower than the price of that call." Covers serving cost only, not training or infrastructure. | LessWrong, Yair Halberstadt, 11 May 2026 | https://www.lesswrong.com/posts/Rz9ubmfyDxTzaoYFL/ai-companies-are-already-profitable-in-the-way-that-matters |
| Medium | Axios's own bottom line: "The costs of AI will keep going down." Token pricing "has fallen, partly due to a massive efficiency jump in inference." | Axios, 12 March 2026 (date from URL) | https://www.axios.com/2026/03/12/ai-models-costs-ipo-pricing |
| Medium | Anthropic backed off a price squeeze under competitive pressure (section 4), and Gigazine reports, citing the WSJ, that OpenAI is considering lowering token prices. Competition is currently pushing prices down, not up. | The Decoder, 16 June 2026; Gigazine, 12 June 2026 | links in sections 2 and 4 |

## 7. The position that survives a skeptic

- API inference sold at list price to paying customers appears to be profitable at the compute level. Saying "all inference is sold below cost" will lose the argument.
- The subsidy that is documented sits in three places: flat-rate plans for heavy users (Altman, Anthropic, GitHub and Cursor have each said so in their own words), free users, and the training and infrastructure bill that revenue does not yet cover (OpenAI's $25B forecast burn for 2026, Anthropic's GAAP operating loss in Q3 2026).
- The pressure that could force prices up is the fixed commitments: $895.4 billion at Anthropic per its S-1/A, about 80% of the earlier $518 billion non-cancellable, and $665 billion of planned model spend at OpenAI through 2030.
- The evidence that the frontier itself is getting more expensive to use, even while old capability gets cheaper, is the arXiv study: frontier running price "rising between 3x to 18x per year".

## 8. Sources that failed to load and were left out

- CNBC, 15 October 2026, on Anthropic's Q3 revenue: client error.
- Quartz, on the same: client error.
- exchange4media, on the same: client error.
- TechSpot's SemiAnalysis write-up and devops.com's report on the June 15 pause both loaded, but the fetched text carried no publication date, so their claims are cited from dated sources instead.
- SemiAnalysis's original report was not fetched; its figures are cited as reported by Tom's Guide, Tom's Hardware and Gigazine.
