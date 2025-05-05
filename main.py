from crawlers.crawl_site import collect_internal_links
from ai.page_classifier import is_recipe_page
#from extractors.scrape_recipe import scrape_and_save_recipe
#from storage.summary import generate_summary


def scrape_site(homepage_url, max_pages=50):
    print(f"🔍 Starting crawl at: {homepage_url}")

    # Step 1: Crawl website for links
    all_links = collect_internal_links(homepage_url, limit=max_pages)

    print(f"🧠 Classifying {len(all_links)} pages...")

    # Step 2: Classify and extract recipes
    recipe_count = 0
    for url in all_links:
        if is_recipe_page(url):
            print("yes")
            '''success = scrape_and_save_recipe(url)
            if success:
                recipe_count += 1

    print(f"✅ Finished! Total recipes saved: {recipe_count}")

    # Step 3: Generate summary/dashboard
    generate_summary()'''


if __name__ == "__main__":
    scrape_site("https://www.allrecipes.com")
