# Frontmatter Artwork Prompt Templates

These prompts create decorative artwork only. Exact copy is added later by `compose_frontmatter.py`.

## Shared constraints

- Use case: `illustration-story`.
- Match the book's style bible, recurring subjects, and line weight.
- `SQUARE 1:1` for 8.5x8.5; `PORTRAIT 3:4` for 8.5x11.
- Black-and-white/grayscale line illustration on white; restrained light gray is acceptable outside text zones.
- Keep a generous clean central region for deterministic text overlays.
- No words, letters, numbers, symbols that resemble text, logos, signatures, watermarks, borders, frames, crop marks, or page mockups.
- Keep all decorative art inside safe margins.

## Title artwork

```text
Use case: illustration-story
Asset type: Amazon KDP interior title-page artwork
Primary request: Create elegant decorative artwork for a <theme> coloring-book title page.
Subject: <3–5 concrete motifs or recurring characters from the actual book>
Style/medium: <style bible>, grayscale line illustration with bold clean outlines
Composition/framing: <ratio>; motifs arranged around the outer upper and lower thirds; large calm white central area for title, subtitle, and author overlay
Constraints: artwork only; safe margins; no full-page border
Avoid: all text/letters/numbers, watermark, logo, frame, dense clutter, mockup
```

## Ownership artwork (kids only)

```text
Use case: illustration-story
Asset type: Amazon KDP "This Book Belongs To" page artwork
Primary request: Create playful decorative artwork for a child to personalize this <theme> coloring book.
Subject: one friendly recurring mascot plus small theme motifs
Style/medium: <style bible>, grayscale line illustration with bold clean outlines
Composition/framing: <ratio>; mascot in the lower third; upper two-thirds mostly clean white for heading and writing lines
Constraints: artwork only; safe margins; no full-page border
Avoid: all text/letters/numbers, pre-drawn writing lines, watermark, logo, frame, mockup
```

## Copyright/welcome artwork

```text
Use case: illustration-story
Asset type: Amazon KDP interior copyright/welcome-page artwork
Primary request: Create elegant text-free decoration for the book's welcome and legal page.
Subject: <3–6 quiet motifs taken from the actual book>
Style/medium: <style bible>, grayscale line illustration with bold clean outlines
Composition/framing: <ratio>; motifs limited to the outer edges and lower corners; large clean central field for exact typography
Constraints: artwork only; safe margins; no full-page border
Avoid: all text/letters/numbers, copyright symbol, writing lines, watermark, logo, frame, dense clutter, mockup
```

## Instructions artwork

```text
Use case: illustration-story
Asset type: Amazon KDP interior coloring-instructions artwork
Primary request: Create light, inviting text-free decoration for a practical four-step coloring guide.
Subject: <coloring tools plus 3–5 recurring theme motifs>
Style/medium: <style bible>, grayscale line illustration with bold clean outlines
Composition/framing: <ratio>; small airy motifs in the outer corners and extreme edges; large clean central field for heading and four instruction rows
Constraints: artwork only; safe margins; no full-page border
Avoid: all text/letters/numbers, writing lines, labels, watermark, logo, frame, dense clutter, mockup
```

## Closing artwork

```text
Use case: illustration-story
Asset type: Amazon KDP coloring-book closing-page artwork
Primary request: Create a warm final-page illustration that feels like a satisfying goodbye to this specific <theme> book.
Subject: <recurring subject> with <2–4 recognizable objects/scene motifs from the book>
Style/medium: <style bible>, grayscale line illustration with bold clean outlines
Composition/framing: <ratio>; decorative action in the upper/lower outer areas; clean central field for closing message and review note
Constraints: artwork only; warm but uncluttered; safe margins; no full-page border
Avoid: all text/letters/numbers, review stars, watermark, logo, frame, mockup
```
