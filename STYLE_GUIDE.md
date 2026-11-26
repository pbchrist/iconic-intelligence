# ICONIC style guide (iconic.onl)

**Three views of one guide, all linked from one page:**

- **Visual guide (people):** https://iconic.onl/preview/style-guide/ shows the logo, colors, type at real size and the real components, with do/don't beside each.
- **Machine-readable source (AI tools):** [style-guide.yaml](style-guide.yaml), served at https://iconic.onl/style-guide.yaml. The visual page is built from it. **When this file and the YAML differ, the YAML wins.**
- **This file:** the same rules as plain text.

Patrick's rules for every page, button and line of copy. If Patrick says something newer, update style-guide.yaml (and this file) in the same commit.

Last updated 2026-11-26. Italics stay: Patrick rejected removing them on 2026-11-17.

## 1. Who the page is for

- **Reader:** a business owner who saw the WAC Magazine ad. They are busy, not technical, and skeptical of AI hype.
- **Job of every page:** say what they get, why it matters to their business, and the one next step.
- **One idea per page or section.** If a section makes a second argument, it belongs on another page (the ownership argument lives at /aipocalypse/).

## 2. Words

| Rule | Do | Don't |
|---|---|---|
| Plain English | "We work on it live, and you leave with something that works." | "Leverage agentic workflows to unlock value." |
| Present tense | "ICONIC tracks every truck." | "ICONIC will track every truck." |
| Outcomes, not features | "You see a rival's price cut the same day." | "Real-time competitive monitoring pipeline." |
| No em dashes | Use a period, comma or colon. | "One problem — one fix." |
| No hype words | "useful", "works", "pays back" | "magic", "genius", "revolutionary", "unlock" |
| "Connections", never "links", for what the AI learns | "It found 96 connections nobody told it." | "It found 96 links." |
| Never name the dealership client | "an auto dealership" | the dealership's name or city |
| Numbers stay true | "$4,472 price gap measured" | "$4,472 recovered" (unless it was) |
| No size or startup screens | "For business owners." | "For 10 to 200 people. Not for startups." |

## 3. Buttons and calls to action

- **One action, one name, everywhere.** Booking the call is always **BOOK THE FREE CALL**. Don't use variants like "Find your first fix", "Discuss", "Bring me your problem" or "Talk about your first problem".
- **No dollar signs or prices in button labels.** A price goes in the text next to the button, never on it.
  - Do: `SEE TRAINING` with "Workshops from $249" beside it.
  - Don't: `SEE THE $1,000 OFFER`.
- **One primary button per section, plus at most one secondary.**
- **Every button lands on a styled page that matches its label.** Never send a visitor to a raw .md, .txt or .json file. Click every button in a real browser before calling it done.
- **Each booking button opens the Calendly page,** and the Calendly title matches the offer named on the site.

## 4. Look

The site today: a dark ink page, pearl headlines, one lavender accent, flat dark panels with 1px hairlines, 12px button corners, 20 to 22px card corners. The free call panel ("BRING ONE PROBLEM.") is the reference: heavy flat caps sans, hard edges, one idea.

Current components, shown live at /preview/style-guide/: primary and ghost buttons, header and nav, eyebrow with the green live dot, small caps card labels, the offer panel, offer cards, step cards, quote block, evidence tags, text links.

**Not decided yet:** Patrick called the pulsing dot badge, caps eyebrows and serif-with-one-italic-word headlines part of the "Claude look" (2026-11-22). They stay documented as they are until he decides. Don't add a cream background; don't add new glows.

## 5. Type

| Use | Font | Size (desktop / phone) |
|---|---|---|
| Section headline | "Arial Black", Inter 900, Arial, sans-serif, or the Georgia serif headline. Italic accent lines are allowed. | clamp(40px, 5.7vw, 82px) / 37 to 54px |
| Subhead / intro | Inter, or Georgia for a long-form intro paragraph. | 17 to 20px |
| Body | Inter, Arial, sans-serif | 15px (phone 15px) |
| Fine print | Inter | 13px |

No new font sizes. Use the sizes above (the type-system branch sets the same scale for intros, body and fine print).

## 6. Color (tokens: styles.css :root, final values from mobile-first.css :root)

| Token | Value | Use |
|---|---|---|
| `--ink` | #070813 | Page background |
| `--ink-2` / `--ink-3` | #0b0d1a / #11152a | Panels |
| `--pearl` | #f3f0e7 | Headlines, primary button fill |
| `--muted` | #a8adc7 | Body text |
| `--accent` / `--accent-2` | #929cff / #c0c6ff | Links, italic accent lines, one highlight per screen |
| `--line` / `--line-strong` | pearl at 12% / 22% | Rules and borders |
| `--success` / `--danger` | #b9ffd2 / #ff9fba | Status only |

Use the tokens. Don't introduce a new hex value.

## 7. Code rules (from CLAUDE.md)

- **One design system.** Every size, color and spacing value comes from the shared tokens.
- **No per-page `<style>` blocks** and no inline `style=""` for anything visual. Fix the shared stylesheet instead.
- **Design changes go to /preview/ first.** They reach the live site only after Patrick says so.
- **Check at desktop (1440px) and phone (390px) widths.** There must be no sideways scroll and no overlapping text.

## 8. Keeping it true

`python3 scripts/check-style-guide.py` checks the YAML colors against the live CSS tokens. The visual page runs the same check in the browser and shows any mismatch in red.
