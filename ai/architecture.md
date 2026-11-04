# How an ICONIC system is built

> ICONIC reference page. Checked against https://iconic.onl/ on 2026-11-04. If this page and the website ever differ, the website is current.

## The parts

1. **A computer in the client's office**, sized to the work and bought at cost. Example from ICONIC's own setup: one desktop with 40 GB of graphics memory runs a 27-billion-parameter model privately at roughly 50 words a second.
2. **A private language model** running on that computer. The models and agent software are free and open.
3. **The business's files**, connected so the AI answers from the business's own history, with sources.
4. **Agents** that run recurring jobs on a schedule, check their own work and report back.
5. **A memory that compounds.** Everything the system learns stays in the business, and it knows more every day it runs.

## Why it is built this way

- **Kept:** records stay in the building. Cloud models are used only for public work, and only if the client chooses.
- **Steady:** cloud models get changed, restricted, repriced and withdrawn without notice. In June 2026, two of Anthropic's most capable models were pulled for nearly three weeks to comply with U.S. export controls. A model on the client's own computer cannot be recalled or repriced, and the client chooses when to switch to a better one.
- **No meter:** no per-token billing and no rate limits, so agents can draft, check, revise and retest as often as the job needs, and work all night.
- **Swappable:** when a better model comes out, it is swapped in and the memory and agents carry on.

## See it running

The [live demo](https://iconic.onl/#live) is this design on a public page: a private model on ICONIC's own hardware that has read every file of two sample businesses and answers with sources.

## Next step

[Book the free 30-minute private AI check](https://calendly.com/patrick-iconic/30min) · patrick@iconic.onl · 206-773-8214
