#!/usr/bin/env python3
"""
Generate a KDP-ready full cover (front + spine + back) for coloring books.
Uses Gemini API to generate front cover artwork, then composites with text.
"""

import argparse
import io
import os
import sys
import textwrap

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import config

load_dotenv()

# --- Cover Dimensions ---
BLEED_INCHES = 0.125
PAPER_THICKNESS = 0.002252  # White paper, inches per page
TRIM_WIDTH = config.PAGE_WIDTH_INCHES   # 8.5"
TRIM_HEIGHT = config.PAGE_HEIGHT_INCHES  # 11"
SAFE_MARGIN = 0.375  # Keep important content this far from trim edge


def calculate_cover_dimensions(total_pages: int) -> dict:
    """Calculate full cover dimensions based on page count."""
    spine_width = total_pages * PAPER_THICKNESS

    full_width = (2 * TRIM_WIDTH) + spine_width + (2 * BLEED_INCHES)
    full_height = TRIM_HEIGHT + (2 * BLEED_INCHES)

    full_width_px = int(full_width * config.DPI)
    full_height_px = int(full_height * config.DPI)

    # Regions in pixels (from left to right)
    bleed_px = int(BLEED_INCHES * config.DPI)
    trim_w_px = int(TRIM_WIDTH * config.DPI)
    spine_w_px = int(spine_width * config.DPI)
    safe_px = int(SAFE_MARGIN * config.DPI)

    return {
        "total_pages": total_pages,
        "spine_width_inches": spine_width,
        "full_width_inches": full_width,
        "full_height_inches": full_height,
        "full_width_px": full_width_px,
        "full_height_px": full_height_px,
        "bleed_px": bleed_px,
        "trim_w_px": trim_w_px,
        "spine_w_px": spine_w_px,
        "safe_px": safe_px,
        # Region x-coordinates
        "back_start_x": bleed_px,
        "spine_start_x": bleed_px + trim_w_px,
        "front_start_x": bleed_px + trim_w_px + spine_w_px,
        "can_have_spine_text": total_pages >= 79,
    }


def count_pages(theme: str) -> int:
    """Count total pages from generated images."""
    image_dir = os.path.join(config.OUTPUT_IMAGES_DIR, theme)
    if not os.path.exists(image_dir):
        return config.COLORING_PAGES_PER_BOOK * 2 + 3  # Estimate

    num_images = len([f for f in os.listdir(image_dir) if f.endswith(".png")])
    if num_images == 0:
        num_images = config.COLORING_PAGES_PER_BOOK

    total = 2 + (num_images * 2) + 1  # title + copyright + pages*2 + thankyou
    if total % 2 != 0:
        total += 1
    return total


