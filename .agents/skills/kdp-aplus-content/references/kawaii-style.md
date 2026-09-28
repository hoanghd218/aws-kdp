# Kawaii A+ visual style

The visual DNA for all A+ modules. Based on top-selling kawaii coloring books (Girl Getaway /
MinaAru, Coco Wyo "Little Cuddles"). Study these rules before writing any `image_prompt`.

---

## The core principle: **product first, decoration second**

The strongest A+ strips let the colored art do the selling. Decoration (stars, borders, doodles)
is SUPPORT — never the hero. When in doubt: less decoration, more art.

---

## The five style pillars

### 1. Background treatment (per module type)

**Hero + Specs modules (01, 02):**  
Warm golden yellow background (e.g. `#F2C84B`) with tiny scattered 4-point sparkle stars and
small plus signs in cream white. Sparse and asymmetric — confetti, not a pattern fill. **No outer
border frame** — the golden background extends to the panel edges.

**Sample Showcase modules (04, 05):**  
Solid soft teal background (e.g. `#6BBFBF`) with tiny scattered sparkle stars and plus signs in
white/cream. **Same sparse confetti rule. No outer border frame.** The two showcase panels share
the same background so they read as a matched pair.

**Features/Friends module (03) only:**  
Soft cream `#FBF3E4` with a hand-drawn wavy scalloped deckle border in the book's accent color —
gently rippled like torn paper edge, NOT a hard rectangle. Reserve generous empty margin inside
the frame. Sparse pastel doodles (plus signs, small hearts, sparkles). This is the ONE module
that uses the frame treatment.

### 2. Scattered doodle accents

Sprinkle a FEW tiny doodles in empty spaces: 4-point sparkle stars, small plus signs, tiny hearts,
mini flowers. **Sparse and asymmetric** — think confetti, not a pattern fill. Muted pastel, low
contrast. More decoration = more amateur. Less = more premium.

### 3. Two-font typography

- **Brand / labels / callouts / captions** → friendly **handwritten marker script**, warm brown
  `#5A4636` — never pure black.
- **Big titles / section headers** → **chunky rounded bubble font**, thick dark warm-brown outline
  `#5A4636` with white (or pale) fill, slight playful tilt (3–5 degrees).

### 4. Peeking mascot (module 03 only)

A tiny chibi animal peeking over a corner or panel edge — paws on the rim, big simple face, blush
cheeks. Use in the Features/Friends module only (not in showcase or hero panels).

### 5. Kawaii character rendering

Any illustrated character/animal must be **chibi-cute**: soft rounded shapes, oversized simple
faces, big dot eyes, blush cheek circles, **thin warm-brown outlines** (NOT harsh black), flat-to-
soft cel shading in **pastel** colors. Full-color samples in showcase modules are cel-shaded in the
book's actual palette — not AI-generic art.

---

## Palette

Pull 3–4 colors from the book's own `cover_prompt`. Carry ONE palette across all modules.
Default cozy palette if cover gives nothing: cream `#FBF3E4`, blush `#F0C4B8`, sage `#BFD3A8`,
amber `#C8A86E`, warm brown text `#5A4636`.

**Background yellows and teals are ADDITIONAL** to the book palette — they're structural colors
for the panel backgrounds, not from the book's own palette. Choose them to complement, not clash.

---

## Colored sample images (modules 04 and 05)

These are the most important visual in the strip. They must:

1. **Show a specific scene** from the book's `page_prompts` — name the character, location, props,
   and all colors in the prompt. "A cozy reading scene" is too vague.
2. **Render completely** — NOT a placeholder. The renderer draws the full colored illustration.
3. **Use the book's actual palette** — state each color (`#FBF3E4` cream walls, `#F0C4B8` dusty
   pink cushions, etc.) so the renderer matches the cover.
4. Have a **thick colored border frame** (8px, a different accent color per module) like a premium
   photo card + soft drop shadow.
5. Use **cel-shaded flat pastel** style with warm-brown outlines — the same style as the book's
   kawaii line art, but in full color.

---

## Composite placeholders

When real files need to be dropped in at layout time:
- **Cover composite** (hero 01, specs 02): a light warm-cream rectangle with a thin dashed warm-
  brown outline, labeled "composite: front cover here". Show it as a standing tilted paperback
  shape with soft drop shadow.
- **Page composites** (showcase 04, 05 thumbnails): white squares with thin dashed warm-brown
  borders, labeled "composite: page_NN.png line-art thumbnail". Show polaroid-style (thin white
  border, slight tilt, soft shadow).

---

## Reserve space for copy

Any module with baked-in text needs a **clear, calm area** for it — open background or flat cream
panel. State this explicitly in the prompt: "leave the right 55% as open golden background for
large typography". Showcase modules (04, 05) carry **no text** — omit this instruction for them.

---

## KDP A+ hard rules (screen images — NOT print)

A+ images display on Amazon product pages (screens). KDP checks pixel dimensions and file size
only — DPI metadata is irrelevant.

- **Width = 970 px** (exact). Height 300–600 px typical. PNG or JPG, **≤ 5 MB** per module.
- NO external links, phone, email, price/shipping, or "free" claims.
- NO time-sensitive or ranking words: "new", "#1", "best seller", "sale".
- NO other brands' trademarks or characters; NO customer-review quotes.
- Keep all baked-in text well inside the frame (safe margin) — nothing should look cut off.

---

## Common mistakes to avoid

| Bad | Good |
|-----|------|
| Complex scalloped border on showcase panels | Solid teal background + sparse sparkle stars |
| Three equal-size images per showcase module | 1 large colored image + 2 smaller thumbnails |
| Generic "cozy scene" colored sample | Named character + specific scene + exact palette colors |
| Harsh black outlines on kawaii characters | Thin warm-brown outlines `#5A4636` |
| Pure black text | Warm brown text `#5A4636` |
| Heavy decoration everywhere | Sparse confetti doodles only in empty corners |
| Same colored scene in both showcase panels | Different scene in 04 vs 05 |
| Mismatched backgrounds across modules | Consistent: yellow hero/specs, teal showcases |
