#!/usr/bin/env python3
"""
Product Research Agent v1.0
Scaneaza Amazon bestsellers, Google Trends, calculeaza margini si genereaza raport HTML.

Utilizare:
    python main.py
"""

import os
import sys
import time
import webbrowser
from datetime import datetime

from agents.amazon_agent import fetch_all_categories
from agents.trends_agent import analyze_trends
from agents.margin_calculator import enrich_products_with_margins
from agents.affiliate_agent import enrich_with_affiliate
from agents.report_generator import generate_report
from agents.promo_agent import run as generate_promos


def main():
    _banner()
    start = time.time()

    # 1. Amazon bestsellers
    print("\n[1/5] Colectez bestsellers de pe Amazon...")
    products = fetch_all_categories()

    if not products:
        print("\n[!] Nu s-au gasit produse.")
        print("    Amazon poate bloca request-urile. Incearca:")
        print("    - Asteapta 5 minute si ruleaza din nou")
        print("    - Foloseste un VPN (server US)")
        sys.exit(1)

    print(f"     {len(products)} produse colectate din {len(set(p['category'] for p in products))} categorii")

    # 2. Margini de profit
    print("\n[2/5] Calculez margini de profit...")
    products = enrich_products_with_margins(products)

    # 3. Google Trends pentru top candidati
    print("\n[3/5] Analizez Google Trends...")
    top_titles = [
        p["title"] for p in products
        if p.get("opportunity_score") in ("EXCELLENT", "GOOD") and p.get("title")
    ][:30]

    trends_data = analyze_trends(top_titles) if top_titles else {}

    # 4. Link-uri affiliate
    print("\n[4/5] Generez link-uri affiliate...")
    products = enrich_with_affiliate(products)
    print(f"  [+] Link-uri generate pentru {len(products)} produse")

    # 5. Raport HTML
    print("\n[5/5] Generez raport HTML...")
    report_path = generate_report(products, trends_data)
    elapsed = time.time() - start

    _summary(products, report_path, elapsed)

    # Deschide raportul intern in browser
    try:
        abs_path = os.path.abspath(report_path)
        webbrowser.open(f"file:///{abs_path.replace(os.sep, '/')}")
    except Exception:
        pass

    # Genereaza posturi de promovare
    print("\n[6/6] Generez posturi de promovare...")
    promo_path = generate_promos(products)
    if promo_path:
        try:
            webbrowser.open(f"file:///{os.path.abspath(promo_path).replace(os.sep, '/')}")
        except Exception:
            pass

    # Deploy site public GitHub Pages
    print("\n  Vrei sa actualizezi si site-ul public? (y/n): ", end="", flush=True)
    try:
        answer = input().strip().lower()
    except EOFError:
        answer = "n"

    if answer == "y":
        import deploy as _deploy
        _deploy.main()


def _banner():
    print("=" * 62)
    print("  PRODUCT RESEARCH AGENT v1.0")
    print(f"  {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("=" * 62)
    print("  Agenti activi: Amazon | Trends | Margin | Affiliate | Report")
    print("=" * 62)


def _summary(products: list, report_path: str, elapsed: float):
    excellent = [p for p in products if p.get("opportunity_score") == "EXCELLENT"]
    good      = [p for p in products if p.get("opportunity_score") == "GOOD"]

    print("\n" + "=" * 62)
    print(f"  RAPORT GENERAT IN {elapsed:.0f}s")
    print(f"  Fisier: {report_path}")
    print("=" * 62)
    print(f"\n  Produse analizate : {len(products)}")
    print(f"  EXCELLENT         : {len(excellent)}")
    print(f"  GOOD              : {len(good)}")

    top_all = excellent + good
    if top_all:
        best = max(top_all, key=lambda x: x.get("score_value", 0) * 100 + x.get("avg_interest", 0))
        print(f"\n  CEL MAI BUN PRODUS:")
        print(f"  {best.get('title','')[:58]}")
        print(f"  Profit ~${best.get('estimated_profit',0):.2f} | Marja {best.get('margin_percent',0):.1f}%")
        print(f"  Categorie: {best.get('category','')} | Trend: {best.get('trend_direction','?')}")

    print(f"\n  Raportul s-a deschis automat in browser.")
    print()


if __name__ == "__main__":
    main()
