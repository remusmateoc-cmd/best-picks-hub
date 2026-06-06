from config import PROFIT_SETTINGS


def enrich_products_with_margins(products: list[dict]) -> list[dict]:
    print(f"\n[AGENT MARGIN] Calculez margini pentru {len(products)} produse...")
    enriched = [_enrich(p) for p in products if p.get("price") and p["price"] > 0]

    good = sum(1 for p in enriched if p.get("opportunity_score") in ("EXCELLENT", "GOOD"))
    skip = sum(1 for p in enriched if p.get("opportunity_score") == "SKIP")
    print(f"  [+] {good} oportunitati bune | {skip} de sarit")
    return enriched


def _enrich(product: dict) -> dict:
    price = product["price"]
    s = PROFIT_SETTINGS

    aliexpress_cost = price * s["aliexpress_cost_ratio"]
    amazon_fee = price * (s["amazon_fee_percent"] / 100)
    shipping = s["shipping_cost_usd"]
    total_cost = aliexpress_cost + amazon_fee + shipping

    profit = price - total_cost
    margin = (profit / price * 100) if price > 0 else 0

    if margin >= s["target_margin_percent"] and profit >= s["min_profit_usd"]:
        score, score_val = "EXCELLENT", 5
    elif margin >= s["min_margin_percent"] and profit >= s["min_profit_usd"]:
        score, score_val = "GOOD", 3
    elif profit >= s["min_profit_usd"]:
        score, score_val = "MARGINAL", 2
    else:
        score, score_val = "SKIP", 1

    return {
        **product,
        "aliexpress_cost": round(aliexpress_cost, 2),
        "amazon_fee": round(amazon_fee, 2),
        "shipping": shipping,
        "total_cost": round(total_cost, 2),
        "estimated_profit": round(profit, 2),
        "margin_percent": round(margin, 1),
        "opportunity_score": score,
        "score_value": score_val,
    }
