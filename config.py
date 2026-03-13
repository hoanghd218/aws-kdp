"""
Configuration for KDP Coloring Book Generator.
All measurements based on Amazon KDP paperback specifications.
"""

# --- Page Dimensions ---
PAGE_WIDTH_INCHES = 8.5
PAGE_HEIGHT_INCHES = 11.0
DPI = 300
MARGIN_INCHES = 0.25

# Derived pixel dimensions
PAGE_WIDTH_PX = int(PAGE_WIDTH_INCHES * DPI)   # 2550
PAGE_HEIGHT_PX = int(PAGE_HEIGHT_INCHES * DPI)  # 3300
MARGIN_PX = int(MARGIN_INCHES * DPI)            # 75

# Safe drawing area (inside margins)
SAFE_WIDTH_PX = PAGE_WIDTH_PX - (2 * MARGIN_PX)   # 2400
SAFE_HEIGHT_PX = PAGE_HEIGHT_PX - (2 * MARGIN_PX)  # 3150

# --- Gemini API ---
GEMINI_MODEL = "gemini-3.1-flash-image-preview"  # Nano Banana Pro - fast image generation
REQUEST_DELAY_SECONDS = 5  # Delay between API calls to avoid rate limits
MAX_RETRIES = 3

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
