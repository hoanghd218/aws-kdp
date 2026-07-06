# Cover Pitfalls

## Trim-Safe Text (text too close to the edge gets cut)

KDP prints the wrap larger than the finished book, then a blade trims it down.
Two things eat into the edges:

1. **Bleed** — the outer **0.125"** on every side is removed entirely.
2. **Cut drift** — the blade can wander another **~0.25"** in either direction.

So the practical safe margin is **0.375" (≈112 px at 300 DPI) from every cover
edge**. Any text inside that band can be shaved or sliced. The compose script's
code overlays (back headline, feature line, badge, barcode) already honor the
`SAFE_MARGIN = 0.375"` from `scripts/generate_cover.py`. The risk is the
**front cover title/subtitle/author**, because those are baked into the AI
artwork — the script cannot pull them inward after the fact.

Fix it in the prompt, every single time: tell `image_gen` to leave a wide empty
margin on all four sides and keep all type inside the central ~80% of the panel,
with nothing important near an edge. Then verify in the rendered PNG before
delivery — if a letter is within ~0.375" of an edge, re-generate that panel.

## Prompt-Generated Barcode Zones

Do not ask `image_gen` to leave a blank barcode/stamp area. Models create the
wrong size, the wrong position, or several boxes. Generate full edge-to-edge
artwork, then let the compose script stamp exactly one white barcode zone
(2.0in × 1.2in, bottom-right of the back, inside the safe margin) by code.

## Back Cover Text

For stable headline / feature / badge text, prefer the code overlays
(`--headline`, `--feature-line`, `--badge-top/--badge-bottom`) — they stay crisp
and land inside the safe margin. Use AI-rendered text only when the user
explicitly wants it as part of the illustration.

## Page Count

Use the `interior.pdf` page count when available — it drives the spine width.
Counting `images/page_*.png` can be wrong when frontmatter pages were added or
backup files match the glob.

## Spine Text

Add spine text only when the spine is wide enough (79+ pages) and the user asks.
For thin books a plain blended spine is safer; a hairline of mis-registered spine
text reads as a defect.

## Color Mode (RGB vs CMYK)

KDP prints in CMYK and recommends CMYK files with no embedded color profile. The
compose script outputs RGB; KDP accepts it and auto-converts, but neon/vivid RGB
and pure black can shift on press. Acceptable for coloring-book covers — just set
expectations and don't promise screen-exact print color.

## Flatten / Transparency / Fonts (handled by construction)

Unflattened transparency, crop marks, and unembedded fonts are common KDP reject
reasons. The script rasterizes the whole wrap to one flat image embedded in the
PDF, so none of these can occur — there is nothing extra to do here.

## File Size

Keep the cover PDF ≤ 40 MB (KDP recommendation; 650 MB hard limit). A full-bleed
300-DPI PNG can exceed 25 MB; if the PDF is huge, re-export with JPEG compression
or regenerate the art slightly smaller rather than uploading a giant file.

## Spine Text vs Spine Width (page-count rule wins)

KDP allows spine text only at **79+ pages**, regardless of how wide the spine
looks. Do not gate spine text on spine width alone — a 56–78 page book can have a
wide-enough spine yet still be rejected for spine text. The script avoids this by
never drawing spine text by default.

## Existing Assets

The compose script backs up `cover.pdf`, `cover.png`, `front_artwork.png`, and
`back_artwork.png` into `output/<theme>/backups/` before overwriting. Keep the
original `image_gen` outputs around and copy the selected ones into the project.
