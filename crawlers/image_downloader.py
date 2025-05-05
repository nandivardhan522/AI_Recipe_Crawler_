import os
import json
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path
from loguru import logger

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = PROJECT_ROOT / "data" / "processed" / "json"
IMAGE_DIR = PROJECT_ROOT / "data" / "processed" / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

def download_and_resize_image(image_url, image_path, size=(512, 512)):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content)).convert("RGB")
        img = img.resize(size)
        img.save(image_path)
        logger.success(f"Saved image: {image_path.name}")
        return True
    except Exception as e:
        logger.warning(f"Failed to download or resize image: {image_url} — {e}")
        return False

def process_all_jsons():
    for json_file in JSON_DIR.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        image_url = data.get("image_url")
        title = data.get("title", "recipe").lower().replace(" ", "_").replace("/", "-")
        image_path = IMAGE_DIR / f"{title}.jpg"

        if image_url and not image_path.exists():
            success = download_and_resize_image(image_url, image_path)
            if success:
                logger.info(f"Image saved for: {title}")
            else:
                logger.warning(f"Skipped: {title}")

if __name__ == "__main__":
    process_all_jsons()
