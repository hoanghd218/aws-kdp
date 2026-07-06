#!/usr/bin/env python3
"""
Shared image generation providers for KDP coloring book pipeline.
Supports: AI33, Bimai, NanoPic, Kie.ai.
"""
from __future__ import annotations

import base64
import io
import json
import os
import sys
import time
import threading

import requests
from PIL import Image

import config


# ── NanoPic Token Pool ───────────────────────────────────────────────
class NanoPickTokenPool:
    """Thread-safe round-robin pool for multiple NANOPIC_ACCESS_TOKENs."""

    def __init__(self):
        raw = os.getenv("NANOPIC_ACCESS_TOKEN", "")
        self._tokens = [t.strip() for t in raw.split(",") if t.strip()]
        self._index = 0
        self._lock = threading.Lock()
        if self._tokens:
            print(f"  NanoPic token pool initialised with {len(self._tokens)} token(s)")
        else:
            print("  Warning: No NANOPIC_ACCESS_TOKEN found in .env")

    @property
    def size(self) -> int:
        return len(self._tokens)

    def next(self) -> str:
        """Return the next token in round-robin order (thread-safe)."""
        with self._lock:
            if not self._tokens:
                raise RuntimeError("No NANOPIC_ACCESS_TOKEN available")
            token = self._tokens[self._index % len(self._tokens)]
            self._index += 1
            return token


# Singleton — created once at module import time
_nanopic_pool: NanoPickTokenPool | None = None


def get_nanopic_pool() -> NanoPickTokenPool:
    global _nanopic_pool
    if _nanopic_pool is None:
        _nanopic_pool = NanoPickTokenPool()
    return _nanopic_pool


def generate_image_ai33(prompt: str, aspect_ratio: str = "1:1") -> Image.Image | None:
    """Generate an image using AI33 API."""
    api_key = os.getenv("AI33_KEY")
    if not api_key:
        print("Error: AI33_KEY not found in .env")
        sys.exit(1)

    headers = {"xi-api-key": api_key}
    model_params = json.dumps({
        "aspect_ratio": aspect_ratio,
        "resolution": config.AI33_RESOLUTION,
    })

    for attempt in range(config.MAX_RETRIES):
        try:
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
                        print("  Warning: Task done but no images returned")
                        break
                    image_url = images[0].get("imageUrl")
                    if not image_url:
                        print("  Warning: No imageUrl in result")
                        break
                    img_resp = requests.get(image_url)
                    img_resp.raise_for_status()
                    return Image.open(io.BytesIO(img_resp.content))

                elif status.get("status") == "error":
                    print(f"  AI33 error: {status.get('error_message', 'Unknown error')}")
                    break
                else:
                    progress = status.get("progress", 0)
                    if elapsed % 15 == 0:
                        print(f"  Polling... status={status.get('status')} progress={progress}%")

            if elapsed >= config.AI33_POLL_TIMEOUT:
                print(f"  Timeout waiting for AI33 task {task_id}")

        except Exception as e:
            print(f"  Error (attempt {attempt + 1}/{config.MAX_RETRIES}): {e}")
            if attempt < config.MAX_RETRIES - 1:
                time.sleep(config.REQUEST_DELAY_SECONDS)

    return None