def generate_front_artwork(theme: str, title: str = "") -> Image.Image | None:
    """Generate front cover artwork using Gemini API."""
    import json

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    theme_config = config.THEMES[theme]

    # Try to load cover_prompt from plan file
    plan_path = os.path.join("plans", f"{theme}_plan.json")
    cover_prompt_from_plan = None
    if os.path.exists(plan_path):
        with open(plan_path) as f:
            plan = json.load(f)
            cover_prompt_from_plan = plan.get("cover_prompt")

    if cover_prompt_from_plan:
        # Use plan's cover prompt, but ensure title text is included in artwork
        prompt = cover_prompt_from_plan
        # Override the "DO NOT include text" instruction — we WANT the title in the artwork
        prompt = prompt.replace("DO NOT include any text, letters, or words in the generated image.", "")
        prompt += f'\n\nIMPORTANT: Include the book title "{title}" as beautiful, large, decorative text integrated into the artwork at the top of the image. The title text should be stylish, readable, and part of the cover design. Do NOT include any placeholder text, subtitle text, or extra text besides the title.'
    else:
        theme_subjects = {
            "cute_animals": "a cute cat, puppy, and bunny playing together in a colorful flower garden with butterflies",
            "dinosaurs": "a friendly T-Rex, Triceratops, and baby Pterodactyl in a vibrant prehistoric jungle with volcano",
            "vehicles": "a bright red fire truck, rocket ship, and yellow airplane flying over a cheerful city",
            "unicorn_fantasy": "a magical unicorn with rainbow mane, a fairy with sparkly wings, and a baby dragon in an enchanted garden",
        }
        subject = theme_subjects.get(theme, "cute cartoon characters for children")
        prompt = f"""Create a colorful, vibrant book cover illustration for a coloring book.
Theme: {theme_config['name']}
Title: {title}
Style: Bright, cheerful, eye-catching, cartoon style, professional book cover art.
The image should feature {subject}.
IMPORTANT: Include the book title "{title}" as beautiful, large, decorative text integrated into the artwork at the top. The title should be stylish, readable, and part of the cover design. Do NOT include any placeholder text, subtitle text, or extra text besides the title.
The artwork should be high quality, detailed, and appealing.
Use a clean, attractive background with vibrant colors."""

    print("Generating front cover artwork...")
    for attempt in range(config.MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data
                    return Image.open(io.BytesIO(image_data))

            print(f"  No image in response (attempt {attempt + 1})")
        except Exception as e:
            print(f"  Error (attempt {attempt + 1}): {e}")

    return None


def colorize_page(image_path: str) -> Image.Image | None:
    """Use Gemini to colorize a line art coloring page."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    client = genai.Client(api_key=api_key)

    img = Image.open(image_path).convert("RGB")
    # Resize for API efficiency
    img_small = img.resize((512, 664), Image.Resampling.LANCZOS)
    img_bytes = io.BytesIO()
    img_small.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    prompt = """Color this coloring page with beautiful, vibrant colors.
Fill in all the white areas with appropriate colors while keeping the black outlines visible.
Use a warm, cozy color palette with soft pastels and warm tones.
Make it look like a professionally colored coloring book page."""

    try:
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=img_bytes.read(), mime_type="image/png"),
                prompt,
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
    except Exception as e:
        print(f"  Colorize failed: {e}")

    return None


def get_sample_pages(theme: str, count: int = 6) -> list[str]:
    """Select evenly spaced sample pages from the theme."""
    image_dir = os.path.join(config.OUTPUT_IMAGES_DIR, theme)
    pages = sorted([
        os.path.join(image_dir, f)
        for f in os.listdir(image_dir)
        if f.endswith(".png")
    ])
    if len(pages) <= count:
        return pages
    # Pick evenly spaced pages
    step = len(pages) / count
    return [pages[int(i * step)] for i in range(count)]


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Get a font, falling back to default if custom fonts unavailable."""
    # Try common system fonts on macOS
    font_paths = []
    if bold:
        font_paths = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        font_paths = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    return ImageFont.load_default()


def draw_text_with_outline(
    draw: ImageDraw.ImageDraw,
    position: tuple,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str = "white",
    outline_color: str = "black",
    outline_width: int = 3,
):
    """Draw text with outline for readability on any background."""
    x, y = position
    # Draw outline
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx * dx + dy * dy <= outline_width * outline_width:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    # Draw main text
    draw.text(position, text, font=font, fill=fill)


def build_cover(
    theme: str,
    author: str = "",
    custom_title: str | None = None,
    kdp_width: float | None = None,
    kdp_height: float | None = None,
):
    """Build the complete cover image."""
    theme_config = config.THEMES.get(theme)
    if not theme_config:
        print(f"Error: Unknown theme '{theme}'")
        sys.exit(1)

    title = custom_title or theme_config["book_title"]
    total_pages = count_pages(theme)

    if kdp_width and kdp_height:
        # Use exact KDP dimensions — back-calculate spine from total width
        spine_width = kdp_width - (2 * TRIM_WIDTH) - (2 * BLEED_INCHES)
        bleed_px = round(BLEED_INCHES * config.DPI)
        trim_w_px = round(TRIM_WIDTH * config.DPI)
        spine_w_px = round(spine_width * config.DPI)
        safe_px = round(SAFE_MARGIN * config.DPI)
        dims = {
            "total_pages": total_pages,
            "spine_width_inches": spine_width,
            "full_width_inches": kdp_width,
            "full_height_inches": kdp_height,
            "full_width_px": round(kdp_width * config.DPI),
            "full_height_px": round(kdp_height * config.DPI),
            "bleed_px": bleed_px,
            "trim_w_px": trim_w_px,
            "spine_w_px": spine_w_px,
            "safe_px": safe_px,
            "back_start_x": bleed_px,
            "spine_start_x": bleed_px + trim_w_px,
            "front_start_x": bleed_px + trim_w_px + spine_w_px,
            "can_have_spine_text": total_pages >= 79,
        }
        print("(Using exact KDP dimensions)")
    else:
        dims = calculate_cover_dimensions(total_pages)

    print(f"Theme: {theme_config['name']}")
    print(f"Title: {title}")
    print(f"Pages: {dims['total_pages']}")
    print(f"Spine: {dims['spine_width_inches']:.3f}\"")
    print(f"Cover: {dims['full_width_inches']:.3f}\" x {dims['full_height_inches']:.3f}\"")
    print(f"Pixels: {dims['full_width_px']} x {dims['full_height_px']}")
    print()

    # Create full cover canvas (white background)
    cover = Image.new("RGB", (dims["full_width_px"], dims["full_height_px"]), (255, 255, 255))
    draw = ImageDraw.Draw(cover)

    # --- Generate and place front cover artwork ---
    artwork = generate_front_artwork(theme, title)
    if artwork:
        # Resize artwork to fit front cover area
        front_w = dims["trim_w_px"]
        front_h = dims["full_height_px"]
        artwork = artwork.convert("RGB")
        artwork = artwork.resize((front_w, front_h), Image.Resampling.LANCZOS)
        cover.paste(artwork, (dims["front_start_x"], 0))
        print("Front artwork placed.")
    else:
        # Fallback: solid color background for front
        print("Warning: Could not generate artwork. Using solid color.")
        front_colors = {
            "cute_animals": (255, 200, 220),
            "dinosaurs": (200, 230, 200),
            "vehicles": (200, 220, 255),
            "unicorn_fantasy": (230, 200, 255),
        }
        color = front_colors.get(theme, (200, 220, 255))
        draw.rectangle(
            [dims["front_start_x"], 0, dims["full_width_px"], dims["full_height_px"]],
            fill=color,
        )

    # --- Back cover: light gradient/solid ---
    back_colors = {
        "cute_animals": (255, 245, 248),
        "dinosaurs": (245, 255, 245),
        "vehicles": (240, 248, 255),
        "unicorn_fantasy": (248, 240, 255),
    }
    back_color = back_colors.get(theme, (248, 248, 255))
    draw.rectangle(
        [0, 0, dims["spine_start_x"], dims["full_height_px"]],
        fill=back_color,
    )

    # --- Spine: slightly darker ---
    spine_color = tuple(max(0, c - 30) for c in back_color)
    draw.rectangle(
        [
            dims["spine_start_x"],
            0,
            dims["front_start_x"],
            dims["full_height_px"],
        ],
        fill=spine_color,
    )

    # --- Add bottom gradient overlay on front cover for subtitle/author ---
    front_x = dims["front_start_x"]
    front_w = dims["trim_w_px"]
    full_h = dims["full_height_px"]

    bottom_h = full_h // 5
    bottom_overlay = Image.new("RGBA", (front_w, bottom_h), (0, 0, 0, 0))
    bottom_draw = ImageDraw.Draw(bottom_overlay)
    for y in range(bottom_h):
        alpha = int(200 * (y / bottom_h))  # Fade from transparent to dark
        bottom_draw.line([(0, y), (front_w, y)], fill=(0, 0, 0, alpha))
    front_region = cover.crop((front_x, full_h - bottom_h, front_x + front_w, full_h)).convert("RGBA")
    front_region = Image.alpha_composite(front_region, bottom_overlay)
    cover.paste(front_region.convert("RGB"), (front_x, full_h - bottom_h))

    # Refresh draw after overlay
    draw = ImageDraw.Draw(cover)

    # --- Add author name only to Front Cover (title + subtitle are in artwork) ---
    front_center_x = dims["front_start_x"] + dims["trim_w_px"] // 2
    safe = dims["safe_px"]

    if author:
        author_font = get_font(44, bold=False)
        bbox = draw.textbbox((0, 0), author, font=author_font)
        auth_w = bbox[2] - bbox[0]
        auth_y = dims["full_height_px"] - dims["bleed_px"] - safe - 80
        draw_text_with_outline(
            draw,
            (front_center_x - auth_w // 2, auth_y),
            author,
            author_font,
            fill="white",
            outline_color=(30, 30, 30),
            outline_width=4,
        )

    # --- Back cover: sample pages grid + text ---
    back_center_x = dims["bleed_px"] + dims["trim_w_px"] // 2
    back_font = get_font(32, bold=False)
    back_title_font = get_font(44, bold=True)
    safe = dims["safe_px"]

    # Back title
    back_title = f"{config.THEMES[theme]['name']}"
    bbox = draw.textbbox((0, 0), back_title, font=back_title_font)
    bt_w = bbox[2] - bbox[0]
    title_y = dims["bleed_px"] + safe + 60
    draw.text(
        (back_center_x - bt_w // 2, title_y),
        back_title,
        font=back_title_font,
        fill=(40, 40, 40),
    )

    # Short description below title
    desc_font = get_font(28, bold=False)

    # Count actual images
    image_dir = os.path.join(config.OUTPUT_IMAGES_DIR, theme)
    num_images = len([f for f in os.listdir(image_dir) if f.endswith(".png")]) if os.path.exists(image_dir) else 0

    # Load plan for description
    import json
    plan_path = os.path.join("plans", f"{theme}_plan.json")
    plan_desc = ""
    plan_audience = "adults"
    if os.path.exists(plan_path):
        with open(plan_path) as f:
            plan_data = json.load(f)
            plan_desc = plan_data.get("description", "")
            plan_audience = plan_data.get("audience", "adults")

    back_desc_lines = [
        f"{num_images} unique coloring pages",
        "Bold, easy-to-color designs",
        "Single-sided pages to prevent bleed-through",
        "Hours of creative relaxation!",
    ]
    desc_y = title_y + 70
    for line in back_desc_lines:
        bbox = draw.textbbox((0, 0), line, font=desc_font)
        line_w = bbox[2] - bbox[0]
        draw.text(
            (back_center_x - line_w // 2, desc_y),
            line,
            font=desc_font,
            fill=(80, 80, 80),
        )
        desc_y += 42

    # --- Sample pages grid (3 colored + 3 line art) ---
    sample_paths = get_sample_pages(theme, 6)
    if sample_paths:
        print("Generating sample page previews for back cover...")
        # Colorize first 3, keep last 3 as line art
        colored_count = min(3, len(sample_paths))
        sample_images = []

        import time
        for i, path in enumerate(sample_paths):
            if i < colored_count:
                print(f"  Colorizing sample {i + 1}/{colored_count}: {os.path.basename(path)}...")
                colored = colorize_page(path)
                if colored:
                    sample_images.append(("colored", colored))
                else:
                    # Fallback: use line art
                    sample_images.append(("lineart", Image.open(path).convert("RGB")))
                if i < colored_count - 1:
                    time.sleep(config.REQUEST_DELAY_SECONDS)
            else:
                sample_images.append(("lineart", Image.open(path).convert("RGB")))

        # Layout: 2 rows x 3 cols grid
        grid_cols = 3
        grid_rows = 2
        back_area_w = dims["trim_w_px"] - 2 * safe
        grid_top = desc_y + 30
        # Leave space for barcode at bottom
        barcode_h = int(1.2 * config.DPI)
        grid_bottom = dims["full_height_px"] - dims["bleed_px"] - safe - barcode_h - 60
        grid_avail_h = grid_bottom - grid_top

        padding = 30  # Between thumbnails
        thumb_w = (back_area_w - (grid_cols - 1) * padding) // grid_cols
        thumb_h = (grid_avail_h - (grid_rows - 1) * padding) // grid_rows

        # Keep aspect ratio (portrait pages are taller than wide)
        page_ratio = 3300 / 2550  # ~1.294
        if thumb_h / thumb_w > page_ratio:
            thumb_h = int(thumb_w * page_ratio)
        else:
            thumb_w = int(thumb_h / page_ratio)

        # Recalculate grid dimensions to center
        grid_w = grid_cols * thumb_w + (grid_cols - 1) * padding
        grid_h = grid_rows * thumb_h + (grid_rows - 1) * padding
        grid_x_start = dims["bleed_px"] + (dims["trim_w_px"] - grid_w) // 2
        grid_y_start = grid_top + (grid_avail_h - grid_h) // 2

        for idx, (img_type, img) in enumerate(sample_images[:grid_cols * grid_rows]):
            row = idx // grid_cols
            col = idx % grid_cols
            x = grid_x_start + col * (thumb_w + padding)
            y = grid_y_start + row * (thumb_h + padding)

            # Resize to thumbnail
            thumb = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)

            # Add thin border
            border = 3
            bordered = Image.new("RGB", (thumb_w + 2 * border, thumb_h + 2 * border), (180, 180, 180))
            bordered.paste(thumb, (border, border))

            # Add subtle shadow
            shadow_offset = 4
            draw.rectangle(
                [x + shadow_offset, y + shadow_offset,
                 x + thumb_w + 2 * border + shadow_offset, y + thumb_h + 2 * border + shadow_offset],
                fill=(200, 200, 200),
            )

            cover.paste(bordered, (x, y))

        # Refresh draw after pasting images
        draw = ImageDraw.Draw(cover)

        print(f"  Placed {len(sample_images)} sample pages on back cover.")

    # Barcode placeholder (KDP adds barcode here)
    barcode_w = int(2 * config.DPI)
    barcode_h = int(1.2 * config.DPI)
    barcode_x = dims["bleed_px"] + dims["trim_w_px"] - safe - barcode_w
    barcode_y = dims["full_height_px"] - dims["bleed_px"] - safe - barcode_h
    draw.rectangle(
        [barcode_x, barcode_y, barcode_x + barcode_w, barcode_y + barcode_h],
        fill="white",
        outline=(200, 200, 200),
    )
    barcode_font = get_font(20)
    draw.text(
        (barcode_x + 10, barcode_y + barcode_h // 2 - 10),
        "BARCODE AREA (KDP auto-generates)",
        font=barcode_font,
        fill=(180, 180, 180),
    )

    # --- Save PNG + PDF ---
    os.makedirs(config.COVERS_DIR, exist_ok=True)
    png_path = os.path.join(config.COVERS_DIR, f"{theme}_cover.png")
    pdf_path = os.path.join(config.COVERS_DIR, f"{theme}_cover.pdf")

    cover.save(png_path, "PNG", dpi=(config.DPI, config.DPI))

    # Save as PDF (KDP requires PDF for cover upload)
    cover_cmyk = cover.convert("RGB")
    cover_cmyk.save(pdf_path, "PDF", resolution=config.DPI)

    print(f"\nCover saved:")
    print(f"  PNG: {png_path}")
    print(f"  PDF: {pdf_path} (upload this to KDP)")
    print(f"Size: {cover.size[0]} x {cover.size[1]} px")

    return pdf_path


def main():
    parser = argparse.ArgumentParser(description="Generate KDP coloring book cover")
    parser.add_argument(
        "--theme",
        required=True,
        choices=config.THEMES.keys(),
        help="Coloring book theme",
    )
    parser.add_argument(
        "--author",
        type=str,
        default="",
        help="Author name to display on cover",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Custom book title (default: from config)",
    )
    parser.add_argument(
        "--kdp-width",
        type=float,
        default=None,
        help="Exact cover width in inches from KDP (overrides calculated width)",
    )
    parser.add_argument(
        "--kdp-height",
        type=float,
        default=None,
        help="Exact cover height in inches from KDP (overrides calculated height)",
    )
    args = parser.parse_args()

    build_cover(args.theme, args.author, args.title, args.kdp_width, args.kdp_height)


if __name__ == "__main__":
    main()
