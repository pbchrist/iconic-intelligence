# ICONIC style guide (iconic.onl)

Patrick's rules for every page, button and line of copy. If this file and an older note disagree, this file wins. If Patrick says something newer, update this file in the same commit.

Last updated 2026-11-26.

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

## 4. Look: no "Claude look"

| Don't | Do instead |
|---|---|
| Serif headline with one word in colored italic ("Move *first.*") | One weight and one color for the whole headline |
| Italic second line on headings ("START SMALL. *GO FURTHER*") | A single plain headline line, or a plain subhead under it |
| Dot or pill badges ("● PRIVATE BY DESIGN") | No badge. If a label is needed, use plain text. |
| Tiny letter-spaced caps labels on every block ("01 · LEARN IT") | At most one small label per section, only when it helps |
| Glows, glassy cards, soft gradients | Flat panels, hard 1px rules, solid fills |
| Rounded pill buttons | Square or near-square buttons (0 to 4px radius) |
| Cream background | The dark ink background below |

The "ONE PROBLEM." / "BRING ONE PROBLEM." panel is the reference: heavy flat caps sans, hard edges, one idea.

## 5. Type

| Use | Font | Size (desktop / phone) |
|---|---|---|
| Section headline | "Arial Black", Inter 900, Arial, sans-serif. Caps allowed, never italic. | clamp(40px, 5.7vw, 82px) / 37 to 54px |
| Subhead / intro | Inter. Georgia only for a long-form intro paragraph, never italic. | 17 to 20px |
| Body | Inter, Arial, sans-serif | 15px (phone 15px) |
| Fine print | Inter | 13px |

No new font sizes. Use the sizes above (the type-system branch sets the same scale for intros, body and fine print).

## 6. Color (tokens in styles.css :root)

| Token | Value | Use |
|---|---|---|
| `--ink` | #070912 | Page background |
| `--ink-2` / `--ink-3` | #0b0e1b / #10152a | Panels |
| `--pearl` | #f3f0e7 | Headlines, primary button fill |
| `--muted` | #a8adc7 | Body text |
| `--accent` | #8d98ff | Links, one highlight per screen |
| `--line` / `--line-strong` | pearl at 12% / 22% | Rules and borders |
| `--success` / `--danger` | #b9ffd2 / #ff9fba | Status only |

Use the tokens. Don't introduce a new hex value.

## 7. Code rules (from CLAUDE.md)

- **One design system.** Every size, color and spacing value comes from the shared tokens.
- **No per-page `<style>` blocks** and no inline `style=""` for anything visual. Fix the shared stylesheet instead.
- **Design changes go to /preview/ first.** They reach the live site only after Patrick says so.
- **Check at desktop (1440px) and phone (390px) widths.** There must be no sideways scroll and no overlapping text.

## 8. Where the live site still breaks this guide (2026-11-26)

1. The hero "Move *first.*" has an italic accent word and a dot badge.
2. Most section headings have an italic lavender second line.
3. There are caps labels on nearly every card.
4. The cards are rounded, glassy and glowing.
5. The live homepage has "$1,000" in button labels and about six names for the booking button. The /preview/ page fixes this one.

These need Patrick's go-ahead before anyone fixes them.
