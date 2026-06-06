"""
Promo Agent — genereaza posturi de promovare pentru Facebook, TikTok, Pinterest, Reddit.
Citeste produsele din ultimul raport JSON si genereaza continut gata de publicat.
"""

import os
import json
import glob
import random
from datetime import datetime
from config import REPORT_OUTPUT_DIR, SITE_NAME, AMAZON_AFFILIATE_TAG

PROMO_DIR = "promotions"

# Subreddits potrivite pe categorie
REDDIT_SUBS = {
    "Electronics":       ["r/deals", "r/frugal", "r/gadgets", "r/electronics"],
    "Home & Kitchen":    ["r/deals", "r/frugal", "r/homeimprovement", "r/BuyItForLife"],
    "Sports & Outdoors": ["r/deals", "r/running", "r/fitness", "r/hiking"],
    "Toys & Games":      ["r/deals", "r/toys", "r/boardgames"],
    "Beauty":            ["r/deals", "r/SkincareAddiction", "r/MakeupAddiction"],
    "Health":            ["r/deals", "r/frugal", "r/health"],
    "Pet Supplies":      ["r/deals", "r/dogs", "r/cats", "r/pets"],
    "Office Products":   ["r/deals", "r/frugal", "r/WorkOnline", "r/productivity"],
}

TIKTOK_HOOKS = [
    "POV: You found the best Amazon deal of the week 🔥",
    "Amazon products that are actually worth it 💯",
    "I tested this so you don't have to ✅",
    "This Amazon find is going viral for a reason 👀",
    "Stop overpaying — this is the smart buy right now 🛒",
    "Rating Amazon bestsellers so you know what to buy 📦",
]

FACEBOOK_INTROS = [
    "🔥 OFERTA ZILEI pe Amazon:",
    "💡 Produsul saptamanii — trebuie sa il vezi:",
    "📦 Am gasit ceva interesant pe Amazon:",
    "⚡ Deal alert! Verifica asta acum:",
    "🛒 Recomandarea mea de azi de pe Amazon:",
]


def run(products: list[dict]) -> str:
    """Genereaza posturi pentru toate platformele. Returneaza calea fisierului HTML."""
    os.makedirs(PROMO_DIR, exist_ok=True)

    top = _get_top_products(products)
    if not top:
        print("  [!] Nu sunt produse bune pentru promovare.")
        return ""

    date_str  = datetime.now().strftime("%Y-%m-%d")
    posts = {
        "facebook": [_facebook_post(p) for p in top[:5]],
        "tiktok":   [_tiktok_script(p) for p in top[:3]],
        "pinterest":[_pinterest_pin(p) for p in top[:5]],
        "reddit":   [_reddit_post(p) for p in top[:3]],
    }

    html_path = os.path.join(PROMO_DIR, f"promo_{date_str}.html")
    _save_html(posts, html_path, date_str)

    total = sum(len(v) for v in posts.values())
    print(f"  [+] {total} posturi generate: {html_path}")
    return html_path


def _get_top_products(products: list[dict]) -> list[dict]:
    good = [p for p in products if p.get("opportunity_score") in ("EXCELLENT", "GOOD")]
    return sorted(good, key=lambda x: x.get("avg_interest", 0), reverse=True)


def _affiliate_link(p: dict) -> str:
    asin = p.get("asin", "")
    tag  = AMAZON_AFFILIATE_TAG
    if asin:
        return f"https://www.amazon.com/dp/{asin}?tag={tag}"
    return p.get("amazon_url", "")


def _facebook_post(p: dict) -> dict:
    intro  = random.choice(FACEBOOK_INTROS)
    title  = p.get("title", "")[:60]
    price  = p.get("price", 0)
    rating = p.get("rating", 0)
    link   = _affiliate_link(p)
    cat    = p.get("category", "")
    trend  = p.get("trend_direction", "stable")
    trend_text = "📈 In trend acum!" if trend == "rising" else ""

    text = f"""{intro}

✅ {title}
💰 Pret: ${price:.2f}
⭐ Rating: {rating}/5
{trend_text}

👉 Link: {link}

#Amazon #Deal #{''.join(cat.split())} #Reduceri #Shopping #BestPicks"""

    return {"platform": "Facebook", "category": cat, "text": text, "link": link}


