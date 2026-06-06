#!/usr/bin/env python3
"""
Deploy Agent — genereaza site-ul public GitHub Pages din ultimul raport JSON.

Utilizare:
    python deploy.py              # genereaza site in docs/
    python deploy.py --push       # genereaza + commit + push pe GitHub
"""

import os
import sys
import json
import glob
import subprocess
from datetime import datetime
from config import (
    DOCS_DIR, REPORT_OUTPUT_DIR,
    SITE_NAME, SITE_TAGLINE, SITE_AUTHOR, AMAZON_AFFILIATE_TAG,
)

CATEGORY_EMOJI = {
    "Electronics":      "⚡",
    "Home & Kitchen":   "🏠",
    "Sports & Outdoors":"🏃",
    "Toys & Games":     "🎮",
    "Beauty":           "💄",
    "Health":           "💊",
    "Pet Supplies":     "🐾",
    "Office Products":  "💼",
}


def main():
    push_to_github = "--push" in sys.argv

    print("=" * 56)
    print(f"  DEPLOY AGENT — {SITE_NAME}")
    print("=" * 56)

    data = _load_latest_json()
    if not data:
        print("[!] Nu exista date. Ruleaza mai intai: python main.py")
        sys.exit(1)

    public_products = _filter_public(data)
    categories = sorted(set(p.get("category", "") for p in public_products))

    print(f"  Produse pentru site: {len(public_products)}")
    print(f"  Categorii: {len(categories)}")

    os.makedirs(DOCS_DIR, exist_ok=True)
    _write_index(public_products, categories)
    _write_css()
    _write_nojekyll()

    print(f"\n  [+] Site generat in /{DOCS_DIR}/")

    if push_to_github:
        _git_push()
    else:
        print("\n  Tip: ruleaza 'python deploy.py --push' pentru a publica pe GitHub.")

    print()


def _load_latest_json() -> list[dict]:
    files = sorted(glob.glob(os.path.join(REPORT_OUTPUT_DIR, "data_*.json")))
    if not files:
        return []
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)


def _filter_public(products: list[dict]) -> list[dict]:
    """Pastreaza doar produsele bune si elimina datele interne de cost."""
    good = [p for p in products if p.get("opportunity_score") in ("EXCELLENT", "GOOD")]
    public = []
    for p in good:
        public.append({
            "title":    p.get("title", ""),
            "price":    p.get("price", 0),
            "rating":   p.get("rating"),
            "category": p.get("category", ""),
            "asin":     p.get("asin", ""),
            "amazon_url": p.get("amazon_url", ""),
            "trend_direction": p.get("trend_direction", "stable"),
            "avg_interest": p.get("avg_interest", 0),
            "score":    p.get("opportunity_score", ""),
        })
    return public


def _affiliate_link(p: dict) -> str:
    asin = p.get("asin", "")
    tag  = AMAZON_AFFILIATE_TAG
    if asin and tag and tag != "yourtag-20":
        return f"https://www.amazon.com/dp/{asin}?tag={tag}"
    return p.get("amazon_url", "") or (f"https://www.amazon.com/dp/{asin}" if asin else "#")


def _stars(rating) -> str:
    if not rating:
        return ""
    full  = int(rating)
    half  = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + ("½" if half else "") + "☆" * empty


def _trend_badge(direction: str) -> str:
    icons = {"rising": ("📈", "trend-up"), "falling": ("📉", "trend-down"), "stable": ("➡️", "trend-stable")}
    icon, cls = icons.get(direction, ("❓", ""))
    return f'<span class="trend-badge {cls}">{icon} {direction.title()}</span>'


def _product_cards(products: list[dict]) -> str:
    html = ""
    for p in products:
        link   = _affiliate_link(p)
        stars  = _stars(p.get("rating"))
        rating = p.get("rating")
        cat    = p.get("category", "")
        emoji  = CATEGORY_EMOJI.get(cat, "🛍️")
        trend  = _trend_badge(p.get("trend_direction", "stable"))
        price  = p.get("price", 0)
        title  = p.get("title", "")

        html += f"""
      <div class="card" data-category="{cat}">
        <div class="card-cat">{emoji} {cat}</div>
        <h3 class="card-title">{title}</h3>
        <div class="card-meta">
          {"<span class='stars'>" + stars + f"</span> <span class='rating-num'>{rating}</span>" if rating else ""}
          {trend}
        </div>
        <div class="card-price">${price:.2f}</div>
        <a class="btn-buy" href="{link}" target="_blank" rel="noopener sponsored">
          🛒 View on Amazon
        </a>
      </div>"""
    return html


def _category_buttons(categories: list[str]) -> str:
    buttons = '<button class="filter-btn active" onclick="filter(\'all\')">All</button>\n'
    for cat in categories:
        emoji = CATEGORY_EMOJI.get(cat, "🛍️")
        buttons += f'      <button class="filter-btn" onclick="filter(\'{cat}\')">{emoji} {cat}</button>\n'
    return buttons


def _write_index(products: list[dict], categories: list[str]):
    date_str  = datetime.now().strftime("%B %d, %Y")
    cards     = _product_cards(products)
    cat_btns  = _category_buttons(categories)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{SITE_TAGLINE} — Updated {date_str}">
  <title>{SITE_NAME} — {SITE_TAGLINE}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>

<header>
  <div class="header-inner">
    <div class="logo">🛍️ {SITE_NAME}</div>
    <p class="tagline">{SITE_TAGLINE}</p>
  </div>
</header>

