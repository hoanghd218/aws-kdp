"""
Configuration for KDP Coloring Book Generator.
All measurements based on Amazon KDP paperback specifications.
"""

# --- Page Dimensions ---
# Supported page sizes for KDP
PAGE_SIZES = {
    "8.5x11": {
        "width": 8.5,
        "height": 11.0,
        "aspect_ratio": "3:4",       # For Gemini API
        "ai33_aspect_ratio": "3:4",  # For AI33 API
        "label": "8.5\" x 11\" (Portrait)",
    },
    "8.5x8.5": {
        "width": 8.5,
        "height": 8.5,
        "aspect_ratio": "1:1",       # For Gemini API
        "ai33_aspect_ratio": "1:1",  # For AI33 API
        "label": "8.5\" x 8.5\" (Square)",
    },
}

# Default page size
DEFAULT_PAGE_SIZE = "8.5x11"

# Legacy defaults (8.5x11) — used when --size is not specified
PAGE_WIDTH_INCHES = 8.5
PAGE_HEIGHT_INCHES = 11.0
DPI = 300
MARGIN_INCHES = 0.25

# Derived pixel dimensions (default 8.5x11)
PAGE_WIDTH_PX = int(PAGE_WIDTH_INCHES * DPI)   # 2550
PAGE_HEIGHT_PX = int(PAGE_HEIGHT_INCHES * DPI)  # 3300
MARGIN_PX = int(MARGIN_INCHES * DPI)            # 75

# Safe drawing area (inside margins)
SAFE_WIDTH_PX = PAGE_WIDTH_PX - (2 * MARGIN_PX)   # 2400
SAFE_HEIGHT_PX = PAGE_HEIGHT_PX - (2 * MARGIN_PX)  # 3150


def get_page_dims(size_key: str = DEFAULT_PAGE_SIZE) -> dict:
    """Return pixel dimensions for a given page size key."""
    ps = PAGE_SIZES[size_key]
    w = int(ps["width"] * DPI)
    h = int(ps["height"] * DPI)
    m = int(MARGIN_INCHES * DPI)
    return {
        "width_inches": ps["width"],
        "height_inches": ps["height"],
        "width_px": w,
        "height_px": h,
        "margin_px": m,
        "safe_width_px": w - 2 * m,
        "safe_height_px": h - 2 * m,
        "aspect_ratio": ps["aspect_ratio"],
        "ai33_aspect_ratio": ps["ai33_aspect_ratio"],
    }

# --- Gemini API ---
GEMINI_MODEL = "gemini-3.1-flash-image-preview"  # Nano Banana Pro - fast image generation
REQUEST_DELAY_SECONDS = 3  # Min delay between API calls (20 requests/min)
MAX_PARALLEL_WORKERS = 5   # Concurrent image generation threads
MAX_RETRIES = 3

# --- AI33 API ---
AI33_API_URL = "https://api.ai33.pro/v1i/task/generate-image"
AI33_STATUS_URL = "https://api.ai33.pro/v1/task"
AI33_MODEL_ID = "gemini-3.1-flash-image-preview"
AI33_RESOLUTION = "2K"
AI33_ASPECT_RATIO = "3:4"  # Portrait for coloring books
AI33_POLL_INTERVAL = 5  # Seconds between status polls
AI33_POLL_TIMEOUT = 300  # Max seconds to wait for image generation

# --- Book Settings ---
COLORING_PAGES_PER_BOOK = 30
TARGET_AGE = "6-12"

