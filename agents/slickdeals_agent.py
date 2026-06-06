"""
Slickdeals Agent — posteaza automat cel mai bun deal pe Slickdeals.net
Foloseste Playwright pentru automatizare browser.

Mod semi-auto (default): completeaza formularul, tu dai click Submit
Mod full-auto:           python slickdeals_agent.py --auto (submit automat)
"""

import json
import glob
import time
import random
import sys
from datetime import datetime
from config import (
    SLICKDEALS_EMAIL, SLICKDEALS_PASSWORD,
    AMAZON_AFFILIATE_TAG, REPORT_OUTPUT_DIR
)

SLICKDEALS_LOGIN_URL = "https://slickdeals.net/account/login/"
SLICKDEALS_DEAL_URL  = "https://slickdeals.net/share-a-deal/"
SITE_URL = "https://remusmateoc-cmd.github.io/best-picks-hub"

DEAL_TEMPLATES = {
    "Electronics": {
        "category": "Electronics",
        "desc_suffix": "Great deal on a top-rated Amazon electronics bestseller. Free shipping with Prime."
    },
    "Home & Kitchen": {
        "category": "Home & Kitchen",
        "desc_suffix": "Highly rated home product, consistently in Amazon's bestseller list. Ships free with Prime."
    },
    "Sports & Outdoors": {
        "category": "Sports & Outdoors",
        "desc_suffix": "Top-rated sports product at a great price. Perfect for this season. Free Prime shipping."
    },
    "Toys & Games": {
        "category": "Toys & Games",
        "desc_suffix": "Best-selling toy on Amazon with thousands of 5-star reviews. Free Prime shipping."
    },
    "Beauty": {
        "category": "Beauty",
        "desc_suffix": "Amazon bestseller in beauty. Highly rated by verified buyers. Free shipping with Prime."
    },
    "Health": {
        "category": "Health & Beauty",
        "desc_suffix": "Top-rated health product on Amazon. Great value, free Prime shipping."
    },
    "Pet Supplies": {
        "category": "Pet Supplies",
        "desc_suffix": "Best-selling pet product with excellent reviews. Your pet will love it. Free Prime shipping."
    },
    "Office Products": {
        "category": "Office Supplies",
        "desc_suffix": "Top Amazon bestseller for home and office. Highly rated, free Prime shipping."
    },
}


def run(full_auto: bool = False):
    if not SLICKDEALS_EMAIL or not SLICKDEALS_PASSWORD:
        print("  [!] Completeaza SLICKDEALS_EMAIL si SLICKDEALS_PASSWORD in config.py")
        return

    product = _best_product()
    if not product:
        print("  [!] Nu sunt produse pentru Slickdeals. Ruleaza mai intai main.py.")
        return

    deal = _build_deal(product)
    print(f"\n[AGENT SLICKDEALS] Postez deal: {deal['title'][:60]}")
    print(f"  Pret: ${deal['price']} | Link: {deal['url'][:50]}...")

    _post_via_playwright(deal, full_auto)


def _best_product() -> dict | None:
    files = sorted(glob.glob(f"{REPORT_OUTPUT_DIR}/data_*.json"))
    if not files:
        return None
    with open(files[-1], encoding="utf-8") as f:
        data = json.load(f)

    good = [p for p in data if p.get("opportunity_score") in ("EXCELLENT", "GOOD")
            and p.get("price", 0) > 10 and p.get("asin") or p.get("amazon_url")]

    if not good:
        return None

    # Alege produsul cu cel mai bun raport pret/interes
    return max(good, key=lambda x: x.get("avg_interest", 0) * 2 + x.get("score_value", 0))


def _affiliate_link(product: dict) -> str:
    asin = product.get("asin", "")
    url  = product.get("amazon_url", "")
    tag  = AMAZON_AFFILIATE_TAG

    if asin and tag:
        return f"https://www.amazon.com/dp/{asin}?tag={tag}"

    # Extrage ASIN din URL daca nu e stocat separat
    if "/dp/" in url:
        asin = url.split("/dp/")[1].split("/")[0].split("?")[0]
        if asin:
            return f"https://www.amazon.com/dp/{asin}?tag={tag}"

    return url