<section class="hero">
  <h1>Today's Best Amazon Picks</h1>
  <p>Curated from Amazon's bestseller lists — updated daily</p>
  <div class="hero-stats">
    <div class="hstat"><strong>{len(products)}</strong><span>Top Products</span></div>
    <div class="hstat"><strong>{len(categories)}</strong><span>Categories</span></div>
    <div class="hstat"><strong>Daily</strong><span>Updated</span></div>
  </div>
</section>

<section class="filters">
  <div class="container">
    {cat_btns}
  </div>
</section>

<main class="container">
  <p class="update-note">Last updated: {date_str}</p>
  <div class="grid" id="grid">
    {cards}
  </div>
</main>

<footer>
  <div class="container">
    <p><strong>Affiliate Disclosure:</strong> {SITE_AUTHOR} is a participant in the Amazon Services LLC
    Associates Program, an affiliate advertising program designed to provide a means for sites to earn
    advertising fees by advertising and linking to Amazon.com.</p>
    <p style="margin-top:8px;color:#999">© {datetime.now().year} {SITE_AUTHOR} · Updated {date_str}</p>
  </div>
</footer>

<script>
function filter(cat) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('.card').forEach(c => {{
    c.style.display = (cat === 'all' || c.dataset.category === cat) ? 'flex' : 'none';
  }});
}}
</script>

</body>
</html>"""

    path = os.path.join(DOCS_DIR, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [+] {path}")


def _write_css():
    css = """/* Best Picks Hub — stylesheet */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Segoe UI', Arial, sans-serif;
  background: #f5f7fa;
  color: #222;
  line-height: 1.6;
}

.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }

/* Header */
header {
  background: #fff;
  border-bottom: 3px solid #ff9900;
  padding: 16px 20px;
  position: sticky; top: 0; z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
}
.header-inner { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; gap: 16px; }
.logo { font-size: 1.4rem; font-weight: 700; color: #232f3e; }
.tagline { font-size: .85rem; color: #888; }

/* Hero */
.hero {
  background: linear-gradient(135deg, #232f3e, #37475a);
  color: #fff;
  text-align: center;
  padding: 60px 20px;
}
.hero h1 { font-size: 2.2rem; margin-bottom: 10px; }
.hero p { color: #ccc; font-size: 1.05rem; margin-bottom: 30px; }
.hero-stats { display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; }
.hstat { text-align: center; }
.hstat strong { display: block; font-size: 1.8rem; color: #ff9900; }
.hstat span { font-size: .8rem; color: #aaa; text-transform: uppercase; letter-spacing: .05em; }

/* Filters */
.filters { background: #fff; padding: 16px 0; border-bottom: 1px solid #e0e0e0; overflow-x: auto; }
.filters .container { display: flex; gap: 8px; flex-wrap: wrap; }
.filter-btn {
  padding: 7px 16px; border-radius: 20px; border: 1px solid #ddd;
  background: #fff; cursor: pointer; font-size: .85rem; white-space: nowrap;
  transition: all .2s;
}
.filter-btn:hover, .filter-btn.active {
  background: #ff9900; border-color: #ff9900; color: #fff; font-weight: 600;
}

/* Grid */
main { padding: 30px 20px; }
.update-note { font-size: .8rem; color: #999; margin-bottom: 18px; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

/* Card */
.card {
  background: #fff;
  border-radius: 14px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
  border: 1px solid #eee;
  transition: transform .2s, box-shadow .2s;
}
.card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,.12); }
.card-cat { font-size: .75rem; color: #888; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }
.card-title { font-size: .95rem; font-weight: 600; color: #232f3e; line-height: 1.4; flex-grow: 1; }
.card-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.stars { color: #ff9900; font-size: 1rem; }
.rating-num { font-size: .82rem; color: #888; }

/* Trend badges */
.trend-badge { font-size: .72rem; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
.trend-up   { background: #e6f9f0; color: #1a8a4a; }
.trend-down { background: #fdecea; color: #c0392b; }
.trend-stable { background: #f0f0f0; color: #666; }

.card-price { font-size: 1.5rem; font-weight: 700; color: #232f3e; }
.btn-buy {
  display: block;
  background: #ff9900;
  color: #fff;
  text-align: center;
  padding: 12px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 700;
  font-size: .95rem;
  transition: background .2s;
  margin-top: auto;
}
.btn-buy:hover { background: #e68a00; }

/* Footer */
footer {
  background: #232f3e;
  color: #aaa;
  padding: 30px 20px;
  text-align: center;
  font-size: .82rem;
  line-height: 1.7;
}

@media (max-width: 600px) {
  .hero h1 { font-size: 1.5rem; }
  .hero-stats { gap: 20px; }
  .grid { grid-template-columns: 1fr; }
}
"""
    path = os.path.join(DOCS_DIR, "style.css")
    with open(path, "w", encoding="utf-8") as f:
        f.write(css)
    print(f"  [+] {path}")


def _write_nojekyll():
    path = os.path.join(DOCS_DIR, ".nojekyll")
    with open(path, "w") as f:
        f.write("")
    print(f"  [+] {path}")


def _git_push():
    print("\n  [GIT] Publicare pe GitHub...")
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    commands = [
        ["git", "add", DOCS_DIR],
        ["git", "commit", "-m", f"update: site rebuilt {date_str}"],
        ["git", "push"],
    ]
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        label = " ".join(cmd[:2])
        if result.returncode == 0:
            print(f"  [+] {label} OK")
        else:
            print(f"  [!] {label} EROARE: {result.stderr.strip()}")
            break
    else:
        print("  Site publicat pe GitHub Pages!")


if __name__ == "__main__":
    main()
