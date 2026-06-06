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

CATEGORY_ICON = {
    "Electronics":       "fa-bolt",
    "Home & Kitchen":    "fa-house",
    "Sports & Outdoors": "fa-dumbbell",
    "Toys & Games":      "fa-gamepad",
    "Beauty":            "fa-star",
    "Health":            "fa-heart-pulse",
    "Pet Supplies":      "fa-paw",
    "Office Products":   "fa-briefcase",
}

CATEGORY_GRADIENT = {
    "Electronics":       "from-blue-500 to-indigo-600",
    "Home & Kitchen":    "from-orange-400 to-red-500",
    "Sports & Outdoors": "from-green-500 to-teal-600",
    "Toys & Games":      "from-purple-500 to-pink-500",
    "Beauty":            "from-pink-400 to-rose-500",
    "Health":            "from-emerald-400 to-green-600",
    "Pet Supplies":      "from-amber-400 to-orange-500",
    "Office Products":   "from-slate-500 to-gray-700",
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
    _write_nojekyll()

    print(f"  [+] Site generat in /{DOCS_DIR}/")

    if push_to_github:
        _git_push()
    else:
        print("  Tip: ruleaza 'python deploy.py --push' pentru a publica pe GitHub.")
    print()


def _load_latest_json() -> list[dict]:
    files = sorted(glob.glob(os.path.join(REPORT_OUTPUT_DIR, "data_*.json")))
    if not files:
        return []
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)


def _filter_public(products: list[dict]) -> list[dict]:
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
    if asin and tag:
        return f"https://www.amazon.com/dp/{asin}?tag={tag}"
    return p.get("amazon_url", "") or (f"https://www.amazon.com/dp/{asin}" if asin else "#")


def _stars(rating) -> str:
    if not rating:
        return ""
    full  = int(rating)
    half  = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + ("½" if half else "") + "☆" * empty


