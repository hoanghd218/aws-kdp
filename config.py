"""
Configuration for KDP Coloring Book Generator.
All measurements based on Amazon KDP paperback specifications.
"""
import os

from dotenv import load_dotenv

load_dotenv()

# --- Author (from .env) ---
DEFAULT_AUTHOR_FIRST = os.getenv("AUTHOR_FIRST_NAME", "").strip()
DEFAULT_AUTHOR_LAST = os.getenv("AUTHOR_LAST_NAME", "").strip()
DEFAULT_AUTHOR = f"{DEFAULT_AUTHOR_FIRST} {DEFAULT_AUTHOR_LAST}".strip()

# --- Page Dimensions ---
# Supported page sizes for KDP
PAGE_SIZES = {
    "8.5x11": {
        "width": 8.5,
        "height": 11.0,
        "aspect_ratio": "3:4",       # For Gemini API
        "ai33_aspect_ratio": "3:4",  # For AI33 API
        "bimai_aspect_ratio": "9:16",  # For Bimai API
        "label": "8.5\" x 11\" (Portrait)",
    },
    "8.5x8.5": {
        "width": 8.5,
        "height": 8.5,
        "aspect_ratio": "1:1",       # For Gemini API
        "ai33_aspect_ratio": "1:1",  # For AI33 API
        "bimai_aspect_ratio": "1:1",  # For Bimai API
        "label": "8.5\" x 8.5\" (Square)",
    },
}

# Default page size
DEFAULT_PAGE_SIZE = "8.5x11"

# Legacy defaults (8.5x11) — used when --size is not specified
PAGE_WIDTH_INCHES = 8.5
PAGE_HEIGHT_INCHES = 11.0
DPI = 300
MARGIN_INCHES = 0.25  # Outside, top, bottom margins
GUTTER_MARGIN_INCHES = 0.25  # Default gutter (overridden by get_gutter_margin)

# Derived pixel dimensions (default 8.5x11)
PAGE_WIDTH_PX = int(PAGE_WIDTH_INCHES * DPI)   # 2550
PAGE_HEIGHT_PX = int(PAGE_HEIGHT_INCHES * DPI)  # 3300
MARGIN_PX = int(MARGIN_INCHES * DPI)            # 75

# Safe drawing area (inside margins)
SAFE_WIDTH_PX = PAGE_WIDTH_PX - (2 * MARGIN_PX)   # 2400
SAFE_HEIGHT_PX = PAGE_HEIGHT_PX - (2 * MARGIN_PX)  # 3150


def get_gutter_margin(page_count: int) -> float:
    """Return required gutter (inside) margin in inches based on KDP page count rules.

    KDP requirements:
    - 24-150 pages:  0.375"
    - 151-300 pages: 0.500"
    - 301-500 pages: 0.625"
    - 501-700 pages: 0.750"
    - 701-828 pages: 0.875"
    - <24 pages:     0.25" (standard)
    """
    if page_count >= 701:
        return 0.875
    elif page_count >= 501:
        return 0.75
    elif page_count >= 301:
        return 0.625
    elif page_count >= 151:
        return 0.5
    elif page_count >= 24:
        return 0.375
    else:
        return 0.25


def get_page_dims(size_key: str = DEFAULT_PAGE_SIZE, page_count: int = 0) -> dict:
    """Return pixel dimensions for a given page size key.

    If page_count > 0, includes gutter_margin calculated from KDP rules.
    """
    ps = PAGE_SIZES[size_key]
    w = int(ps["width"] * DPI)
    h = int(ps["height"] * DPI)
    m = int(MARGIN_INCHES * DPI)
    gutter = get_gutter_margin(page_count) if page_count > 0 else MARGIN_INCHES
    gutter_px = int(gutter * DPI)
    return {
        "width_inches": ps["width"],
        "height_inches": ps["height"],
        "width_px": w,
        "height_px": h,
        "margin_px": m,
        "margin_inches": MARGIN_INCHES,
        "gutter_margin_inches": gutter,
        "gutter_margin_px": gutter_px,
        "safe_width_px": w - m - gutter_px,
        "safe_height_px": h - 2 * m,
        "aspect_ratio": ps["aspect_ratio"],
        "ai33_aspect_ratio": ps["ai33_aspect_ratio"],
        "bimai_aspect_ratio": ps["bimai_aspect_ratio"],
    }

