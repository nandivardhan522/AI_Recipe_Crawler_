'''from playwright.sync_api import sync_playwright
import json
import os
from bs4 import BeautifulSoup
from loguru import logger

from pathlib import Path

# Get project root directory (one level above this file's directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "json"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def scrape_recipe_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        logger.info(f"Loading: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # Give time for JavaScript to render

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Title
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "Untitled"

        # ✅ Ingredients - New DOM structure using span data attributes
        ingredients = []
        ingredient_items = soup.select("ul.mm-recipes-structured-ingredients__list li.mm-recipes-structured-ingredients__list-item")

        for item in ingredient_items:
            quantity = item.find("span", {"data-ingredient-quantity": True})
            unit = item.find("span", {"data-ingredient-unit": True})
            name = item.find("span", {"data-ingredient-name": True})

            quantity_text = quantity.get_text(strip=True) if quantity else ""
            unit_text = unit.get_text(strip=True) if unit else ""
            name_text = name.get_text(strip=True) if name else ""

            full_ingredient = f"{quantity_text} {unit_text} {name_text}".strip()
            if full_ingredient:
                ingredients.append(full_ingredient)

        # ✅ Instructions - Final working selector for new structure
        instructions = []
        instruction_tags = soup.select('li[class*="mntl-sc-block-group--LI"] > p.mntl-sc-block-html')

        for tag in instruction_tags:
            step = tag.get_text(strip=True)
            if step:
                instructions.append(step)

        # ✅ Image - From .img-placeholder div
        image_tag = soup.select_one("div.img-placeholder img")
        image_url = image_tag["src"] if image_tag and "src" in image_tag.attrs else None


        # ✅ Package everything
        recipe = {
            "title": title,
            "ingredients": ingredients,
            "instructions": instructions,
            "image_url": image_url,
            "source": url
        }

        # Save recipe as JSON
        safe_title = title.lower().replace(" ", "_").replace("/", "-")
        output_path = OUTPUT_DIR / f"{safe_title}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)

        logger.success(f"Saved: {output_path}")
        browser.close()
        return recipe

if __name__ == "__main__":
    # Test URL from AllRecipes
    test_url = "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/"
    scrape_recipe_with_playwright(test_url)'''

import json
import os
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "site_config.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(CONFIG_PATH) as f:
    SITE_CONFIG = json.load(f)

def get_site_config(url):
    domain = urlparse(url).netloc.replace("www.", "")
    return SITE_CONFIG.get(domain)

def scrape_recipe(url):
    site_conf = get_site_config(url)
    if not site_conf:
        logger.error(f"No config found for site: {url}")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        logger.info(f"Loading: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        soup = BeautifulSoup(page.content(), "html.parser")
        browser.close()

    # Title
    title = soup.select_one(site_conf["title"]).get_text(strip=True)

    # Ingredients
    ingredients = []
    for li in soup.select(site_conf["ingredients"]):
        q = li.select_one(site_conf["ingredient_parts"]["quantity"])
        u = li.select_one(site_conf["ingredient_parts"]["unit"])
        n = li.select_one(site_conf["ingredient_parts"]["name"])
        text = f"{q.text.strip() if q else ''} {u.text.strip() if u else ''} {n.text.strip() if n else ''}".strip()
        if text:
            ingredients.append(text)

    # Instructions
    instructions = [
        tag.get_text(strip=True)
        for tag in soup.select(site_conf["instructions"])
        if tag.get_text(strip=True)
    ]

    # Image
    image_tag = soup.select_one(site_conf["image"])
    image_url = image_tag["src"] if image_tag and "src" in image_tag.attrs else None

    # Save recipe
    recipe = {
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
        "image_url": image_url,
        "source": url
    }

    safe_title = title.lower().replace(" ", "_").replace("/", "-")
    output_path = OUTPUT_DIR / f"{safe_title}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(recipe, f, indent=2, ensure_ascii=False)

    logger.success(f"Saved: {output_path}")
    return recipe

if __name__ == "__main__":
    test_url = "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/"
    scrape_recipe(test_url)