def _build_deal(product: dict) -> dict:
    cat      = product.get("category", "")
    title    = product.get("title", "")
    price    = product.get("price", 0)
    rating   = product.get("rating", 0)
    tmpl     = DEAL_TEMPLATES.get(cat, {"category": "General", "desc_suffix": "Free Prime shipping."})
    link     = _affiliate_link(product)

    stars = "⭐" * int(rating) if rating else ""
    deal_title = f"[Amazon] {title[:70]} - ${price:.2f}"

    # Posteaza link catre site-ul tau (nu afiliat direct) — acceptat de Slickdeals
    site_link = SITE_URL

    description = f"""Found this {tmpl['category'].lower()} deal on Amazon — one of their current bestsellers.

{stars} {f"{rating}/5 stars from thousands of verified buyers" if rating else ""}
✅ Amazon Bestseller — consistently top-ranked
✅ {tmpl['desc_suffix']}

Full review + direct Amazon link: {site_link}"""

    return {
        "title":       deal_title,
        "url":         site_link,   # link catre site-ul tau, nu afiliat direct
        "store":       "Amazon",
        "price":       f"{price:.2f}",
        "category":    tmpl["category"],
        "description": description,
    }


def _post_via_playwright(deal: dict, full_auto: bool):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [!] Playwright nu e instalat: pip install playwright && playwright install chromium")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=80)
        ctx     = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()

        try:
            # 1. LOGIN
            print("  -> Login Slickdeals...")
            page.goto(SLICKDEALS_LOGIN_URL, wait_until="networkidle", timeout=30000)
            _human_delay()

            page.fill('input[name="username"], input[type="email"], #username', SLICKDEALS_EMAIL)
            _human_delay(0.5)
            page.fill('input[name="password"], input[type="password"], #password', SLICKDEALS_PASSWORD)
            _human_delay(0.8)
            page.click('button[type="submit"], input[type="submit"], .login-btn, button:has-text("Log In"), button:has-text("Sign In")')
            page.wait_for_load_state("networkidle", timeout=15000)
            print("  -> Logat!")

            # 2. SHARE A DEAL PAGE
            _human_delay(1.5)
            print("  -> Deschid formularul de deal...")
            page.goto(SLICKDEALS_DEAL_URL, wait_until="networkidle", timeout=30000)
            _human_delay(2)

            # 3. COMPLETEAZA FORMULARUL
            _fill_field(page, ['input[name="title"]', '#deal-title', 'input[placeholder*="title"]'], deal["title"])
            _fill_field(page, ['input[name="url"]', '#deal-url', 'input[placeholder*="url"], input[placeholder*="link"]'], deal["url"])
            _fill_field(page, ['input[name="price"]', '#deal-price', 'input[placeholder*="price"]'], deal["price"])

            # Store
            _fill_field(page, ['input[name="store"]', '#deal-store', 'input[placeholder*="store"]'], deal["store"])

            # Descriere
            desc_selectors = ['textarea[name="description"]', '#deal-description', 'textarea[placeholder*="description"]', 'textarea']
            for sel in desc_selectors:
                try:
                    page.fill(sel, deal["description"])
                    break
                except Exception:
                    continue

            print("  -> Formular completat!")

            if full_auto:
                _human_delay(1.5)
                page.click('button[type="submit"]:has-text("Submit"), button:has-text("Post Deal"), button:has-text("Share Deal")')
                page.wait_for_load_state("networkidle", timeout=15000)
                print("  -> Deal postat automat!")
            else:
                print("\n  ================================================")
                print("  FORMULAR COMPLETAT AUTOMAT!")
                print("  Verifica datele in browser si apasa SUBMIT.")
                print("  Browserul ramane deschis 3 minute...")
                print("  ================================================")
                time.sleep(180)

        except Exception as e:
            print(f"  [!] Eroare: {e}")
            print("  Browserul ramane deschis 2 minute pentru debug...")
            time.sleep(120)
        finally:
            browser.close()


def _fill_field(page, selectors: list, value: str):
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click()
                _human_delay(0.3)
                el.fill(value)
                _human_delay(0.5)
                return
        except Exception:
            continue


def _human_delay(base: float = 1.0):
    time.sleep(base + random.uniform(0.2, 0.8))


if __name__ == "__main__":
    full_auto = "--auto" in sys.argv
    run(full_auto)
