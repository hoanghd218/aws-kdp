#!/usr/bin/env python3
"""
Generate coloring book page images using AI33 API.
Each image is a black-and-white line art suitable for coloring.
"""

import argparse
import io
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv
from PIL import Image, ImageEnhance, ImageOps

import config

load_dotenv()


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


def load_plan_prompts(plan_path: str) -> tuple[str, list[str], str | None]:
    """Load theme key, full prompts, and page_size from a plan JSON file.

    Returns:
        (theme_key, list_of_full_prompts, page_size_or_None)
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

    page_size = plan.get("page_size")  # e.g. "8.5x11" or "8.5x8.5"

    return theme_key, page_prompts, page_size


def generate_coloring_page(prompt: str, aspect_ratio: str = "3:4") -> Image.Image | None:
    """Generate a single coloring page image using AI33 API.

    Submits a task, polls for completion, downloads the result image.
    """
    api_key = os.getenv("AI33_KEY")
    if not api_key:
        print("Error: AI33_KEY not found in .env file")
        sys.exit(1)

    headers = {"xi-api-key": api_key}
    model_params = json.dumps({
        "aspect_ratio": aspect_ratio,
        "resolution": config.AI33_RESOLUTION,
    })

    for attempt in range(config.MAX_RETRIES):
        try:
            # Submit generation task
            resp = requests.post(
                config.AI33_API_URL,
                headers=headers,
                data={
                    "prompt": prompt,
                    "model_id": config.AI33_MODEL_ID,
                    "generations_count": "1",
                    "model_parameters": model_params,
                },
            )
            resp.raise_for_status()
            result = resp.json()

            if not result.get("success"):
                print(f"  AI33 submit failed (attempt {attempt + 1}): {result}")
                continue

            task_id = result["task_id"]
            credits_remaining = result.get("ec_remain_credits", "?")
            print(f"  Task submitted: {task_id} (credits remaining: {credits_remaining})")

            # Poll for completion
            elapsed = 0
            while elapsed < config.AI33_POLL_TIMEOUT:
                time.sleep(config.AI33_POLL_INTERVAL)
                elapsed += config.AI33_POLL_INTERVAL

                status_resp = requests.get(
                    f"{config.AI33_STATUS_URL}/{task_id}",
                    headers={"Content-Type": "application/json", "xi-api-key": api_key},
                )
                status_resp.raise_for_status()
                status = status_resp.json()

                if status.get("status") == "done":
                    images = status.get("metadata", {}).get("result_images", [])
                    if not images:
                        print(f"  Warning: Task done but no images returned")
                        break

                    image_url = images[0].get("imageUrl")
                    if not image_url:
                        print(f"  Warning: No imageUrl in result")
                        break

                    # Download the image
                    img_resp = requests.get(image_url)
                    img_resp.raise_for_status()
                    pil_image = Image.open(io.BytesIO(img_resp.content))
                    return pil_image

                elif status.get("status") == "error":
                    print(f"  AI33 error: {status.get('error_message', 'Unknown error')}")
                    break

                else:
                    progress = status.get("progress", 0)
                    if elapsed % 15 == 0:  # Log every 15 seconds
                        print(f"  Polling... status={status.get('status')} progress={progress}%")

            if elapsed >= config.AI33_POLL_TIMEOUT:
                print(f"  Timeout waiting for AI33 task {task_id}")

        except Exception as e:
            print(f"  Error (attempt {attempt + 1}/{config.MAX_RETRIES}): {e}")
            if attempt < config.MAX_RETRIES - 1:
                time.sleep(config.REQUEST_DELAY_SECONDS * 2)

    return None


def post_process(image: Image.Image, size_key: str = config.DEFAULT_PAGE_SIZE) -> Image.Image:
    """Post-process generated image for coloring book quality."""
    dims = config.get_page_dims(size_key)

    # Convert to grayscale
    image = ImageOps.grayscale(image)

    # Fit image into safe area while preserving aspect ratio (no distortion)
    image = ImageOps.contain(
        image,
        (dims["safe_width_px"], dims["safe_height_px"]),
        Image.Resampling.LANCZOS,
    )

    # Increase contrast to make lines crisp black on white
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # Increase brightness to ensure white background
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.3)

    # Create full page with margins (white background), center the image
    full_page = Image.new("L", (dims["width_px"], dims["height_px"]), 255)
    paste_x = (dims["width_px"] - image.size[0]) // 2
    paste_y = (dims["height_px"] - image.size[1]) // 2
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
    parser.add_argument(
        "--size",
        choices=config.PAGE_SIZES.keys(),
        default=config.DEFAULT_PAGE_SIZE,
        help=f"Page size (default: {config.DEFAULT_PAGE_SIZE})",
    )
    args = parser.parse_args()

    # Determine mode: plan-based or theme-based
    use_raw_prompt = False
    if args.plan:
        theme_key, prompts, plan_page_size = load_plan_prompts(args.plan)
        use_raw_prompt = True
        theme_name = theme_key
        # Auto-detect page size from plan if not explicitly set via CLI
        if plan_page_size and plan_page_size in config.PAGE_SIZES and args.size == config.DEFAULT_PAGE_SIZE:
            args.size = plan_page_size
        # Use theme config name if available, otherwise use theme_key
        if theme_key in config.THEMES:
            theme_name = config.THEMES[theme_key]["name"]
    elif args.theme:
        theme_key = args.theme
        theme_name = config.THEMES[args.theme]["name"]
        prompts = load_subjects(args.theme)
    else:
        parser.error("--theme is required unless --plan is provided")

    # Limit to requested count
    end_idx = min(args.start + args.count, len(prompts))
    prompts = prompts[args.start : end_idx]

    output_dir = os.path.join(config.OUTPUT_IMAGES_DIR, theme_key)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Theme: {theme_name}")
    if use_raw_prompt:
        print(f"Plan: {args.plan}")
    dims = config.get_page_dims(args.size)
    print(f"Renderer: AI33")
    print(f"Page size: {config.PAGE_SIZES[args.size]['label']}")
    print(f"Generating {len(prompts)} coloring pages...")
    print(f"Output: {output_dir}/")
    print()

    # --- Generate pages (parallel via AI33 async tasks) ---
    def _generate_one(i_prompt):
        i, prompt_text = i_prompt
        page_num = args.start + i + 1
        filename = f"page_{page_num:02d}.png"
        filepath = os.path.join(output_dir, filename)

        if os.path.exists(filepath):
            print(f"[{page_num}/{end_idx}] Skipping (exists): {filename}")
            return True

        display_text = prompt_text[:80] + "..." if len(prompt_text) > 80 else prompt_text
        print(f"[{page_num}/{end_idx}] Generating: {display_text}")

        if use_raw_prompt:
            full_prompt = prompt_text
        else:
            full_prompt = config.BASE_PROMPT.format(age=config.TARGET_AGE, subject=prompt_text)
        image = generate_coloring_page(full_prompt, aspect_ratio=dims["ai33_aspect_ratio"])

        if image:
            processed = post_process(image, size_key=args.size)
            processed.save(filepath, "PNG", dpi=(config.DPI, config.DPI))
            print(f"  Saved: {filename}")
            return True
        else:
            print(f"  FAILED: Could not generate image")
            return False

    tasks = list(enumerate(prompts))

    if len(tasks) > 1:
        from concurrent.futures import ThreadPoolExecutor
        workers = min(config.MAX_PARALLEL_WORKERS, len(tasks))
        print(f"Running {workers} parallel workers...\n")
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_generate_one, tasks))
        success_count = sum(1 for r in results if r)
    else:
        success_count = 0
        for task in tasks:
            if _generate_one(task):
                success_count += 1

    print()
    print(f"Done! Generated {success_count}/{len(prompts)} pages")
    print(f"Output directory: {output_dir}/")


if __name__ == "__main__":
    main()