# --- Gemini API ---
GEMINI_MODEL = "gemini-3.1-flash-image-preview"  # Nano Banana Pro - fast image generation
REQUEST_DELAY_SECONDS = 3  # Min delay between API calls (20 requests/min)
MAX_PARALLEL_WORKERS = 3   # Concurrent image generation threads (reduced to avoid rate limits)
MAX_RETRIES = 3

# --- AI33 API ---
AI33_API_URL = "https://api.ai33.pro/v1i/task/generate-image"
AI33_STATUS_URL = "https://api.ai33.pro/v1/task"
AI33_MODEL_ID = "gemini-3.1-flash-image-preview"
AI33_RESOLUTION = "2K"
AI33_ASPECT_RATIO = "3:4"  # Portrait for coloring books
AI33_POLL_INTERVAL = 5  # Seconds between status polls
AI33_POLL_TIMEOUT = 300  # Max seconds to wait for image generation

# --- Bimai API (app.bimai.vn) ---
BIMAI_API_URL = "https://api.bimai.vn/api/v1/generate"
BIMAI_STATUS_URL = "https://api.bimai.vn/api/v1/tasks"
BIMAI_DISPLAY_NAME = "Google Flow"
BIMAI_PROVIDER = "Google Flow"
BIMAI_MODEL = "Google Flow"
BIMAI_POLL_INTERVAL = 5   # Seconds between status polls
BIMAI_POLL_TIMEOUT = 300  # Max seconds to wait for image generation

