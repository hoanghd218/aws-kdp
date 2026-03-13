#!/usr/bin/env python3
"""
Generate coloring book page images using Gemini API (Nano Banana Pro).
Each image is a black-and-white line art suitable for kids to color.
"""

import argparse
import io
import json
import os
import sys
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, ImageEnhance, ImageOps

import config

load_dotenv()


def get_client():
    """Initialize Gemini API client."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env file")
        print("Copy .env.example to .env and add your API key")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def load_subjects(theme: str) -> list[str]:
    """Load subject list from prompt template file."""
    theme_config = config.THEMES.get(theme)
    if not theme_config:
        print(f"Error: Unknown theme '{theme}'")
        print(f"Available themes: {', '.join(config.THEMES.keys())}")
        sys.exit(1)

    prompt_file = theme_config["prompt_file"]
    if not os.path.exists(prompt_file):
        print(f"Error: Prompt file not found: {prompt_file}")
        sys.exit(1)

    with open(prompt_file, "r") as f:
        subjects = [line.strip() for line in f if line.strip()]
    return subjects


def load_plan_prompts(plan_path: str) -> tuple[str, list[str]]:
    """Load theme key and full prompts from a plan JSON file.

    Returns:
        (theme_key, list_of_full_prompts)
    """
    if not os.path.exists(plan_path):
        print(f"Error: Plan file not found: {plan_path}")
        sys.exit(1)

    with open(plan_path, "r") as f:
        plan = json.load(f)

    theme_key = plan.get("theme_key")
    if not theme_key:
        print("Error: Plan file missing 'theme_key'")
        sys.exit(1)

    page_prompts = plan.get("page_prompts", [])
    if not page_prompts:
        print("Error: Plan file has no 'page_prompts'")
        sys.exit(1)

    return theme_key, page_prompts


def generate_coloring_page(client, subject: str, use_raw_prompt: bool = False) -> Image.Image | None:
    """Generate a single coloring page image using Gemini API (Nano Banana Pro).

    Args:
        client: Gemini API client.
        subject: Either a subject description (formatted with BASE_PROMPT) or a full prompt.
        use_raw_prompt: If True, use subject as the complete prompt without BASE_PROMPT formatting.
    """
    if use_raw_prompt:
        prompt = subject
    else:
        prompt = config.BASE_PROMPT.format(age=config.TARGET_AGE, subject=subject)

    for attempt in range(config.MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio="3:4",
                    ),
                ),
            )

            # Extract image from response parts
            for part in response.parts:
                if part.text is not None:
                    print(f"  Model note: {part.text[:100]}")
                elif part.inline_data is not None:
                    # Convert raw bytes to PIL Image
                    image_bytes = part.inline_data.data
                    pil_image = Image.open(io.BytesIO(image_bytes))
                    return pil_image

            print(f"  Warning: No image in response (attempt {attempt + 1})")

        except Exception as e:
            print(f"  Error (attempt {attempt + 1}/{config.MAX_RETRIES}): {e}")
            if attempt < config.MAX_RETRIES - 1:
                time.sleep(config.REQUEST_DELAY_SECONDS * 2)

    return None


def post_process(image: Image.Image) -> Image.Image:
    """Post-process generated image for coloring book quality."""
    # Convert to grayscale
    image = ImageOps.grayscale(image)

    # Fit image into safe area while preserving aspect ratio (no distortion)
    image = ImageOps.contain(
        image,
        (config.SAFE_WIDTH_PX, config.SAFE_HEIGHT_PX),
        Image.Resampling.LANCZOS,
    )

    # Increase contrast to make lines crisp black on white
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # Increase brightness to ensure white background
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.3)

    # Create full page with margins (white background), center the image
    full_page = Image.new("L", (config.PAGE_WIDTH_PX, config.PAGE_HEIGHT_PX), 255)
    paste_x = (config.PAGE_WIDTH_PX - image.size[0]) // 2
    paste_y = (config.PAGE_HEIGHT_PX - image.size[1]) // 2
    full_page.paste(image, (paste_x, paste_y))

    return full_page


def main():
    parser = argparse.ArgumentParser(description="Generate coloring book images")
    parser.add_argument(
        "--theme",
        choices=config.THEMES.keys(),
        help="Coloring book theme (required unless --plan is used)",
    )
    parser.add_argument(
        "--plan",
        type=str,
        default=None,
        help="Path to a plan JSON file (from plan_book.py output)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=config.COLORING_PAGES_PER_BOOK,
        help=f"Number of pages to generate (default: {config.COLORING_PAGES_PER_BOOK})",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Start index in subject list (for resuming)",
    )
    args = parser.parse_args()

    # Determine mode: plan-based or theme-based
    use_raw_prompt = False
    if args.plan:
        theme_key, prompts = load_plan_prompts(args.plan)
        use_raw_prompt = True
        theme_name = theme_key
        # Use theme config name if available, otherwise use theme_key
        if theme_key in config.THEMES:
            theme_name = config.THEMES[theme_key]["name"]
    elif args.theme:
        theme_key = args.theme
        theme_name = config.THEMES[args.theme]["name"]
        prompts = load_subjects(args.theme)
    else:
        parser.error("--theme is required unless --plan is provided")

    client = get_client()

    # Limit to requested count
    end_idx = min(args.start + args.count, len(prompts))
    prompts = prompts[args.start : end_idx]

    output_dir = os.path.join(config.OUTPUT_IMAGES_DIR, theme_key)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Theme: {theme_name}")
    if use_raw_prompt:
        print(f"Plan: {args.plan}")
    print(f"Generating {len(prompts)} coloring pages...")
    print(f"Output: {output_dir}/")
    print()

    success_count = 0
    for i, prompt_text in enumerate(prompts):
        page_num = args.start + i + 1
        filename = f"page_{page_num:02d}.png"
        filepath = os.path.join(output_dir, filename)

        # Skip if already exists
        if os.path.exists(filepath):
            print(f"[{page_num}/{end_idx}] Skipping (exists): {filename}")
            success_count += 1
            continue

        display_text = prompt_text[:80] + "..." if len(prompt_text) > 80 else prompt_text
        print(f"[{page_num}/{end_idx}] Generating: {display_text}")

        image = generate_coloring_page(client, prompt_text, use_raw_prompt=use_raw_prompt)
        if image:
            processed = post_process(image)
            processed.save(filepath, "PNG", dpi=(config.DPI, config.DPI))
            print(f"  Saved: {filename}")
            success_count += 1
        else:
            print(f"  FAILED: Could not generate image")

        # Rate limiting
        if i < len(prompts) - 1:
            time.sleep(config.REQUEST_DELAY_SECONDS)

    print()
    print(f"Done! Generated {success_count}/{len(prompts)} pages")
    print(f"Output directory: {output_dir}/")


if __name__ == "__main__":
    main()