def generate_image_nanopic(prompt: str, aspect_ratio: str = "1:1") -> Image.Image | None:
    """Generate an image using NanoPic API (nanoai.pics)."""
    api_key = os.getenv("NANOPIC_API_KEY")
    pool = get_nanopic_pool()
    if not api_key or pool.size == 0:
        print("Error: NANOPIC_API_KEY or NANOPIC_ACCESS_TOKEN not found in .env")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    nanopic_ar = config.NANOPIC_ASPECT_RATIOS.get(aspect_ratio, "IMAGE_ASPECT_RATIO_SQUARE")

    for attempt in range(config.MAX_RETRIES):
        # Rotate token on each attempt so a bad/expired token gets skipped
        access_token = pool.next()
        token_tail = access_token[-10:] if len(access_token) >= 10 else access_token
        try:
            payload = {
                "accessToken": access_token,
                "promptText": prompt,
                "imageUrls": [],
                "aspectRatio": nanopic_ar,
                "imageModel": config.NANOPIC_MODEL,
            }
            resp = requests.post(config.NANOPIC_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            result = resp.json()

            if not result.get("success"):
                print(f"  NanoPic submit failed (token ...{token_tail}): {result}")
                continue

            task_id = result.get("taskId") or result.get("data", {}).get("taskId")
            if not task_id:
                for key in result:
                    if "task" in key.lower() and isinstance(result[key], str):
                        task_id = result[key]
                        break
            if not task_id:
                print(f"  NanoPic submit failed (attempt {attempt + 1}): no taskId in {result}")
                continue

            print(f"  NanoPic task submitted: {task_id}")

            elapsed = 0
            while elapsed < config.NANOPIC_POLL_TIMEOUT:
                time.sleep(config.NANOPIC_POLL_INTERVAL)
                elapsed += config.NANOPIC_POLL_INTERVAL

                status_resp = requests.get(
                    f"{config.NANOPIC_STATUS_URL}?taskId={task_id}",
                    headers=headers,
                )
                status_resp.raise_for_status()
                status = status_resp.json()

                code = status.get("code", "")
                data = status.get("data") or {}

                # Success: code=="success" and data.fifeUrl present
                if code == "success" and data.get("fifeUrl"):
                    image_url = data["fifeUrl"]
                    img_resp = requests.get(image_url)
                    img_resp.raise_for_status()
                    return Image.open(io.BytesIO(img_resp.content))

                # Failure states
                if code in ("error", "failed", "fail"):
                    error_msg = status.get("message", "Unknown error")
                    detail = data.get("error") or {}
                    if detail:
                        error_msg = f"{error_msg} ({detail.get('status', '')}: {detail.get('message', '')})"
                    print(f"  NanoPic error (token ...{token_tail}): {error_msg}")
                    break

                # code="processing" / "pending" / empty — keep polling
                if elapsed % 15 == 0:
                    print(f"  Polling... status={code or 'pending'}")

            if elapsed >= config.NANOPIC_POLL_TIMEOUT:
                print(f"  Timeout waiting for NanoPic task {task_id}")

        except Exception as e:
            print(f"  Error (attempt {attempt + 1}/{config.MAX_RETRIES}): {e}")
            if attempt < config.MAX_RETRIES - 1:
                time.sleep(config.REQUEST_DELAY_SECONDS)

    return None


def generate_image_kie(prompt: str, aspect_ratio: str = "3:4") -> Image.Image | None:
    """Generate an image using Kie.ai API."""
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("Error: KIE_API_KEY not found in .env")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.KIE_MODEL,
        "input": {
            "prompt": prompt,
            "image_input": [],
            "aspect_ratio": aspect_ratio,
            "resolution": config.KIE_RESOLUTION,
            "output_format": "png",
        },
    }

    for attempt in range(config.MAX_RETRIES):
        try:
            resp = requests.post(config.KIE_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            result = resp.json()

            if result.get("code") != 200:
                print(f"  Kie.ai submit failed (attempt {attempt + 1}): {result.get('msg', result)}")
                continue

            task_id = result.get("data", {}).get("taskId")
            if not task_id:
                print(f"  Kie.ai submit failed (attempt {attempt + 1}): no taskId in {result}")
                continue

            print(f"  Kie.ai task submitted: {task_id}")

            elapsed = 0
            while elapsed < config.KIE_POLL_TIMEOUT:
                time.sleep(config.KIE_POLL_INTERVAL)
                elapsed += config.KIE_POLL_INTERVAL

                status_resp = requests.get(
                    f"{config.KIE_STATUS_URL}?taskId={task_id}",
                    headers=headers,
                )
                status_resp.raise_for_status()
                status = status_resp.json()
                task_data = status.get("data", {})
                task_state = task_data.get("state", "")

                if task_state == "success":
                    result_json_str = task_data.get("resultJson", "")
                    if result_json_str:
                        result_json = json.loads(result_json_str)
                        urls = result_json.get("resultUrls", [])
                        if urls:
                            img_resp = requests.get(urls[0])
                            img_resp.raise_for_status()
                            return Image.open(io.BytesIO(img_resp.content))
                    print("  Warning: Kie.ai task succeeded but no result URLs")
                    break

                elif task_state == "failed":
                    fail_msg = task_data.get("failMsg", "Unknown error")
                    print(f"  Kie.ai error: {fail_msg}")
                    break
                else:
                    if elapsed % 15 == 0:
                        print(f"  Polling... state={task_state}")

            if elapsed >= config.KIE_POLL_TIMEOUT:
                print(f"  Timeout waiting for Kie.ai task {task_id}")

        except Exception as e:
            print(f"  Error (attempt {attempt + 1}/{config.MAX_RETRIES}): {e}")
            if attempt < config.MAX_RETRIES - 1:
                time.sleep(config.REQUEST_DELAY_SECONDS)

    return None


def _decode_image_payload(obj: dict) -> Image.Image | None:
    """Turn an OpenAI-style image record into a PIL Image.

    Accepts either {"b64_json": "..."} or {"url": "..."}.
    """
    b64 = obj.get("b64_json") or obj.get("image_base64") or obj.get("b64")
    if b64:
        if "," in b64 and b64.strip().startswith("data:"):
            b64 = b64.split(",", 1)[1]
        return Image.open(io.BytesIO(base64.b64decode(b64)))
    url = obj.get("url") or obj.get("image_url")
    if url:
        img_resp = requests.get(url)
        img_resp.raise_for_status()
        return Image.open(io.BytesIO(img_resp.content))
    return None


def _extract_image_from_event(payload: dict) -> Image.Image | None:
    """Pull an image out of a parsed SSE/JSON payload, trying common shapes."""
    # Final OpenAI images response: {"data": [{"b64_json": ...}]}
    data = payload.get("data")
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                img = _decode_image_payload(item)
                if img is not None:
                    return img
    # Streaming completion events: top-level b64_json / url
    img = _decode_image_payload(payload)
    if img is not None:
        return img
    return None


_REF_MAX_PX = 1024  # resize local reference images to keep payloads small


def _load_reference_image(ref: str) -> str:
    """Return a reference image as a data URI or URL for the 'image' API field.

    Accepts:
      - https?:// URL  → returned as-is
      - data:image/... → returned as-is
      - local file path → resize to max _REF_MAX_PX, base64-encode as JPEG
    """
    if ref.startswith("data:") or ref.startswith("http://") or ref.startswith("https://"):
        return ref
    img = Image.open(ref).convert("RGB")
    if max(img.size) > _REF_MAX_PX:
        img.thumbnail((_REF_MAX_PX, _REF_MAX_PX), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"


def generate_image_chatgpt(
    prompt: str,
    aspect_ratio: str = "1:1",
    reference_image: str | list[str] | None = None,
) -> Image.Image | None:
    """Generate an image via an OpenAI-compatible /v1/images/generations endpoint.

    Streams the response as Server-Sent Events (Accept: text/event-stream) and
    keeps the last image found (final/completed event wins over partials).

    Args:
        reference_image: Optional reference image(s) for style/composition guidance.
                         str  → single image, sent as "image" in the payload.
                         list → multiple images, sent as "images" in the payload.
                         Each item may be a URL, local file path, or data URI.
    """
    api_key = os.getenv("CHATGPT_API_KEY")
    if not api_key:
        print("Error: CHATGPT_API_KEY not found in .env")
        sys.exit(1)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Accept": "text/event-stream",
    }
    size = config.CHATGPT_SIZES.get(aspect_ratio, "1024x1024")
    payload = {
        "model": config.CHATGPT_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": config.CHATGPT_QUALITY,
        "background": "auto",
        "image_detail": "high",
        "output_format": "png",
    }
    if isinstance(reference_image, list):
        payload["images"] = [_load_reference_image(r) for r in reference_image]
    elif reference_image:
        payload["image"] = _load_reference_image(reference_image)

    for attempt in range(config.MAX_RETRIES):
        last_image: Image.Image | None = None
        try:
            resp = requests.post(
                config.CHATGPT_API_URL,
                headers=headers,
                json=payload,
                stream=True,
                timeout=config.CHATGPT_POLL_TIMEOUT,
            )

            # Handle 429 rate limit: parse reset time from body and wait
            if resp.status_code == 429:
                wait = config.REQUEST_DELAY_SECONDS
                try:
                    body = resp.json()
                    msg = str(body.get("error", {}).get("message", ""))
                    import re as _re
                    m = _re.search(r"reset after (\d+)m?\s*(\d+)?s", msg)
                    if m:
                        mins = int(m.group(1)) if m.group(1) else 0
                        secs = int(m.group(2)) if m.group(2) else 0
                        # if pattern is "Xm Ys" or just "Xs"
                        if "m" in msg[m.start():m.end()]:
                            wait = mins * 60 + secs + 5
                        else:
                            wait = mins + 5  # "reset after Xs" — group(1) is seconds
                except Exception:
                    wait = 90
                print(f"  429 rate limit (attempt {attempt + 1}/{config.MAX_RETRIES}) — waiting {wait}s...")
                time.sleep(wait)
                continue

            resp.raise_for_status()

            for raw in resp.iter_lines(decode_unicode=True):
                if not raw:
                    continue
                line = raw.strip()
                if line.startswith("data:"):
                    line = line[len("data:"):].strip()
                if not line or line == "[DONE]":
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("error"):
                    print(f"  ChatGPT error: {event['error']}")
                    last_image = None
                    break
                img = _extract_image_from_event(event)
                if img is not None:
                    last_image = img  # keep latest; final event overwrites partials

            if last_image is not None:
                return last_image
            print(f"  ChatGPT: no image in stream (attempt {attempt + 1}/{config.MAX_RETRIES})")

        except Exception as e:
            print(f"  Error (attempt {attempt + 1}/{config.MAX_RETRIES}): {e}")

        if attempt < config.MAX_RETRIES - 1:
            time.sleep(config.REQUEST_DELAY_SECONDS)

    return None


# --- Dispatcher ---

RENDERERS = {
    "ai33": generate_image_ai33,
    "nanopic": generate_image_nanopic,
    "kie": generate_image_kie,
    "chatgpt": generate_image_chatgpt,
}

RENDERER_CHOICES = list(RENDERERS.keys())

DEFAULT_RENDERER = os.getenv("IMAGE_RENDERER", "chatgpt").lower()
if DEFAULT_RENDERER not in RENDERERS:
    print(f"Warning: IMAGE_RENDERER='{DEFAULT_RENDERER}' in .env is not valid. Using 'chatgpt'.")
    DEFAULT_RENDERER = "chatgpt"


def generate_image(
    prompt: str,
    renderer: str | None = None,
    aspect_ratio: str = "1:1",
    reference_image: str | list[str] | None = None,
) -> Image.Image | None:
    """Generate an image using the specified renderer.

    Args:
        prompt: The text prompt for image generation.
        renderer: One of 'ai33', 'nanopic', 'kie', 'chatgpt'.
        aspect_ratio: Aspect ratio string (e.g. '1:1', '3:4', '9:16').
        reference_image: Optional reference image(s) — URL, local path, or data URI.
                         str → single ("image"), list[str] → multi ("images").
                         Currently supported by the 'chatgpt' renderer only.

    Returns:
        PIL Image or None on failure.
    """
    if renderer is None:
        renderer = DEFAULT_RENDERER
    fn = RENDERERS.get(renderer)
    if not fn:
        print(f"Error: Unknown renderer '{renderer}'. Choose from: {RENDERER_CHOICES}")
        sys.exit(1)

    kwargs: dict = {"aspect_ratio": aspect_ratio}
    if reference_image is not None and renderer == "chatgpt":
        kwargs["reference_image"] = reference_image
    return fn(prompt, **kwargs)