# --- NanoPic API (nanoai.pics) ---
NANOPIC_API_URL = "https://flow-api.nanoai.pics/api/v2/images/create"
NANOPIC_STATUS_URL = "https://flow-api.nanoai.pics/api/v2/task"
NANOPIC_MODEL = "GEM_PIX_2"
NANOPIC_POLL_INTERVAL = 5
NANOPIC_POLL_TIMEOUT = 300
NANOPIC_ASPECT_RATIOS = {
    "1:1": "IMAGE_ASPECT_RATIO_SQUARE",
    "3:4": "IMAGE_ASPECT_RATIO_PORTRAIT",
    "9:16": "IMAGE_ASPECT_RATIO_PORTRAIT",
    "4:3": "IMAGE_ASPECT_RATIO_LANDSCAPE",
    "16:9": "IMAGE_ASPECT_RATIO_LANDSCAPE",
}

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
    "cozy_spring_garden": {
        "name": "Cozy Spring Garden",
        "book_title": "Cozy Spring Garden \u2014 Bold and Easy Coloring Book",
        "prompt_file": "prompts/cozy_spring_garden.txt",
        "page_size": "8.5x8.5",
    },
    "easter_bold_easy_kids": {
        "name": "Easter Bold and Easy for Kids",
        "book_title": "Easter Coloring Book for Kids Ages 3-8: Bold and Easy Easter Egg, Bunny, and Spring Designs",
        "prompt_file": "prompts/easter_bold_easy_kids.txt",
        "page_size": "8.5x8.5",
    },
    "cottagecore_mushrooms": {
        "name": "Cottagecore Mushrooms & Woodland",
        "book_title": "Cottagecore Mushrooms & Woodland: A Cozy Coloring Book for Adults with Bold and Easy Designs",
        "prompt_file": "prompts/cottagecore_mushrooms.txt",
        "page_size": "8.5x8.5",
    },
    "mothers_day_floral": {
        "name": "Mother's Day Flowers",
        "book_title": "Mother's Day Flowers Coloring Book: A Beautiful Floral Gift for Mom",
        "prompt_file": "prompts/mothers_day_floral.txt",
        "page_size": "8.5x8.5",
    },
    "ocean_underwater_kids": {
        "name": "Ocean & Underwater Adventures",
        "book_title": "Ocean & Underwater Adventures Coloring Book for Kids Ages 3-8: Fun Sea Creatures with Bold and Easy Designs",
        "prompt_file": "prompts/ocean_underwater_kids.txt",
        "page_size": "8.5x8.5",
    },
    "monochrome_minimalist": {
        "name": "Monochrome Minimalist",
        "book_title": "Monochrome Minimalist Coloring Book: One Pen, Endless Calm — Bold and Easy Designs for Adults",
        "prompt_file": "prompts/monochrome_minimalist.txt",
        "page_size": "8.5x8.5",
    },
    "kawaii_food_sweets": {
        "name": "Kawaii Food & Sweets",
        "book_title": "Kawaii Food & Sweets Coloring Book: Cute Kawaii Food with Adorable Faces — Bold and Easy Designs for Kids, Teens & Adults",
        "prompt_file": "prompts/kawaii_food_sweets.txt",
        "page_size": "8.5x8.5",
    },
    "succulents_cacti": {
        "name": "Succulents & Cacti",
        "book_title": "Succulents & Cacti Coloring Book",
        "prompt_file": "output/succulents_cacti/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "vintage_travel_destinations": {
        "name": "Vintage Travel Destinations",
        "book_title": "Vintage Wanderlust: Coloring Book for Adults, Bold and Easy",
        "prompt_file": "output/vintage_travel_destinations/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "tech_boy_adventure": {
        "name": "The Boy Who Learned Tech",
        "book_title": "The Boy Who Learned Tech: A Coding Adventure Coloring Book for Kids Ages 6-12",
        "prompt_file": "prompts/tech_boy_adventure.txt",
    },
    "little_corner": {
        "name": "Hygge Havens",
        "book_title": "Little Corner: Coloring Book for Adults and Teens, Super Cute Designs of Cozy, Hygge Spaces for Relaxation",
        "prompt_file": "prompts/little_corner.txt",
    },
    "cozy_cat_kids": {
        "name": "Cozy Cats",
        "book_title": "Cozy Cats Coloring Book for Kids Ages 6-12",
        "prompt_file": "prompts/cozy_cat_kids.txt",
    },
    "cozy_dog_kids": {
        "name": "Cozy Dogs",
        "book_title": "Cozy Dogs Coloring Book for Kids Ages 6-12",
        "prompt_file": "prompts/cozy_dog_kids.txt",
    },
    "race_cars_vehicles": {
        "name": "Race Cars & Vehicles",
        "book_title": "Race Cars & Vehicles Coloring Book for Kids Ages 5-9",
        "prompt_file": "output/race_cars_vehicles/prompts.txt",
    },
    "airplanes_helicopters": {
        "name": "Airplanes & Helicopters",
        "book_title": "Airplanes and Helicopters Coloring Book for Kids Ages 3-7: 50 Bold and Easy Aircraft Designs with Planes, Helicopters, and Flying Fun",
        "prompt_file": "output/airplanes_helicopters/prompts.txt",
    },
    "flowers_garden_kids": {
        "name": "Flowers & Garden Kids",
        "book_title": "Flowers & Garden Coloring Book for Kids Ages 5-10: 50 Bold and Easy Flower Species, Garden Scenes, and Nature Designs",
        "prompt_file": "output/flowers_garden_kids/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "weather_seasons": {
        "name": "Weather & Seasons",
        "book_title": "Weather & Seasons Coloring Book for Kids Ages 4-8: 50 Bold and Easy Designs of Sun, Rain, Snow, and the Four Seasons",
        "prompt_file": "output/weather_seasons/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "alphabet_animals_abc": {
        "name": "Alphabet Animals ABC",
        "book_title": "Alphabet Animals ABC Coloring Book for Toddlers: Big Letters, Bold Lines, and Cute Animals for Ages 2-5",
        "prompt_file": "output/alphabet_animals_abc/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "numbers_counting": {
        "name": "Numbers & Counting",
        "book_title": "Numbers & Counting Coloring Book for Kids Ages 2-5: Bold and Easy",
        "prompt_file": "output/numbers_counting/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "summer_beach_fun": {
        "name": "Summer Beach Fun",
        "book_title": "Summer Beach Fun Coloring Book for Kids Ages 4-8: 50 Bold and Easy Beach Scenes with Sandcastles, Ocean Waves, and Summer Vacation Activities",
        "prompt_file": "output/summer_beach_fun/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "halloween_cute_spooky": {
        "name": "Halloween Cute & Spooky",
        "book_title": "Halloween Cute & Spooky Coloring Book for Kids Ages 3-7: 50 Big and Simple Halloween Designs with Friendly Ghosts, Pumpkins, and Kawaii Creatures",
        "prompt_file": "output/halloween_cute_spooky/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "summer_road_trip": {
        "name": "Summer Road Trip Adventure",
        "book_title": "Summer Road Trip Adventure Coloring Book for Kids Ages 4-8: 50 Bold and Easy Designs with Cars, Camping, Road Signs, and Vacation Fun",
        "prompt_file": "output/summer_road_trip/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "4th_july_patriotic": {
        "name": "4th of July Cute Patriotic",
        "book_title": "4th of July Coloring Book for Kids Ages 3-7: 50 Big and Simple Patriotic Designs with Cute Eagles, Fireworks, and Stars",
        "prompt_file": "output/4th_july_patriotic/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "sunflower_fields": {
        "name": "Sunflower Fields",
        "book_title": "Sunflower Fields Coloring Book: Beautiful Sunflowers, Farmhouse Scenes, and Golden Meadows with Bold and Easy Designs for Adults",
        "prompt_file": "output/sunflower_fields/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "rose_garden": {
        "name": "Rose Garden Collection",
        "book_title": "Rose Garden Collection Coloring Book: Beautiful Roses, Romantic Blooms, and Cozy Garden Scenes with Bold and Easy Designs for Adults",
        "prompt_file": "output/rose_garden/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "autumn_leaves_forest": {
        "name": "Autumn Leaves & Forest",
        "book_title": "Autumn Leaves & Forest Coloring Book: Cozy Fall Scenes with Bold and Easy Designs for Adults",
        "prompt_file": "output/autumn_leaves_forest/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "herb_garden_kitchen": {
        "name": "Herb Garden & Kitchen Herbs",
        "book_title": "Herb Garden & Kitchen Herbs Coloring Book: Cute Kawaii Herbs with Cozy Cottagecore Scenes for Adults",
        "prompt_file": "output/herb_garden_kitchen/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "cherry_blossom_garden": {
        "name": "Japanese Cherry Blossom Garden",
        "book_title": "Japanese Cherry Blossom Garden Coloring Book: Serene Temples, Torii Gates, and Sakura Scenes for Adults",
        "prompt_file": "output/cherry_blossom_garden/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "tropical_botanical": {
        "name": "Tropical Botanical Paradise",
        "book_title": "Tropical Botanical Paradise Coloring Book: Lush Tropical Plants, Exotic Flowers, and Jungle Scenes with Bold and Easy Designs for Adults",
        "prompt_file": "output/tropical_botanical/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "wildflower_meadow": {
        "name": "Wildflower Meadow",
        "book_title": "Wildflower Meadow Coloring Book: Beautiful Botanical Scenes with Bold and Easy Designs for Adults",
        "prompt_file": "output/wildflower_meadow/prompts.txt",
        "page_size": "8.5x8.5",
    },
    "lavender_dreams": {
        "name": "Lavender Dreams",
        "book_title": "Lavender Dreams Coloring Book: Provence Lavender Fields, Stone Cottages, and Cozy Garden Scenes with Bold and Easy Designs for Adults",
        "prompt_file": "output/lavender_dreams/prompts.txt",
        "page_size": "8.5x8.5",
    },
}

