# Cover Pitfalls

## Trim-Safe Text (text too close to the edge gets cut)

KDP prints the wrap larger than the finished book, then a blade trims it down.
Two things eat into the edges:

1. **Bleed** — the outer **0.125"** on every side is removed entirely.
2. **Cut drift** — the blade can wander another **~0.25"** in either direction.

So the practical safe margin is **0.375" (≈112 px at 300 DPI) from every cover
edge**. Any text inside that band can be shaved or sliced. All visible front and
back typography is baked into the generated artwork, so the prompt and visual
review must protect every title, subtitle, author, headline, tagline, badge, and
complete banner outline. The composer cannot pull baked text inward afterward
and must never repair it with a separate code overlay.

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

Bake the exact headline/tagline into the generated back artwork. Compose with
`--no-back-text`. Do not use `--headline`, `--feature-line`,
`--badge-top`, or `--badge-bottom`; visible cover typography must never be added
as a separate code layer.

## Preview Grid vs Barcode

Do not prompt a blank barcode box, but keep every preview card above
approximately 68-70% of panel height. Fill the bottom 25% with continuing
themed artwork so the deterministic barcode stamp does not cover a card border
or an important focal object. Always inspect the composed wrap.

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