def _tiktok_script(p: dict) -> dict:
    hook   = random.choice(TIKTOK_HOOKS)
    title  = p.get("title", "")[:50]
    price  = p.get("price", 0)
    rating = p.get("rating", 0)
    link   = _affiliate_link(p)
    cat    = p.get("category", "")

    script = f"""🎬 SCRIPT TIKTOK / REELS (30-60 secunde)

HOOK (primele 3 sec — spui asta uitandu-te direct in camera):
"{hook}"

CONTINUT (15-30 sec):
"Hai sa va arat {title}.
Costa doar ${price:.2f} pe Amazon, are {rating} stele din 5
si e unul dintre cele mai vandute din categoria {cat}.
Eu l-am testat si sincer... merita fiecare cent."

CALL TO ACTION (ultimele 5 sec):
"Link-ul e in bio! Nu ratati oferta."

CAPTION:
{hook} #{cat.replace(' ', '')} #Amazon #AmazonFinds #Deal

BIO LINK: {link}"""

    return {"platform": "TikTok/Reels", "category": cat, "text": script, "link": link}


def _pinterest_pin(p: dict) -> dict:
    title  = p.get("title", "")[:100]
    price  = p.get("price", 0)
    rating = p.get("rating", 0)
    link   = _affiliate_link(p)
    cat    = p.get("category", "")

    description = f"""✨ {title}

⭐ {rating}/5 stele pe Amazon
💰 Doar ${price:.2f}

Unul dintre cele mai vandute produse din categoria {cat} pe Amazon.
Calitate excelenta la un pret accesibil — perfect pentru oricine cauta
cele mai bune produse fara sa plateasca prea mult.

🔗 Gasesti link-ul in profil!

#{cat.replace(' ', '')} #AmazonFinds #BestProducts #Shopping #Deals #{''.join(title.split()[:2])}"""

    pin_title = f"Best {cat} Deal: {title[:60]}"

    return {"platform": "Pinterest", "category": cat, "pin_title": pin_title,
            "text": description, "link": link}


def _reddit_post(p: dict) -> dict:
    title  = p.get("title", "")
    price  = p.get("price", 0)
    rating = p.get("rating", 0)
    link   = _affiliate_link(p)
    cat    = p.get("category", "")
    subs   = REDDIT_SUBS.get(cat, ["r/deals"])

    post_title = f"[Deal] {title[:80]} — ${price:.2f} | ⭐{rating}/5"

    body = f"""Found this while browsing Amazon bestsellers and thought this community would appreciate it.

**Product:** {title}
**Price:** ${price:.2f}
**Rating:** {rating}/5 stars (Amazon Bestseller)
**Category:** {cat}

This has been consistently in Amazon's top sellers.
Solid reviews across the board — worth checking out if you've been looking for something in this category.

[View on Amazon]({link})

---
*Disclosure: This is an affiliate link. I may earn a small commission at no extra cost to you.*"""

    return {"platform": "Reddit", "category": cat, "post_title": post_title,
            "body": body, "subreddits": subs, "link": link}


