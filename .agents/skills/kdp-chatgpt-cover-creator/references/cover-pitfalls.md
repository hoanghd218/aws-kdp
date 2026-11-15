# Cover Pitfalls

## Trim-Safe Text (text too close to the edge gets cut)

Separate the background bleed from content safety. Background illustration extends
0.125 inches beyond the trim on the outside edges. KDP requires front/back text
at least 0.125 inches inside the trim, with no text extending into the spine.
Use the book's KDP template to check important image placement too.
Source: https://kdp.amazon.com/en_US/help/topic/G201953020

Prompt for roughly 5-7% panel-edge clearance around lettering, text-bearing
banners/badges, and important subjects as a practical generation target, then
verify the final physical dimensions. This percentage is not an Amazon rule.
Background scenery and expendable decorations should reach all edges.
Do not impose central 72-75% placement or a fixed author height on every design.

If text or a focal subject is too close to the edge, revise the prompt or make a
targeted imagegen edit to that element. Preserve the approved full-bleed scene.
Never shrink the complete panel, add blurred/mirrored padding, or crop inward.
The diagnostic checker's default 0.375-inch margin is conservative; use an
explicit `--safe-in 0.125` for the minimum text check. Decorative ink in a margin
is not proof that text is unsafe. Inspect the actual lettering and focal subjects.
Never repair generated typography with a code overlay.

## Prompt-Generated Barcode Zones

Do not prompt image generation to leave a blank barcode/stamp area. Models often create the wrong size, position, or multiple blank boxes. Generate full artwork, then cover the barcode area in code.

## Back Cover Text

Bake the exact headline/tagline into the generated back artwork. Compose with
`--no-back-text`. Headline, feature, badge, title, subtitle, and author overlay
flags are forbidden because they create a cover assembled from separate text.

## Preview Grid vs Barcode

The generated back artwork must not reserve a white barcode box, but the preview
grid still needs to avoid the deterministic barcode zone. Keep every card above
approximately 68-70% of panel height and fill the bottom 25% with continuing
themed decoration. After composition, confirm the stamped barcode box does not
cover a card border or focal object.

## Page Count

Use `interior.pdf` page count when available. Counting `images/page_*.png` can be wrong when frontmatter pages are added or backup files match the pattern.

## Spine Text

Do not add spine text unless the spine width is safe and the user explicitly wants it. For thin KDP books, a plain blended spine is safer.

## Color Mode (RGB vs CMYK)

KDP prints in CMYK and recommends CMYK files with no embedded color profile. The
compose script outputs RGB; KDP accepts it and auto-converts, but neon/vivid RGB
and pure black can shift on press. Acceptable for coloring-book covers — set
expectations, don't promise screen-exact print color.

## Flatten / Transparency / Fonts (handled by construction)

The script rasterizes the whole wrap to one flat image embedded in the PDF, so
unflattened transparency, crop marks, and unembedded fonts (all common KDP reject
reasons) cannot occur — nothing extra to do.

## File Size

Keep the cover PDF ≤ 40 MB (KDP recommendation; 650 MB hard limit). A full-bleed
300-DPI PNG can exceed 25 MB; if the PDF is huge, re-export with JPEG compression
rather than uploading a giant file.

## Spine Text vs Spine Width (page-count rule wins)

KDP allows spine text only at 79+ pages, regardless of spine width. A 56–78 page
book can have a wide-enough spine yet still be rejected for spine text. The script
avoids this by never drawing spine text by default.

## Existing Assets

Back up `cover.pdf`, `cover.png`, `front_artwork.png`, and `back_artwork.png` before replacing them. Keep generated images under `$CODEX_HOME/generated_images/...` intact and copy selected assets into the project.
