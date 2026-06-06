import time
import random
import requests
from bs4 import BeautifulSoup
from config import AMAZON_BESTSELLER_URLS, HEADERS, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, MAX_PRODUCTS_PER_CATEGORY


def fetch_all_categories() -> list[dict]:
    all_products = []
    print(f"\n[AGENT AMAZON] Scanez {len(AMAZON_BESTSELLER_URLS)} categorii...")

    for category, url in AMAZON_BESTSELLER_URLS.items():
        print(f"  -> {category}...", end=" ", flush=True)
        products = _scrape_category(category, url)
        all_products.extend(products)
        print(f"{len(products)} produse")

    return all_products


def _scrape_category(category: str, url: str) -> list[dict]:
    time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
    except requests.exceptions.RequestException as e:
        print(f"\n  [!] Request failed: {e}")
        return []

    if resp.status_code != 200:
        print(f"\n  [!] HTTP {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.content, "html.parser")
    products = []

    # Incearca mai multi selectori (Amazon isi schimba des layout-ul)
    items = (
        soup.select(".zg-grid-general-faceout") or
        soup.select(".zg-item-immersion") or
        soup.select("[data-asin]")
    )

    for item in items[:MAX_PRODUCTS_PER_CATEGORY]:
        product = _extract(item, category)
        if product:
            products.append(product)

    return products


def _extract(item, category: str) -> dict | None:
    title = _text(item, [
        ".p13n-sc-truncated-heading",
        "._cDEzb_p13n-sc-css-line-clamp-3_g3dy1",
        ".a-size-base-plus",
        ".a-link-normal span",
    ])

    price = _parse_price(_text(item, [
        ".p13n-sc-price",
        ".a-price .a-offscreen",
        "span[data-a-color='price'] .a-offscreen",
    ]))

    if not title or not price:
        return None

    rating_el = item.select_one(".a-icon-star-small .a-icon-alt, .a-icon-star .a-icon-alt")
    rating = None
    if rating_el:
        try:
            rating = float(rating_el.get_text().split()[0])
        except (ValueError, IndexError):
            pass

    asin = item.get("data-asin", "")
    link_el = item.select_one("a.a-link-normal[href]")
    amazon_url = f"https://www.amazon.com{link_el['href']}" if link_el else ""

    rank_el = item.select_one(".zg-bdg-text")
    rank = rank_el.get_text(strip=True).lstrip("#") if rank_el else None

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "asin": asin,
        "rank": rank,
        "category": category,
        "amazon_url": amazon_url,
    }


def _text(item, selectors: list[str]) -> str | None:
    for sel in selectors:
        el = item.select_one(sel)
        if el:
            return el.get_text(strip=True)
    return None


def _parse_price(text: str | None) -> float | None:
    if not text:
        return None
    try:
        return float(text.replace("$", "").replace(",", "").split("-")[0].strip())
    except ValueError:
        return None
