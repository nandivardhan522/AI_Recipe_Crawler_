import os
import json
import pandas as pd
from pathlib import Path
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = PROJECT_ROOT / "data" / "processed" / "json"
IMAGE_DIR = PROJECT_ROOT / "data" / "processed" / "images"
OUTPUT_DIR = PROJECT_ROOT / "data" / "final"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def combine_recipes():
    all_recipes = []

    for json_file in JSON_DIR.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        title = data.get("title", "unknown")
        ingredients = " | ".join(data.get("ingredients", []))
        instructions = " ".join(data.get("instructions", []))
        image_filename = f"{title.lower().replace(' ', '_').replace('/', '-')}.jpg"
        image_path = IMAGE_DIR / image_filename
        image_path = str(image_path) if image_path.exists() else None
        video_link = data.get("video_link")

        all_recipes.append({
            "title": title,
            "ingredients": ingredients,
            "instructions": instructions,
            "image_path": image_path,
            "video_link": video_link,
            "source": data.get("source")
        })

    # ✅ Save as JSONL
    jsonl_path = OUTPUT_DIR / "recipes.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in all_recipes:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")
    logger.success(f"Saved: {jsonl_path}")

    # ✅ Save as CSV
    df = pd.DataFrame(all_recipes)
    csv_path = OUTPUT_DIR / "recipes.csv"
    df.to_csv(csv_path, index=False)
    logger.success(f"Saved: {csv_path}")

if __name__ == "__main__":
    combine_recipes()
