import os
import json
from bs4 import BeautifulSoup
from pathlib import Path
from playwright.sync_api import sync_playwright
from loguru import logger

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = PROJECT_ROOT / "data" / "processed" / "json"

def extract_video_link(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        logger.info(f"Loading: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Try finding YouTube iframe
        iframe = soup.find("iframe", {"src": lambda x: x and "youtube.com" in x})
        video_url = iframe["src"] if iframe else None

        browser.close()
        return video_url

def update_jsons_with_video_links():
    for json_file in JSON_DIR.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Skip if already has a video
        if "video_link" in data and data["video_link"]:
            continue

        url = data.get("source")
        if not url:
            continue

        video_url = extract_video_link(url)
        if video_url:
            data["video_link"] = video_url
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.success(f"Video added to {json_file.name}")
        else:
            logger.info(f"No video found for {json_file.name}")

if __name__ == "__main__":
    update_jsons_with_video_links()