def _write_index(products: list[dict], categories: list[str]):
    date_str   = datetime.now().strftime("%B %d, %Y")
    featured   = products[:4]
    all_prods  = products

    # Swiper slides pentru featured
    swiper_slides = ""
    for p in featured:
        link     = _affiliate_link(p)
        cat      = p.get("category", "")
        gradient = CATEGORY_GRADIENT.get(cat, "from-gray-500 to-gray-700")
        icon     = CATEGORY_ICON.get(cat, "fa-tag")
        rating   = p.get("rating")
        stars    = _stars(rating)
        trend    = p.get("trend_direction", "stable")
        trend_html = ""
        if trend == "rising":
            trend_html = '<span class="inline-flex items-center gap-1 bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded-full"><i class="fa-solid fa-arrow-trend-up"></i> Trending</span>'

        swiper_slides += f"""
        <div class="swiper-slide">
          <div class="featured-card bg-gradient-to-br {gradient} rounded-2xl p-6 h-full flex flex-col justify-between text-white shadow-2xl">
            <div>
              <div class="flex items-center justify-between mb-3">
                <span class="bg-white/20 backdrop-blur-sm text-white text-xs font-bold px-3 py-1 rounded-full">
                  <i class="fa-solid {icon} mr-1"></i>{cat}
                </span>
                {trend_html}
              </div>
              <h3 class="text-lg font-bold leading-tight mb-3">{p.get("title","")[:75]}</h3>
              <div class="text-yellow-300 text-sm mb-1">{stars}</div>
              {"<div class='text-white/70 text-xs'>" + str(rating) + " / 5 stars</div>" if rating else ""}
            </div>
            <div class="mt-4">
              <div class="text-3xl font-black mb-4">${p.get("price", 0):.2f}</div>
              <a href="{link}" target="_blank" rel="noopener sponsored"
                 class="block w-full text-center bg-white text-gray-900 font-bold py-3 px-4 rounded-xl hover:bg-yellow-300 transition-all duration-200 shadow-lg">
                <i class="fa-brands fa-amazon mr-2"></i>View on Amazon
              </a>
            </div>
          </div>
        </div>"""

    # Category filter buttons
    cat_buttons = '<button onclick="filterCat(\'all\', this)" class="filter-btn active-btn">All</button>'
    for cat in categories:
        icon = CATEGORY_ICON.get(cat, "fa-tag")
        safe = cat.replace(" ", "_").replace("&", "and")
        cat_buttons += f'<button onclick="filterCat(\'{safe}\', this)" class="filter-btn"><i class="fa-solid {icon} mr-1"></i>{cat}</button>'

    # Product cards grid
    product_cards = ""
    for p in all_prods:
        link     = _affiliate_link(p)
        cat      = p.get("category", "")
        icon     = CATEGORY_ICON.get(cat, "fa-tag")
        safe_cat = cat.replace(" ", "_").replace("&", "and")
        rating   = p.get("rating")
        stars    = _stars(rating)
        trend    = p.get("trend_direction", "stable")
        gradient = CATEGORY_GRADIENT.get(cat, "from-gray-500 to-gray-700")

        trend_badge = ""
        if trend == "rising":
            trend_badge = '<span class="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full"><i class="fa-solid fa-arrow-trend-up mr-1"></i>Trending</span>'
        elif trend == "falling":
            trend_badge = '<span class="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full"><i class="fa-solid fa-arrow-trend-down mr-1"></i>Falling</span>'

        product_cards += f"""
        <div class="product-card group bg-gray-800 rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 flex flex-col" data-cat="{safe_cat}">
          <div class="h-2 bg-gradient-to-r {gradient}"></div>
          <div class="p-5 flex flex-col flex-1">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs text-gray-400 font-semibold uppercase tracking-wider">
                <i class="fa-solid {icon} mr-1"></i>{cat}
              </span>
              {trend_badge}
            </div>
            <h3 class="text-white font-semibold text-sm leading-snug mb-3 flex-1">{p.get("title","")[:80]}</h3>
            {"<div class='text-yellow-400 text-sm mb-1'>" + stars + "<span class='text-gray-400 text-xs ml-1'>" + str(rating) + "</span></div>" if rating else ""}
            <div class="flex items-center justify-between mt-3 pt-3 border-t border-gray-700">
              <span class="text-2xl font-black text-white">${p.get("price", 0):.2f}</span>
              <a href="{link}" target="_blank" rel="noopener sponsored"
                 class="flex items-center gap-2 bg-yellow-400 hover:bg-yellow-300 text-gray-900 font-bold text-sm px-4 py-2 rounded-xl transition-all duration-200">
                <i class="fa-brands fa-amazon"></i>Buy Now
              </a>
            </div>
          </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{SITE_TAGLINE} — Updated {date_str}">
  <title>{SITE_NAME} — {SITE_TAGLINE}</title>

  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config = {{ darkMode: 'class', theme: {{ extend: {{}} }} }}</script>

  <!-- Swiper.js -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"/>

  <!-- AOS Animations -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.css"/>

  <!-- Font Awesome -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>

  <!-- Google Fonts: Inter -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"/>

  <style>
    body {{ font-family: 'Inter', sans-serif; }}
    .filter-btn {{
      @apply px-4 py-2 rounded-full text-sm font-medium border border-gray-600 text-gray-300
             hover:border-yellow-400 hover:text-yellow-400 transition-all duration-200 whitespace-nowrap;
    }}
    .active-btn {{
      @apply bg-yellow-400 text-gray-900 border-yellow-400 font-bold;
    }}
    .swiper {{ padding-bottom: 40px !important; }}
    .swiper-pagination-bullet {{ background: #facc15; }}
    .swiper-pagination-bullet-active {{ background: #facc15; }}
    .featured-card {{ min-height: 320px; }}
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: #1f2937; }}
    ::-webkit-scrollbar-thumb {{ background: #facc15; border-radius: 3px; }}
  </style>
</head>

<body class="bg-gray-900 text-gray-100 dark">

  <!-- NAVBAR -->
  <nav class="sticky top-0 z-50 bg-gray-900/95 backdrop-blur-sm border-b border-gray-800 shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center gap-2">
          <i class="fa-brands fa-amazon text-yellow-400 text-2xl"></i>
          <span class="text-xl font-black text-white">{SITE_NAME}</span>
        </div>
        <div class="flex items-center gap-4">
          <span class="text-xs text-gray-400 hidden sm:block">Updated {date_str}</span>
          <a href="#products" class="bg-yellow-400 hover:bg-yellow-300 text-gray-900 font-bold text-sm px-4 py-2 rounded-lg transition-all">
            Browse Deals
          </a>
        </div>
      </div>
    </div>
  </nav>

  <!-- HERO -->
  <section class="relative overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-20 px-4">
    <div class="absolute inset-0 opacity-10">
      <div class="absolute top-10 left-10 w-72 h-72 bg-yellow-400 rounded-full blur-3xl"></div>
      <div class="absolute bottom-10 right-10 w-96 h-96 bg-blue-500 rounded-full blur-3xl"></div>
    </div>
    <div class="relative max-w-4xl mx-auto text-center" data-aos="fade-up">
      <div class="inline-flex items-center gap-2 bg-yellow-400/10 border border-yellow-400/30 text-yellow-400 text-sm font-semibold px-4 py-2 rounded-full mb-6">
        <i class="fa-solid fa-fire-flame-curved animate-pulse"></i>
        Daily Updated Amazon Bestsellers
      </div>
      <h1 class="text-4xl sm:text-5xl lg:text-6xl font-black text-white mb-4 leading-tight">
        Find the Best<br><span class="text-yellow-400">Amazon Deals</span> Today
      </h1>
      <p class="text-gray-400 text-lg max-w-2xl mx-auto mb-8">{SITE_TAGLINE}</p>
      <div class="flex justify-center gap-8 flex-wrap">
        <div class="text-center">
          <div class="text-3xl font-black text-yellow-400">{len(all_prods)}+</div>
          <div class="text-gray-400 text-sm">Top Products</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-black text-yellow-400">{len(categories)}</div>
          <div class="text-gray-400 text-sm">Categories</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-black text-yellow-400">Daily</div>
          <div class="text-gray-400 text-sm">Updated</div>
        </div>
      </div>
    </div>
  </section>

  <!-- FEATURED CAROUSEL -->
  <section class="py-12 px-4 bg-gray-900">
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center gap-3 mb-8" data-aos="fade-right">
        <div class="w-1 h-8 bg-yellow-400 rounded-full"></div>
        <h2 class="text-2xl font-black text-white">Featured Picks</h2>
        <span class="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full animate-pulse">HOT</span>
      </div>
      <div class="swiper featuredSwiper" data-aos="fade-up" data-aos-delay="100">
        <div class="swiper-wrapper">
          {swiper_slides}
        </div>
        <div class="swiper-pagination"></div>
      </div>
    </div>
  </section>

  <!-- ALL PRODUCTS -->
  <section id="products" class="py-12 px-4 bg-gray-950">
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center gap-3 mb-6" data-aos="fade-right">
        <div class="w-1 h-8 bg-yellow-400 rounded-full"></div>
        <h2 class="text-2xl font-black text-white">All Products</h2>
      </div>

      <!-- Filters -->
      <div class="flex gap-2 flex-wrap mb-8 overflow-x-auto pb-2" data-aos="fade-up">
        {cat_buttons}
      </div>

      <!-- Grid -->
      <div id="products-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {product_cards}
      </div>

      <div id="no-results" class="hidden text-center py-16 text-gray-500">
        <i class="fa-solid fa-box-open text-4xl mb-3"></i>
        <p>No products in this category yet.</p>
      </div>
    </div>
  </section>

  <!-- FOOTER -->
  <footer class="bg-gray-900 border-t border-gray-800 py-10 px-4 text-center">
    <div class="max-w-3xl mx-auto">
      <div class="flex items-center justify-center gap-2 mb-4">
        <i class="fa-brands fa-amazon text-yellow-400 text-xl"></i>
        <span class="font-black text-white">{SITE_NAME}</span>
      </div>
      <p class="text-gray-500 text-sm leading-relaxed">
        <strong class="text-gray-400">Affiliate Disclosure:</strong> {SITE_AUTHOR} is a participant in the
        Amazon Services LLC Associates Program. We earn commissions from qualifying purchases at no extra cost to you.
      </p>
      <p class="text-gray-600 text-xs mt-3">
        &copy; {datetime.now().year} {SITE_AUTHOR} &middot; Updated {date_str}
      </p>
    </div>
  </footer>

  <!-- SCRIPTS -->
  <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js"></script>
  <script>
    // Init AOS
    AOS.init({{ duration: 600, once: true, offset: 60 }});

    // Init Swiper
    new Swiper('.featuredSwiper', {{
      slidesPerView: 1,
      spaceBetween: 20,
      pagination: {{ el: '.swiper-pagination', clickable: true }},
      autoplay: {{ delay: 4000, disableOnInteraction: false }},
      loop: true,
      breakpoints: {{
        640:  {{ slidesPerView: 2 }},
        1024: {{ slidesPerView: 3 }},
      }}
    }});

    // Category filter
    function filterCat(cat, btn) {{
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active-btn'));
      btn.classList.add('active-btn');
      const cards = document.querySelectorAll('.product-card');
      let visible = 0;
      cards.forEach(c => {{
        const show = cat === 'all' || c.dataset.cat === cat;
        c.style.display = show ? 'flex' : 'none';
        if (show) visible++;
      }});
      document.getElementById('no-results').classList.toggle('hidden', visible > 0);
    }}
  </script>

</body>
</html>"""

    path = os.path.join(DOCS_DIR, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [+] {path}")


def _write_nojekyll():
    path = os.path.join(DOCS_DIR, ".nojekyll")
    with open(path, "w") as f:
        f.write("")


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
