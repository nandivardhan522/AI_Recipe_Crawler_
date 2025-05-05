from transformers import pipeline
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from loguru import logger

# Load zero-shot classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

CANDIDATE_LABELS = ["recipe", "news article", "blog post", "product page", "home page"]

def is_recipe_page(url):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        # Build candidate text from page title + first paragraph + meta description
        title = soup.find("title").text if soup.find("title") else ""
        meta = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta["content"] if meta else ""
        first_p = soup.find("p").text if soup.find("p") else ""

        input_text = f"{title}. {meta_desc}. {first_p}"

        result = classifier(input_text, CANDIDATE_LABELS)
        top_label = result["labels"][0]
        logger.info(f"[{top_label}] {url} → score: {result['scores'][0]:.2f}")
        return top_label == "recipe"

    except Exception as e:
        logger.warning(f"Error classifying {url}: {e}")
        return False