def _save_html(posts: dict, path: str, date_str: str):
    sections = ""

    platform_config = {
        "facebook":  ("📘 Facebook Groups", "#1877f2", "Copiaza si posteaza in grupuri de oferte/deals"),
        "tiktok":    ("🎵 TikTok / Reels",  "#000000", "Filmeaza urmand scriptul. Pune link-ul in bio."),
        "pinterest": ("📌 Pinterest",        "#e60023", "Creeaza un pin nou, copiaza titlul si descrierea."),
        "reddit":    ("🤖 Reddit",           "#ff4500", "Posteaza in subreddit-urile listate. Nu spama."),
    }

    for key, items in posts.items():
        label, color, hint = platform_config[key]
        cards = ""
        for item in items:
            if key == "reddit":
                content = f"<strong>Titlu post:</strong><br><code>{item['post_title']}</code><br><br>" \
                          f"<strong>Subreddits:</strong> {', '.join(item['subreddits'])}<br><br>" \
                          f"<strong>Body:</strong><br><pre>{item['body']}</pre>"
            elif key == "pinterest":
                content = f"<strong>Titlu pin:</strong><br><code>{item['pin_title']}</code><br><br>" \
                          f"<strong>Descriere:</strong><br><pre>{item['text']}</pre>"
            else:
                content = f"<pre>{item['text']}</pre>"

            cards += f"""
            <div class="post-card">
                <div class="post-cat">{item['category']}</div>
                {content}
                <a href="{item['link']}" target="_blank" class="post-link">🔗 Link produs</a>
                <button onclick="copyText(this)" class="copy-btn">📋 Copiaza</button>
            </div>"""

        sections += f"""
        <div class="platform-section">
            <div class="platform-header" style="border-left:5px solid {color}">
                <h2>{label}</h2>
                <p class="hint">💡 {hint}</p>
            </div>
            <div class="posts-grid">{cards}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Posturi Promovare — {date_str}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',Arial,sans-serif;background:#0d0d1a;color:#e0e0e0;line-height:1.6}}
.header{{background:linear-gradient(135deg,#1a1a2e,#16213e);padding:30px 40px;border-bottom:3px solid #00c851}}
.header h1{{color:#00c851;font-size:1.8rem}}
.header p{{color:#888;margin-top:5px}}
.container{{max-width:1100px;margin:0 auto;padding:30px 20px}}
.platform-section{{margin-bottom:40px}}
.platform-header{{background:#1a1a2e;padding:16px 20px;border-radius:10px;margin-bottom:16px}}
.platform-header h2{{font-size:1.2rem;color:#fff}}
.hint{{color:#888;font-size:.85rem;margin-top:4px}}
.posts-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px}}
.post-card{{background:#1a1a2e;border-radius:10px;padding:18px;display:flex;flex-direction:column;gap:10px}}
.post-cat{{font-size:.72rem;color:#00c851;font-weight:700;text-transform:uppercase}}
pre{{background:#0d0d1a;padding:12px;border-radius:8px;font-size:.78rem;white-space:pre-wrap;word-break:break-word;color:#ccc;max-height:300px;overflow-y:auto}}
code{{background:#0d0d1a;padding:6px 10px;border-radius:6px;font-size:.82rem;display:block;color:#ffbb33}}
.post-link{{color:#ff9900;font-size:.82rem;text-decoration:none}}
.post-link:hover{{text-decoration:underline}}
.copy-btn{{background:#00c851;color:#000;border:none;padding:8px 16px;border-radius:8px;cursor:pointer;font-weight:700;font-size:.82rem;margin-top:4px}}
.copy-btn:hover{{background:#00a844}}
.footer{{text-align:center;padding:20px;color:#444;font-size:.78rem}}
</style>
</head>
<body>
<div class="header">
  <h1>📣 Posturi Promovare — {date_str}</h1>
  <p>Gata de publicat pe Facebook, TikTok, Pinterest si Reddit</p>
</div>
<div class="container">
  {sections}
</div>
<div class="footer">Generat automat de {SITE_NAME} Promo Agent</div>
<script>
function copyText(btn) {{
  const card = btn.closest('.post-card');
  const pre = card.querySelector('pre');
  const text = pre ? pre.innerText : card.innerText;
  navigator.clipboard.writeText(text).then(() => {{
    btn.textContent = '✅ Copiat!';
    setTimeout(() => btn.textContent = '📋 Copiaza', 2000);
  }});
}}
</script>
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def load_latest_products() -> list[dict]:
    files = sorted(glob.glob(os.path.join(REPORT_OUTPUT_DIR, "data_*.json")))
    if not files:
        return []
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)
