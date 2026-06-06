import time
from pytrends.request import TrendReq
from config import TRENDS_TOP_PRODUCTS


def analyze_trends(product_titles: list[str]) -> dict:
    titles = product_titles[:TRENDS_TOP_PRODUCTS]
    print(f"\n[AGENT TRENDS] Analizez {len(titles)} produse pe Google Trends...")

    pytrends = TrendReq(hl="en-US", tz=360)
    results = {}

    for i in range(0, len(titles), 5):
        batch_titles = titles[i:i + 5]
        keywords = [_keyword(t) for t in batch_titles]

        try:
            pytrends.build_payload(keywords, timeframe="today 3-m", geo="US")
            interest = pytrends.interest_over_time()

            for j, kw in enumerate(keywords):
                title = batch_titles[j]
                if not interest.empty and kw in interest.columns:
                    series = interest[kw]
                    avg = round(float(series.mean()), 1)
                    direction = _direction(series)
                else:
                    avg, direction = 0.0, "unknown"

                results[title] = {
                    "keyword": kw,
                    "avg_interest": avg,
                    "trend_direction": direction,
                    "trending": avg > 30,
                }

            time.sleep(1.5)

        except Exception as e:
            print(f"  [!] Trends batch error: {e}")
            for title in batch_titles:
                results[title] = {
                    "keyword": _keyword(title),
                    "avg_interest": 0.0,
                    "trend_direction": "unknown",
                    "trending": False,
                }

    trending_count = sum(1 for v in results.values() if v["trending"])
    print(f"  [+] {trending_count}/{len(titles)} produse in trend")
    return results


def _keyword(title: str) -> str:
    stop = {"with", "for", "and", "the", "a", "an", "in", "of", "to", "by",
            "pack", "set", "count", "piece", "pcs", "oz", "lb", "kg", "inch"}
    words = [w for w in title.split()[:8] if w.lower() not in stop and len(w) > 2]
    return " ".join(words[:3])[:100]


def _direction(series) -> str:
    if len(series) < 4:
        return "stable"
    mid = len(series) // 2
    first, second = series[:mid].mean(), series[mid:].mean()
    if second > first * 1.15:
        return "rising"
    if second < first * 0.85:
        return "falling"
    return "stable"
