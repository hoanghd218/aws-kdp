#!/usr/bin/env python3
"""Cover text safe-zone checker.

KDP's #1 cover reject: text too close to the edge ("move all text at least 0.375 in
away from all edges"). The printer trims the wrap ~0.125" in (bleed) and can drift
another ~0.25", so any *text* within ~0.375" of the trim line can be shaved off.

This tool draws the trim line (green) and the text-safe line (red) on a copy of the
cover and reports how much non-background ink sits in the danger band. It is meant to
run automatically right after a cover is composed, and as part of the kdp-cover-checker
skill. Because decorative art is *allowed* to bleed into the margin (only text/badges
are not), a positive ink reading is a "look at the overlay" signal, not an automatic
fail — always eyeball the saved cover_safe_check.png and confirm no letter crosses the
red line.

Usage:
    python scripts/check_cover_safezone.py <theme_key>
    python scripts/check_cover_safezone.py --png path/to/cover.png
    # options: --safe-in 0.375 (inches inside the trim line), --dpi 300, --quiet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

DEFAULT_DPI = 300
BLEED_IN = 0.125          # KDP wrap bleed — trimmed off entirely
SAFE_INSIDE_TRIM_IN = 0.375  # keep all text this far INSIDE the trim line


def _resolve_png(theme: str | None, png: str | None) -> Path:
    if png:
        p = Path(png)
        return p if p.is_absolute() else REPO_ROOT / p
    if theme:
        return REPO_ROOT / "output" / theme / "cover.png"
    raise SystemExit("Provide a <theme_key> or --png path.")


def check_safezone(
    cover_png: str | Path,
    out_overlay: str | Path | None = None,
    dpi: int = DEFAULT_DPI,
    bleed_in: float = BLEED_IN,
    safe_inside_trim_in: float = SAFE_INSIDE_TRIM_IN,
) -> dict:
    """Draw trim + safe guides on the cover and measure ink in the danger band.

    Returns a dict: {ok, margin_px, edges:{top,bottom,left,right: ink_pct}, overlay}.
    `ok` is True when ink in every danger band is below a soft threshold; it is a hint,
    not a guarantee — confirm visually with the overlay.
    """
    cover_png = Path(cover_png)
    im = Image.open(cover_png).convert("RGB")
    W, H = im.size

    bleed_px = round(bleed_in * dpi)
    safe_px = round(safe_inside_trim_in * dpi)
    margin_px = bleed_px + safe_px  # distance from the PDF edge to the text-safe line

    # --- overlay ---
    over = im.copy()
    d = ImageDraw.Draw(over)
    d.rectangle([bleed_px, bleed_px, W - bleed_px, H - bleed_px],
                outline=(0, 200, 0), width=6)            # trim line (green)
    d.rectangle([margin_px, margin_px, W - margin_px, H - margin_px],
                outline=(255, 0, 0), width=10)           # text-safe line (red)
    out_overlay = Path(out_overlay) if out_overlay else cover_png.with_name("cover_safe_check.png")
    over.save(out_overlay)

    # --- ink heuristic in the danger band (between the PDF edge and the red line) ---
    edges = {"top": None, "bottom": None, "left": None, "right": None}
    if np is not None:
        arr = np.array(im).astype(int)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        mx = np.maximum(np.maximum(r, g), b)
        mn = np.minimum(np.minimum(r, g), b)
        sat = mx - mn
        bright = mx
        # "sticker ink" = strongly saturated OR near-white outline (text/badges look like this)
        ink = (sat > 110) | (bright > 238)

        def band_pct(sl) -> float:
            sub = ink[sl]
            return round(100.0 * sub.mean(), 1) if sub.size else 0.0

        edges["top"] = band_pct(np.s_[bleed_px:margin_px, margin_px:W - margin_px])
        edges["bottom"] = band_pct(np.s_[H - margin_px:H - bleed_px, margin_px:W - margin_px])
        edges["left"] = band_pct(np.s_[margin_px:H - margin_px, bleed_px:margin_px])
        edges["right"] = band_pct(np.s_[margin_px:H - margin_px, W - margin_px:W - bleed_px])

    # The numbers are CONTEXT, not a verdict. On a plain-background cover, a single edge
    # spiking well above the others ≈ text intruding into the margin. On a full-bleed
    # vibrant cover every edge reads high (decoration bleeds), so the overlay — not the
    # number — is the real gate. We flag only an edge that is BOTH high and an outlier vs
    # the calmest edge, to cut false alarms on busy art.
    vals = [v for v in edges.values() if v is not None]
    baseline = min(vals) if vals else 0.0
    flagged = [
        e for e, v in edges.items()
        if v is not None and v > 25.0 and v - baseline > 25.0
    ]

    return {
        "ok": not flagged,            # hint only — always confirm with the overlay
        "margin_px": margin_px,
        "safe_inside_trim_in": safe_inside_trim_in,
        "edges": edges,
        "flagged": flagged,
        "overlay": str(out_overlay),
        "size": (W, H),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("theme", nargs="?", help="theme_key under output/")
    ap.add_argument("--png", help="explicit path to a cover PNG")
    ap.add_argument("--out", help="overlay output path (default <book>/cover_safe_check.png)")
    ap.add_argument("--safe-in", type=float, default=SAFE_INSIDE_TRIM_IN,
                    help="inches of text-safe margin inside the trim line (default 0.375)")
    ap.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    cover_png = _resolve_png(args.theme, args.png)
    if not cover_png.exists():
        raise SystemExit(f"Cover PNG not found: {cover_png}")

    res = check_safezone(cover_png, out_overlay=args.out,
                         dpi=args.dpi, safe_inside_trim_in=args.safe_in)

    if not args.quiet:
        print(f"🛡️  Cover safe-zone check — {cover_png}")
        print(f"   Text-safe margin: {args.safe_in}\" inside trim "
              f"({res['margin_px']}px from the file edge)")
        if res["edges"]["top"] is not None:
            e = res["edges"]
            print(f"   Danger-band ink %  top={e['top']}  bottom={e['bottom']}  "
                  f"left={e['left']}  right={e['right']}")
        else:
            print("   (numpy not available — ink heuristic skipped)")
        print(f"   Overlay: {res['overlay']}")
        if res["flagged"]:
            print(f"   ⚠️  Outlier ink on edge(s): {', '.join(res['flagged'])} — likely text/badge "
                  f"in the margin.")
        print("   👉 ALWAYS open the overlay: confirm NO letter/number/badge crosses the RED line. "
              "Decorative art (balloons, confetti, sparkles, gift boxes) crossing it is fine. "
              "Numbers run high on full-bleed art — trust the picture, not the percentage.")


if __name__ == "__main__":
    main()
