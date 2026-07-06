# Cover Pitfalls

## Trim-Safe Text (text too close to the edge gets cut)

KDP prints the wrap larger than the finished book, then trims it: the outer
0.125" (bleed) is removed entirely and the blade can drift another ~0.25". The
practical safe margin is **0.375" (≈112 px at 300 DPI) from every cover edge** —
any text inside that band can be shaved off. Code overlays honor
`SAFE_MARGIN = 0.375"`, but the AI-generated front title/subtitle/author do not
unless the prompt says so: demand a wide empty margin on all four sides and keep
all type inside the central ~80% of the panel. Verify in the rendered PNG; if a
letter is near an edge, re-generate that panel.

## Prompt-Generated Barcode Zones

Do not prompt image generation to leave a blank barcode/stamp area. Models often create the wrong size, position, or multiple blank boxes. Generate full artwork, then cover the barcode area in code.

## Back Cover Text

For stable headline or feature text, prefer code overlays. Use generated text only when the user explicitly wants the text to be part of the illustration.

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
