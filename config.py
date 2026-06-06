AMAZON_BESTSELLER_URLS = {
    "Electronics":    "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/",
    "Home & Kitchen": "https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/kitchen/",
    "Sports & Outdoors": "https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/",
    "Toys & Games":   "https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games/",
    "Beauty":         "https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty/",
    "Health":         "https://www.amazon.com/Best-Sellers-Health-Personal-Care/zgbs/hpc/",
    "Pet Supplies":   "https://www.amazon.com/Best-Sellers-Pet-Supplies/zgbs/pet-supplies/",
    "Office Products":"https://www.amazon.com/Best-Sellers-Office-Products/zgbs/office-products/",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

PROFIT_SETTINGS = {
    "min_margin_percent": 25,
    "min_profit_usd": 5.0,
    "target_margin_percent": 40,
    "amazon_fee_percent": 15,
    "shipping_cost_usd": 3.5,
    "aliexpress_cost_ratio": 0.25,  # AliExpress cost ≈ 25% din pretul Amazon retail
}

# Comisioane Amazon Associates pe categorie (%)
AMAZON_AFFILIATE_RATES = {
    "Electronics":     3.0,
    "Home & Kitchen":  4.5,
    "Sports & Outdoors": 4.5,
    "Toys & Games":    3.0,
    "Beauty":          6.0,
    "Health":          4.5,
    "Pet Supplies":    5.0,
    "Office Products": 4.0,
}

# Schimba cu tag-ul tau Amazon Associates
AMAZON_AFFILIATE_TAG = "bestpicksh031-20"

REQUEST_DELAY_MIN = 2.0
REQUEST_DELAY_MAX = 4.0
MAX_PRODUCTS_PER_CATEGORY = 20
REPORT_OUTPUT_DIR = "reports"
TRENDS_TOP_PRODUCTS = 30

# ─── Credentiale Slickdeals ─────────────────────────────────────────────────
SLICKDEALS_EMAIL    = ""   # pune email-ul tau de Slickdeals
SLICKDEALS_PASSWORD = ""   # pune parola ta de Slickdeals

# ─── Setari site public GitHub Pages ────────────────────────────────────────
SITE_NAME      = "Best Picks Hub"
SITE_TAGLINE   = "Top Amazon products, handpicked daily"
SITE_AUTHOR    = "Best Picks Hub"
DOCS_DIR       = "docs"          # folder servit de GitHub Pages
# GitHub repo URL — completeaza dupa ce creezi repo-ul
GITHUB_REPO_URL = ""             # ex: "https://github.com/username/best-picks-hub"
