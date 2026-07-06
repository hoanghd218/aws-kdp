#!/usr/bin/env python3
"""Generate A+ Content images for a KDP book using the chatgpt renderer.

Reads output/{theme_key}/aplus_content.json, generates each module with the
chatgpt renderer, crops/resizes to the exact A+ pixel size, then composites
real cover/page files on top using Pillow (no placeholder text in final image).

Usage:
    python scripts/generate_aplus_images.py <theme_key> [--renderer chatgpt|ai33|nanopic]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image, ImageFilter
import image_providers


# A+ size → nearest supported aspect ratio
SIZE_TO_ASPECT = {
    "970x500": "16:9",
    "970x600": "4:3",
}


# ── Pillow composite helpers ─────────────────────────────────────────────────

def _drop_shadow(img: Image.Image, offset: int = 8, blur: int = 14, alpha: int = 55) -> Image.Image:
    """Return an RGBA image with a soft drop-shadow behind the original."""
    img = img.convert("RGBA")
    pad = blur * 2 + abs(offset)
    canvas = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, alpha))
    shadow.putalpha(img.split()[3])
    canvas.paste(shadow, (pad + offset, pad + offset), shadow)
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(img, (pad, pad), img)
    return canvas


def _paste_centered(bg: Image.Image, overlay: Image.Image, cx: int, cy: int) -> Image.Image:
    bg = bg.convert("RGBA")
    x = cx - overlay.width // 2
    y = cy - overlay.height // 2
    bg.paste(overlay, (x, y), overlay)
    return bg


def composite_cover(bg: Image.Image, cover_path: str) -> Image.Image:
    """Paste the real book cover (tilted, shadowed) onto the left zone of bg."""
    if not cover_path or not os.path.exists(cover_path):
        return bg
    pw, ph = bg.size
    cover = Image.open(cover_path).convert("RGBA")
    # resize: fill ~78% of panel height
    target_h = int(ph * 0.78)
    target_w = int(cover.width * target_h / cover.height)
    cover = cover.resize((target_w, target_h), Image.LANCZOS)
    # slight rightward tilt
    cover = cover.rotate(-5, expand=True, resample=Image.BICUBIC)
    cover = _drop_shadow(cover, offset=10, blur=16, alpha=55)
    # center in left 42% of panel
    cx = int(pw * 0.21)
    cy = int(ph * 0.50)
    return _paste_centered(bg, cover, cx, cy).convert("RGB")


def composite_polaroids(
    bg: Image.Image,
    page_paths: list[str],
    zone: str,          # "left" | "right"
    panel_size: str,    # "970x600" | "970x500"
) -> Image.Image:
    """Paste 2 line-art page thumbnails as tilted polaroid cards."""
    pw_str, ph_str = panel_size.split("x")
    pw, ph = int(pw_str), int(ph_str)
    thumb = int(ph * 0.37)   # thumbnail square side ~222px for 600px panel
    border = 14               # polaroid white border

    # (center_x, center_y, tilt_degrees) for top and bottom card
    if zone == "left":
        cx = int(pw * 0.16)
        slots = [(cx - 18, int(ph * 0.30), +5), (cx + 22, int(ph * 0.68), -4)]
    else:
        cx = int(pw * 0.84)
        slots = [(cx + 18, int(ph * 0.30), -5), (cx - 22, int(ph * 0.68), +4)]

    bg = bg.convert("RGBA")
    for path, (scx, scy, angle) in zip(page_paths[:2], slots):
        if not path or not os.path.exists(path):
            continue
        page = Image.open(path).convert("RGB")
        # square-crop to thumb size
        sq = Image.new("RGB", (thumb, thumb), (255, 255, 255))
        page.thumbnail((thumb, thumb), Image.LANCZOS)
        sq.paste(page, ((thumb - page.width) // 2, (thumb - page.height) // 2))
        # white polaroid border
        pol_w, pol_h = sq.width + border * 2, sq.height + border * 2
        polaroid = Image.new("RGBA", (pol_w, pol_h), (255, 255, 255, 255))
        polaroid.paste(sq, (border, border))
        # tilt + shadow
        polaroid = polaroid.rotate(angle, expand=True, resample=Image.BICUBIC)
        polaroid = _drop_shadow(polaroid, offset=6, blur=10, alpha=50)
        bg = _paste_centered(bg, polaroid, scx, scy)

    return bg.convert("RGB")


def apply_composites(img: Image.Image, module: dict, book_dir: str) -> Image.Image:
    """Run all Pillow composites for a module based on its composite_files config."""
    composite_type = module.get("composite")
    files = module.get("composite_files", {})
    size = module.get("size", "970x600")

    if composite_type in ("cover", "page"):
        cover_path = files.get("cover") or os.path.join(book_dir, "front_artwork.png")
        img = composite_cover(img, cover_path)

    if composite_type == "pages":
        pages = files.get("pages", [])
        # determine zone: left zone for 04, right zone for 05
        mid = module.get("id", "")
        zone = "right" if mid.startswith("05") else "left"
        img = composite_polaroids(img, pages, zone, size)

    return img


# ── Resize helper ────────────────────────────────────────────────────────────

def resize_to_aplus(img: Image.Image, target_size: str) -> Image.Image:
    w_str, h_str = target_size.split("x")
    tw, th = int(w_str), int(h_str)
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    new_w, new_h = int(iw * scale), int(ih * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - tw) // 2
    top = (new_h - th) // 2
    return img.crop((left, top, left + tw, top + th))


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: generate_aplus_images.py <theme_key> [--renderer chatgpt|ai33|nanopic]")
        sys.exit(1)

    theme = sys.argv[1]
    renderer = "chatgpt"
    for i, arg in enumerate(sys.argv):
        if arg == "--renderer" and i + 1 < len(sys.argv):
            renderer = sys.argv[i + 1]

    book_dir = os.path.join("output", theme)
    aplus_json = os.path.join(book_dir, "aplus_content.json")
    out_dir = os.path.join(book_dir, "aplus")
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(aplus_json):
        print(f"Error: {aplus_json} not found. Run the kdp-aplus-content skill first.")
        sys.exit(1)

    data = json.load(open(aplus_json, encoding="utf-8"))
    modules = data.get("modules", [])
    print(f"Generating {len(modules)} A+ modules for '{theme}' with renderer={renderer}\n")

    for m in modules:
        mid = m.get("id")
        prompt = m.get("image_prompt", "")
        size = m.get("size", "970x600")
        aspect = SIZE_TO_ASPECT.get(size, "4:3")
        out_path = os.path.join(out_dir, f"aplus_{mid}.png")

        ref = m.get("reference_images") or m.get("reference_image") or None
        composite_type = m.get("composite")

        print(f"[{mid}] size={size} aspect={aspect} composite={composite_type!r}")
        if ref:
            refs = ref if isinstance(ref, list) else [ref]
            print(f"  refs: {[r[:60] for r in refs]}")
        print(f"  prompt: {prompt[:120]}...")

        img = image_providers.generate_image(
            prompt, renderer=renderer, aspect_ratio=aspect, reference_image=ref
        )
        if img is None:
            print(f"  ERROR: renderer returned None, skipping {mid}")
            continue

        img = resize_to_aplus(img, size)
        img = apply_composites(img, m, book_dir)
        img.save(out_path)
        print(f"  Saved → {out_path}  ({img.size[0]}x{img.size[1]})\n")

    print("Done. Images saved to:", out_dir)


if __name__ == "__main__":
    main()
