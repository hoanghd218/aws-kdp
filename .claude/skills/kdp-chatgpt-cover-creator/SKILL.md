---
name: kdp-chatgpt-cover-creator
description: Create a KDP-ready coloring book cover (PNG + PDF) using the ChatGPT image renderer (image_providers.generate_image renderer=chatgpt) for front/back artwork, then deterministic Python composition for spine, back-cover text, barcode safe zone, bleed, DPI, and exact KDP page size. Fully automated — no manual steps. USE WHEN user says 'tao bia chatgpt', 'chatgpt cover', 'kdp cover with chatgpt', 'tao bia sach bang chatgpt', 'make kdp cover', 'rebuild cover', 'fix cover', 'regenerate cover', or asks to build/redo a KDP wrap cover.
---

# KDP ChatGPT Cover Creator

Build a full-wrap KDP paperback cover (back + spine + front) from artwork made
with the **ChatGPT image renderer** (`image_providers.generate_image(renderer="chatgpt")`),
while keeping every fragile production detail — cover math, bleed, DPI, PDF size,
barcode safe zone, spine blend, and back-cover text overlays — in deterministic Python.

**Flow:** Claude writes the prompts → Claude generates front/back art via the `chatgpt`
renderer Python script → Claude composes the wrap with
`.claude/skills/kdp-chatgpt-cover-creator/scripts/compose_chatgpt_cover.py` →
Claude QCs the PDF. No manual hand-off, no user intervention needed.

---

## Two rules that prevent the two most common rejects

**1. Keep ALL text away from the outer edge — the blade cuts ~0.375" in.**
KDP prints the cover slightly larger than the book, then trims it. The outer
0.125" is bleed (cut off entirely) and the printer can drift another ~0.25", so
**any letter within 0.375" of a cover edge can be sliced or shaved off.** This is
the user's #1 concern. Because the front title/subtitle/author are *baked into
the AI artwork*, the only place to enforce it is the prompt: demand a generous
empty margin of "breathing room" around every word, with nothing important near
the four edges. Code overlays on the back (headline/badge/feature line) already
respect the 0.375" safe margin automatically — but the AI-generated front does not
unless you say so, every time.

**The margin language that actually works (paste into every front prompt):**
> keep EVERY letter, badge, ribbon, speech bubble and preview card ENTIRELY inside
> the central ~75% of the panel; leave a WIDE empty margin of ≥15% of the panel on
> ALL FOUR edges and in ALL FOUR CORNERS, filled only with background glow/sparkles/
> confetti; pull any upper-corner badges (e.g. "NEW 2026", a starburst) well INWARD
> away from the corners; place the author name well above the bottom with a large
> empty band (≥16% of panel height) of plain background BELOW it.

The two recurring failures, both fixed by the wording above:
- **author name / bottom ribbon too low** → it gets shaved at the bottom. Demand the
  empty band below it.
- **corner badges ("NEW 2026", starburst) touching a corner/edge** → demand they sit
  inward. The image model copies reference covers that put these flush to the corner;
  you must explicitly override that.

**A third failure mode, just as common: "empty margin" gets taken too literally.**
If the prompt says "leave the bottom clear" or "nothing below the author name except
plain background," the model sometimes renders a big flat, undecorated color block —
looks broken/cheap, not like a margin (compare against `butterfly_collection` or
`cottagecore_frogs`, where the illustrated scene — rug, snow, floor, garden path —
visibly continues all the way to the edge, with the author name layered ON TOP of
that continuing art, not on empty space). Say it explicitly: *"artwork/decoration
must fill the entire panel edge to edge, no flat empty background areas — the author
name sits on top of the continuing illustration."* Also don't over-correct on the
edge-safety side: telling the model to push the author name down to ~85-90% of the
panel height (to "use the space") frequently overshoots and drops it below the red
safe line entirely. Target a baseline around 70-75% down the panel, not lower.

