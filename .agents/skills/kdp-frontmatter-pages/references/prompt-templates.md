# Frontmatter Prompt Blueprints

Use these to write 3 personalized prompts into `output/<theme>/frontmatter/1.txt`,
`2.txt`, `3.txt`. Personalize every bracketed slot from the book's `plan.json`
(theme, audience, age, author, title, recurring characters/objects).

## Golden rules (apply to all 3)
- **Match the interior + cover style.** Read a few `page_prompts` and the
  `cover_prompt` first. Reuse the same style words (e.g. "kawaii", "bold & easy",
  recurring mascots like a teddy bear / bunny).
- **SQUARE** for 8.5x8.5 books, **PORTRAIT (3:4)** for 8.5x11 books — say it explicitly.
- **Grayscale**: "black outlines with soft light-gray shading on a pure white
  background." Interior prints in B&W; never ask for color.
- **Text is baked into the image.** Spell out the EXACT words in quotes, say where
  each line sits (top / center / bottom) and the lettering style (thick rounded
  BUBBLE letters for big titles; clean rounded sans-serif for small copy).
  End with: *"Spell every word exactly as written above."*
- **No full-page border box, no frame, no crop marks.** Keep a comfortable white
  margin around all four edges (nothing touching the edge).
- Title text on page 1 should be a short, punchy version of the book title (the
  hero phrase), NOT the full 60-character KDP title.

## Reliability note
Big bubble-letter titles render reliably. Long small-print paragraphs sometimes
get a misspelled word — that's expected. After images are generated, inspect
them; if small copy is wrong, either regenerate that page, or the
assembly script's plain copyright page already carries the legal text so the
title/thank-you art only needs its short headline + short message.

---

## 1.txt — TITLE PAGE
```
TITLE PAGE for a children's coloring book — <SQUARE|PORTRAIT 3:4> format, grayscale
(black outlines with soft light-gray shading) on a pure white background. <STYLE words
from plan, e.g. kawaii / cute cartoon>. Professional Amazon KDP coloring book look.
Comfortable white margin on all four edges.

LAYOUT top to bottom, centered:
1) TOP ROW of three cute <THEME> objects with thick black outlines + soft gray shading:
   <object A>, <object B>, <object C>. A few small confetti stars/dots between them.
2) BIG HERO TITLE in thick rounded puffy BUBBLE letters, bold black outline + white fill,
   stacked lines: "<HERO TITLE LINE 1>" / "<HERO TITLE LINE 2>". Sub-banner below in bold
   rounded uppercase: "<BOLD & EASY COLORING BOOK or genre line>".
3) BOTTOM ROW of three more <THEME> objects, black outline + soft gray shading:
   <object D>, <object E>, <object F>, with a few confetti stars.
4) SUBTITLE in clean rounded sans-serif (not bubble), three short centered lines:
   "<subtitle line 1>" / "<subtitle line 2>" / "<subtitle line 3>".
5) Bottom small italic, centered: "Copyright <YEAR> © <AUTHOR>. All Rights Reserved."

Spell every word exactly as written above. No frame, no full-page border box, no color —
grayscale only. Cute, friendly, balanced composition.
```

## 2.txt — THIS BOOK BELONGS TO  (optional; great for kids)
```
"THIS BOOK BELONGS TO" page for a children's coloring book — <SQUARE|PORTRAIT 3:4>,
grayscale (black outlines + soft light-gray shading) on pure white. <STYLE words>.
Comfortable white margin on all edges.

LAYOUT top to bottom, centered:
1) HEADER in clean rounded bold uppercase, large: "THIS BOOK BELONGS TO".
2) TWO long horizontal hand-drawn name lines (gently rounded), blank on the lines.
3) Shorter centered line with a blank rule: "AGE: ____".
4) CENTER-BOTTOM one big adorable <THEME mascot> illustration with thick black outlines
   + soft gray shading (e.g. <mascot> wearing a <theme accessory> holding/with <theme item>),
   surrounded by several cute stars and small confetti dots.

Spell every word exactly as written above. No full-page border box, no frame, no color —
grayscale only. Lots of clean white space in the top half.
```

## 3.txt — THANK YOU (last page)
```
"THANK YOU" closing page for a children's coloring book — <SQUARE|PORTRAIT 3:4>, grayscale
(black outlines + soft light-gray shading) on pure white. <STYLE words>. Comfortable margin
on all edges.

LAYOUT top to bottom, centered:
1) BIG HERO HEADER in thick rounded puffy BUBBLE letters, bold black outline + white fill:
   "<UPBEAT HEADLINE e.g. HOORAY, YOU DID IT!>".
2) MIDDLE: a joyful <THEME> scene — <two recurring mascots> waving goodbye, <theme objects>
   (balloons/stars/confetti) floating, a <theme centerpiece> between them. Thick black
   outlines + soft gray shading.
3) BELOW, a warm message in clean rounded sans-serif, three short centered lines that are
   SPECIFIC to this book's theme (mention real objects from the book):
   "<line 1>" / "<line 2>" / "<line 3>".
4) Bottom smaller note, two centered lines:
   "Grown-ups: if your little artist loved this book, a quick" /
   "review on Amazon helps other families find the fun. Thank you!"

Spell every word exactly as written above. No full-page border box, no frame, no color —
grayscale only. Heart-warming, celebratory, balanced.
```

> For **adult** books: drop "AGE" / "little artist" wording, swap mascots for elegant
> theme motifs, and use a calmer headline ("Thank You for Coloring", message about
> relaxation/stress relief), and a refined serif/script feel instead of bubble letters.
