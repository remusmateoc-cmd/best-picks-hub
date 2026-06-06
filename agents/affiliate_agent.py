from config import AMAZON_AFFILIATE_TAG, AMAZON_AFFILIATE_RATES

# Programe affiliate alternative cu comisioane tipice
ALTERNATIVE_PROGRAMS = [
    {"name": "CJ Affiliate",   "url": "https://www.cj.com",        "commission": "5-15%", "niche": "General"},
    {"name": "ShareASale",     "url": "https://www.shareasale.com", "commission": "5-30%", "niche": "Physical Products"},
    {"name": "Impact Radius",  "url": "https://impact.com",         "commission": "5-20%", "niche": "General"},
    {"name": "ClickBank",      "url": "https://www.clickbank.com",  "commission": "30-75%","niche": "Digital Products"},
    {"name": "Etsy Affiliate", "url": "https://www.etsy.com/affiliates", "commission": "4%", "niche": "Handmade/Vintage"},
]


def enrich_with_affiliate(products: list[dict]) -> list[dict]:
    print(f"\n[AGENT AFFILIATE] Generez link-uri affiliate pentru {len(products)} produse...")
    return [_add_affiliate(p) for p in products]


def _add_affiliate(product: dict) -> dict:
    asin = product.get("asin", "")
    category = product.get("category", "")

    affiliate_url = ""
    commission_rate = 0.0

    if asin and AMAZON_AFFILIATE_TAG != "yourtag-20":
        affiliate_url = f"https://www.amazon.com/dp/{asin}?tag={AMAZON_AFFILIATE_TAG}"
        commission_rate = AMAZON_AFFILIATE_RATES.get(category, 4.0)
    elif asin:
        affiliate_url = f"https://www.amazon.com/dp/{asin}"

    price = product.get("price", 0) or 0
    estimated_commission = round(price * (commission_rate / 100), 2)

    return {
        **product,
        "affiliate_url": affiliate_url,
        "affiliate_commission_rate": commission_rate,
        "estimated_commission": estimated_commission,
    }


def get_alternative_programs() -> list[dict]:
    return ALTERNATIVE_PROGRAMS
