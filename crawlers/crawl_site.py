import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from loguru import logger

visited = set()

def collect_internal_links(start_url, limit=50):
    domain = urlparse(start_url).netloc
    queue = [start_url]
    collected = []

    while queue and len(collected) < limit:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            collected.append(url)
            logger.info(f"🔗 Collected: {url}")

            for link in soup.find_all("a", href=True):
                href = urljoin(url, link["href"])
                parsed_href = urlparse(href)

                if parsed_href.netloc == domain and href not in visited:
                    queue.append(href)

        except Exception as e:
            logger.warning(f"⚠️ Failed to process {url}: {e}")

    return collected