**A fourth failure mode: banning all styling on the author name to "play it safe"
makes it look cheap and pasted-on.** Don't tell the model to render the author name
as flat plain unstyled text — that reads as broken/inserted, not baked-in art
(compare a plain black sans-serif "BoBo Art" against `butterfly_collection`'s
matching-font, small-heart-accented version — the plain one looks like a code
overlay even when it isn't). Instead say: *"the author name is styled to MATCH the
title's lettering (same font family and a complementary color), with ONE small,
compact decorative accent (a tiny heart/leaf/paw print, no more than a few percent
of panel height tall) directly beside or just below it — the name AND its accent
together must end by ~78-80% of panel height, well clear of the safe line."*
Banning the accent entirely just trades an edge-safety bug for a visual-quality bug;
constraining its size is what actually fixes both.

**A fifth failure mode: the title banner's own shape can cross the edges even when
the lettering doesn't.** Ribbon-style banners often have raised "flag" ends or
curled corners that sit higher/wider than the flat center where the text lives — a
prompt that only constrains the *text* position can still produce a banner outline
that pokes into the top or side margins. Say explicitly: *"the ENTIRE title text
including the widest word fits within the central ~72% of panel width, with visible
margin on both left AND right of the banner — shrink the font as needed"* AND *"the
banner's outline itself, including any raised ribbon-end/curl at its corners — not
just the flat center — starts no higher than ~10-12% down from the top edge."*

**Always check a zoomed crop, not just the full-panel overview.** After every
compose, `check_cover_safezone.py`'s printed ink-% flags an outlier edge, but the
full `cover_safe_check.png` thumbnail is too small to see a marginal crossing.
Crop the flagged edge(s) with PIL (e.g. bottom-center for the author name, or the
top-left/top-right corners for a wide banner) and Read the crop before deciding
it's clean.

**Always verify after composing** — the compose script auto-writes
`output/<theme>/cover_safe_check.png` (green trim line, red text-safe line) and prints
per-edge ink %. OPEN it and confirm no text crosses the red line (decoration crossing
it is fine). If text crosses, re-roll the front with the margin wording above — do not
ship it.

The official KDP number is **0.25" inside the trim line**; since the trim line
sits 0.125" inside the full-wrap PDF edge, that equals **0.375" from the PDF
edge** — which is exactly the `SAFE_MARGIN = 0.375"` the compose script uses.

**2. Never ask the image model to leave a blank barcode/stamp box.**
Models place it at the wrong size, in the wrong spot, or draw several. Generate
full edge-to-edge artwork, then let the compose script stamp exactly one
white barcode zone into the back cover by code.

---

## Workflow

### 1. Read the book context
- `output/<theme>/plan.json` — `title`, `subtitle`, `author`, `audience`,
  `page_size` (8.5x11 → portrait 3:4 front; 8.5x8.5 → square 1:1 front).
  **If `cover_prompt` and `back_cover_prompt` already exist in plan.json AND the
  front prompt already bakes in the title as text, use them verbatim** — the
  current plan-writing skills emit both in the detailed "ads-marketing" format
  below, with an explicit `Text (verbatim): "<title>"; ...` clause.
  **Do not trust an existing `cover_prompt` on sight — check it for a baked
  title first.** Older `plan.json` files (written before the baked-text
  convention) often hold a plain scene-only prompt with no title/subtitle/author
  text at all, or explicitly say "DO NOT include any text" — reusing one of
  those verbatim silently ships an off-brand, textless cover that doesn't match
  the rest of the catalog (compare any such cover against `butterfly_collection`
  or `cottagecore_frogs`, which do bake in the title). Treat a `cover_prompt`
  that lacks baked title text as **stale, not present** — rewrite it following
  the pattern below and save the corrected prompt back into `plan.json` so the
  fix persists. Only ship a textless cover when the user explicitly asks for one
  for this specific book.
- `output/<theme>/interior.pdf` — the real page count drives spine width; trust
  this over counting `images/page_*.png`.
- existing `output/<theme>/cover.png` if you are fixing an old cover.
- Read `scripts/generate_cover.py` / `scripts/kdp_config.py` only if a dimension
  or barcode convention is unclear.

### 2. Get the FRONT and BACK prompts

Prefer `plan.json.cover_prompt` (front) and `plan.json.back_cover_prompt` (back)
if present **and the front prompt already bakes in the title as text** (see the
staleness check in step 1). Otherwise write them following the patterns below.

**Front** — one panel matching `plan.json.page_size` (portrait `3:4` for 8.5×11,
square `1:1` for 8.5×8.5):
- **Bake the title/subtitle/taglines/author INTO the art** (marketplace-ready —
  this is the default for these covers, it sells far better than a plain
  illustration). Spell every word EXACTLY (author names like `BoBoArt` garble
  easily). Only skip baked text on explicit request.
- **Keep all text inside the safe zone** — see Rule 1.
- No barcode, ISBN, QR code, watermark, or blank boxes. Full-bleed art edge to edge.

**Back** — complete decorative panel, full-bleed, no barcode placeholder:
- Use a **2×3 grid of six sample preview cards** showing the book's actual scenes.
- **Match the card shape to `page_size`:** square book (8.5×8.5) → the six cards
  must be **square (1:1)**, same size, evenly spaced; portrait book (8.5×11) →
  portrait cards.
- **Top row = 3 fully COLORED finished examples** (shows the buyer the colored
  result), **bottom row = 3 black-and-white line-art previews** (the real coloring
  pages). This before/after split is a proven KDP back-cover layout.
- **Bake in a short headline/tagline near the top of the panel**, above/around
  the grid (e.g. "See What's Inside!" or a theme-specific line) — a fully
  text-free back cover reads as less compelling; a little selling copy on the
  back increases appeal. Keep it short, on-brand, and inside the same safe
  margins as the front (≥15–18% from every edge, nothing in the bottom strip).
- Surround the grid with on-theme decorations.
- Because all text (front + back headline) is baked into the AI art, **compose
  with `--no-back-text`** (the barcode zone is still stamped automatically) —
  the code overlay flags (`--headline` etc.) are only for the rare case where
  the back art was deliberately generated with empty reserved space for them.

### 3. Generate both artworks with the `chatgpt` renderer

Run this Python snippet directly. It reads the prompts straight from `plan.json`
(falls back to inline prompts if those keys are missing) and picks the aspect
ratio from `page_size` — `"1:1"` for 8.5×8.5, `"3:4"` for 8.5×11. A square book
returns ~1254×1254 square panels, so the six back-cover cards and any baked-in
front text are never cropped.

```python
import sys, json; sys.path.insert(0, "scripts")
from dotenv import load_dotenv; load_dotenv(".env")
from image_providers import generate_image

THEME = "<theme>"
plan = json.load(open(f"output/{THEME}/plan.json", encoding="utf-8"))
ASPECT = "1:1" if plan.get("page_size") == "8.5x8.5" else "3:4"
FRONT_PROMPT = plan["cover_prompt"]
BACK_PROMPT  = plan["back_cover_prompt"]

front = generate_image(FRONT_PROMPT, renderer="chatgpt", aspect_ratio=ASPECT)
if front: front.save(f"output/{THEME}/front_artwork.png")

back = generate_image(BACK_PROMPT, renderer="chatgpt", aspect_ratio=ASPECT)
if back:  back.save(f"output/{THEME}/back_artwork.png")
```

If a render is garbled or off-style, re-run the snippet for just that panel.
Never ask the user to save the files manually — generate them automatically.

### 5. Compose the wrap

Default — front text baked in, self-contained back grid, so `--no-back-text`
(barcode is still stamped):
```bash
python .claude/skills/kdp-chatgpt-cover-creator/scripts/compose_chatgpt_cover.py \
  --theme <theme> \
  --front output/<theme>/front_artwork.png \
  --back  output/<theme>/back_artwork.png \
  --no-back-text
```
The script reads page count from `interior.pdf`, computes spine + bleed + full
dimensions, resizes the panels, blends the spine, stamps one barcode zone
bottom-right, and writes PNG + PDF at 300 DPI. Existing cover files are backed up
to `output/<theme>/backups/` first.

Only if the back art was made with deliberate empty space for code text, add the
overlays instead of `--no-back-text`:
```bash
  --headline "A SUPER CUTE|COLORING ADVENTURE" \
  --feature-line "36 bold and easy pages for ages 3-7" \
  --badge-top "BIRTHDAY PARTY" --badge-bottom "Coloring Book"
```
If KDP shows an exact required wrap size in the upload dialog, pass
`--kdp-width` and `--kdp-height` to match it precisely.

### 6. Color, flattening & file size (KDP print rules)

The compose script rasterizes everything to **one flat image** embedded in the
PDF — so transparency, layers, crop marks, and unembedded fonts (all common
reject reasons) are impossible by construction. Two things still need attention:

- **Color mode.** KDP prints in **CMYK** and recommends CMYK files with no
  embedded color profile. The script outputs **RGB**; KDP accepts RGB and
  auto-converts, but very vivid/neon RGB and pure blacks can shift on press.
  For coloring-book covers this is normally fine — just expect slightly muted
  print colors, and don't promise the author screen-exact color.
- **File size.** Keep the cover PDF **≤ 40 MB** (KDP's recommendation; hard limit
  650 MB). A full-bleed 300-DPI PNG can balloon past 25 MB — if it does, regen
  the artwork a touch smaller or re-export the PDF with JPEG compression rather
  than uploading a 200 MB file.
- **Spine text = 79+ pages, no exceptions.** Below 79 pages KDP rejects any spine
  text. The script never draws spine text (it blends a clean spine), so the
  default is always safe — only add spine text on an explicit request for a
  79+ page book, and keep 0.0625" clearance each side.
- **Legibility.** KDP rejects illegible / low-contrast text. Keep front title
  and back copy high-contrast against the art behind them.

### 7. Validate before delivery
```bash
python scripts/pdf_qc.py --pdf output/<theme>/cover.pdf --cover \
  --expected-width <full_width_in> --expected-height <full_height_in>
# Safe-zone overlay (compose already wrote it; re-run any time):
python scripts/check_cover_safezone.py <theme>
```
Then READ `output/<theme>/cover_safe_check.png` and confirm visually:
- [ ] No title / subtitle / author / badge letter crosses the RED text-safe line
      (decorative art crossing it is fine). This is the #1 reject — never skip it.
- [ ] Front text spelled correctly and matches `plan.json` + interior title page.
- [ ] Back cover has one clean barcode zone, no AI-drawn blank box or stray text.
- [ ] Spine blend is clean; spine text only if 79+ pages and the user asked.
- [ ] PDF size matches the KDP-required wrap dimensions, ≥300 DPI.
- [ ] Cover PDF ≤ 40 MB; one flat layer, no transparency/crop marks.
- [ ] Text is high-contrast and legible against the art behind it.

---

## Prompt patterns

These are the proven "ads-marketing" patterns the plan-writing skills now emit
into `plan.json` as `cover_prompt` / `back_cover_prompt`. Reuse them when writing
prompts by hand.

**Front cover** — bake all text into the art:
```text
Use case: ads-marketing. Asset type: Amazon KDP <square|portrait> coloring book FRONT
COVER artwork, <8.5 x 8.5|8.5 x 11> inch front panel with bleed-safe composition.
Primary request: a complete full-color front cover illustration for a <audience> coloring
book. All cover text must be generated as part of the image artwork, not added later.
Scene/backdrop: <setting, mood, palette>.
Subject: <main kawaii character + props>.
Style/medium: polished professional <audience> coloring book cover, cute kawaii cartoon,
<palette>, soft clean outlines, marketplace-ready.
Composition/framing: <square|portrait> cover. Big readable title at the top on a soft banner.
Subtitle stacked below, not covering the subject. Small rounded badges for taglines.
Subject centered lower-middle. Author name at bottom center.
Text (verbatim): "<title>"; "<subtitle>"; "<tagline1>"; "<tagline2>"; "<author>".
Spell author exactly <spelled out>.
Constraints: all text part of the image; keep all text inside safe margins with generous
padding from every edge; no barcode; no mockup; no watermark; no publisher marks.
Avoid: misspelled/distorted letters, cropped title, text near the edges, realistic photo.
```

**Back cover** — 2×3 grid, top row colored, cards match book shape:
```text
Use case: ads-marketing. Asset type: Amazon KDP <square|portrait> coloring book BACK COVER
artwork, <8.5 x 8.5|8.5 x 11> inch back panel.
Primary request: a complete decorative back cover with NO blank barcode area and NO empty
white rectangle.
Scene/backdrop: <on-theme background texture + decorations> covering the entire page.
Subject: a tidy 2 by 3 grid of six <SQUARE for 8.5x8.5 | portrait for 8.5x11> sample preview
cards, all the same size and evenly spaced. The TOP ROW of three cards are fully COLORED
finished examples in <palette> (show how a colored page looks). The BOTTOM ROW of three cards
are clean black-and-white line-art coloring-page previews. Surround the cards with on-theme
decorations and a kawaii animal near the lower area.
Composition/framing: keep cards inside safe margins; fill the lower-right with normal
decoration (do not reserve blank space — the barcode is stamped by code).
Constraints: cards must match the book shape (square for a square book), same size; top three
colored, bottom three line art; no title/author text; no barcode; no white rectangle; no blank
stamp area anywhere.
Avoid: rectangular cards on a square book, uneven cards, stray text, blank boxes, busy clutter.
```

---

## References

- `references/cover-pitfalls.md` — the recurring failure modes (trim-safe text,
  prompt-generated barcode boxes, page-count source, spine text, backups). Read
  it the first time you build or fix a cover.