# --- Themes ---
THEMES = {
    "cute_animals": {
        "name": "Cute Animals",
        "book_title": "Adorable Animals Coloring Book for Kids Ages 6-12",
        "prompt_file": "prompts/cute_animals.txt",
    },
    "dinosaurs": {
        "name": "Dinosaurs",
        "book_title": "Amazing Dinosaurs Coloring Book for Kids Ages 6-12",
        "prompt_file": "prompts/dinosaurs.txt",
    },
    "vehicles": {
        "name": "Vehicles",
        "book_title": "Cool Vehicles Coloring Book for Kids Ages 6-12",
        "prompt_file": "prompts/vehicles.txt",
    },
    "unicorn_fantasy": {
        "name": "Unicorn & Fantasy",
        "book_title": "Magical Unicorns & Fantasy Coloring Book for Kids Ages 6-12",
        "prompt_file": "prompts/unicorn_fantasy.txt",
    },
    "cute_animals_fun": {
        "name": "Adorable Animals Coloring Fun",
        "book_title": "Adorable Animals Coloring Fun for Kids Ages 6-12",
        "prompt_file": "prompts/cute_animals_fun.txt",
    },
    "cozy_cat_cafe": {
        "name": "Whiskers & Warmth",
        "book_title": "Whiskers & Warmth: A Cozy Cat Café Coloring Book for Adults",
        "prompt_file": "prompts/cozy_cat_cafe.txt",
    },
    "cute_astronaut": {
        "name": "Stars & Serenity",
        "book_title": "Stars & Serenity: A Cozy Astronaut Coloring Book for Adults",
        "prompt_file": "prompts/cute_astronaut.txt",
    },
    "cute_aliens": {
        "name": "Cosmic Cuties",
        "book_title": "Cosmic Cuties: A Cozy Alien Coloring Book for Adults",
        "prompt_file": "prompts/cute_aliens.txt",
    },
    "cozy_cats_daily_life": {
        "name": "Cozy Cats Coloring Book",
        "book_title": "Cozy Cats Coloring Book: Cute Cats in Daily Life with Easy and Bold Designs for Relaxation",
        "prompt_file": "prompts/cozy_cats_daily_life.txt",
    },
    "self_care_girl": {
        "name": "Self-Care Girl Coloring Book",
        "book_title": "Self-Care Girl Coloring Book: Cute Cozy Daily Routines for Relaxation and Stress Relief",
        "prompt_file": "prompts/self_care_girl.txt",
    },
    "sinh_vat_bien": {
        "name": "Ocean Friends",
        "book_title": "Ocean Friends Coloring Book for Kids Ages 6-12",
        "prompt_file": "prompts/sinh_vat_bien.txt",
    },
    "cozy_kitchen": {
        "name": "Cozy Kitchen",
        "book_title": "Cozy Kitchen — Bold and Easy Coloring Book",
        "prompt_file": "prompts/cozy_kitchen.txt",
        "page_size": "8.5x8.5",
    },
    "cottage_garden": {
        "name": "Cottage Garden",
        "book_title": "Cottage Garden — Bold and Easy Coloring Book",
        "prompt_file": "prompts/cottage_garden.txt",
        "page_size": "8.5x8.5",
    },
    "cat_lovers_bold_easy": {
        "name": "Cat Lovers Bold and Easy",
        "book_title": "Cat Lovers Coloring Book: Bold and Easy Designs for Adults",
        "prompt_file": "prompts/cat_lovers_bold_easy.txt",
        "page_size": "8.5x8.5",
    },
}

# --- Paths ---
OUTPUT_IMAGES_DIR = "output/images"
OUTPUT_BOOKS_DIR = "output/books"
COVERS_DIR = "covers"

# --- Base Prompt ---
BASE_PROMPT = """Create a children's coloring book page in PORTRAIT orientation (taller than wide). Requirements:
- PORTRAIT layout - the image must be taller than it is wide
- Black and white line art ONLY
- NO shading, NO gray tones, NO gradients, NO filled areas
- Thick, clean, bold outlines
- Simple enough for kids ages {age} to color
- White background
- The drawing should fill most of the page vertically
- Leave adequate spacing from edges
- Style: cute, friendly, appealing to children
- Single subject centered on page
- NO borders, NO frames, NO rectangular boundary lines around the image

Subject: {subject}"""
