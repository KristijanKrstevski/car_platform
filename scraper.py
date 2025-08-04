import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "https://reklama5.mk/Search?cat=24"
MODEL_API = "https://reklama5.mk/Search/GetCarModelList?parentID={brand_id}"

def get_brands():
    """Scrape all car brands with their IDs."""
    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    brands = []
    for option in soup.select("#f31 option"):
        value = option.get("value")
        name = option.text.strip()
        # only valid numeric IDs
        if value and value.isdigit():
            brands.append({"id": value, "name": name})
    return brands

def get_models(brand_id):
    """Fetch all models for a given brand using the AJAX API."""
    url = MODEL_API.format(brand_id=brand_id)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            models = [item["Text"].strip() for item in data if item["Value"]]
            return models
    except Exception as e:
        print(f"Error fetching models for {brand_id}: {e}")
    return []

def scrape_all():
    brands = get_brands()
    all_data = {}
    for b in brands:
        print(f"Scraping {b['name']} (ID {b['id']})...")
        models = get_models(b["id"])
        all_data[b["name"]] = models
        time.sleep(0.2)  # avoid server overload

    with open("cars.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("✅ Done! Data saved to cars.json")

if __name__ == "__main__":
    scrape_all()