# --- Paths ---
OUTPUT_DIR = "output"


def get_book_dir(theme_key: str) -> str:
    """Return the output directory for a book: output/{theme_key}/"""
    return os.path.join(OUTPUT_DIR, theme_key)


def get_images_dir(theme_key: str) -> str:
    """Return the images directory: output/{theme_key}/images/"""
    return os.path.join(OUTPUT_DIR, theme_key, "images")


def get_plan_path(theme_key: str) -> str:
    """Return the plan JSON path: output/{theme_key}/plan.json"""
    return os.path.join(OUTPUT_DIR, theme_key, "plan.json")


def get_prompts_path(theme_key: str) -> str:
    """Return the prompts file path: output/{theme_key}/prompts.txt"""
    return os.path.join(OUTPUT_DIR, theme_key, "prompts.txt")


def get_interior_pdf_path(theme_key: str) -> str:
    """Return the interior PDF path: output/{theme_key}/interior.pdf"""
    return os.path.join(OUTPUT_DIR, theme_key, "interior.pdf")


def get_cover_png_path(theme_key: str) -> str:
    """Return the cover PNG path: output/{theme_key}/cover.png"""
    return os.path.join(OUTPUT_DIR, theme_key, "cover.png")


def get_cover_pdf_path(theme_key: str) -> str:
    """Return the cover PDF path: output/{theme_key}/cover.pdf"""
    return os.path.join(OUTPUT_DIR, theme_key, "cover.pdf")

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
