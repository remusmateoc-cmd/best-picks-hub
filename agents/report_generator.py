import os
import json
from datetime import datetime
from config import REPORT_OUTPUT_DIR
from agents.affiliate_agent import get_alternative_programs

SCORE_COLOR = {
    "EXCELLENT": "#00c851",
    "GOOD":      "#ffbb33",
    "MARGINAL":  "#ff8800",
    "SKIP":      "#ff4444",
}

TREND_ICON = {"rising": "📈", "falling": "📉", "stable": "➡️", "unknown": "❓"}


def generate_report(products: list[dict], trends_data: dict) -> str:
    os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Merge trend data
    for p in products:
        td = trends_data.get(p.get("title", ""), {})
        p.setdefault("trend_direction", td.get("trend_direction", "unknown"))
        p.setdefault("avg_interest", td.get("avg_interest", 0))
        p.setdefault("trending", td.get("trending", False))

    ranked = sorted(products, key=lambda x: (x.get("score_value", 0), x.get("avg_interest", 0)), reverse=True)
    top = [p for p in ranked if p.get("opportunity_score") in ("EXCELLENT", "GOOD")]

    html_path = os.path.join(REPORT_OUTPUT_DIR, f"report_{ts}.html")
    json_path = os.path.join(REPORT_OUTPUT_DIR, f"data_{ts}.json")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(_build_html(ranked, top))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ranked, f, indent=2, ensure_ascii=False)

    return html_path


def _build_html(all_products: list, top: list) -> str:
    date_str = datetime.now().strftime("%d %B %Y, %H:%M")
    stats = {
        "total":     len(all_products),
        "excellent": sum(1 for p in all_products if p.get("opportunity_score") == "EXCELLENT"),
        "good":      sum(1 for p in all_products if p.get("opportunity_score") == "GOOD"),
        "categories":len(set(p.get("category", "") for p in all_products)),
    }

    cards_html = "".join(_card(p) for p in top[:12])
    rows_html  = "".join(_row(p) for p in all_products[:60])
    affiliate_html = _affiliate_section()

    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Product Research — {date_str}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',Arial,sans-serif;background:#0d0d1a;color:#e0e0e0;line-height:1.5}}
.hdr{{background:linear-gradient(135deg,#1a1a2e,#16213e);padding:40px;text-align:center;border-bottom:3px solid #00c851}}
.hdr h1{{font-size:2rem;color:#00c851;margin-bottom:8px}}
.hdr p{{color:#888}}
.stats{{display:flex;justify-content:center;gap:40px;padding:24px;background:#12122a;flex-wrap:wrap}}
.stat .n{{font-size:2.2rem;font-weight:700;color:#00c851}}
.stat .l{{color:#888;font-size:.8rem;text-transform:uppercase;letter-spacing:.05em}}
.sec{{padding:32px 40px}}
.sec h2{{color:#00c851;font-size:1.2rem;margin-bottom:20px;border-left:4px solid #00c851;padding-left:12px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px}}
.card{{background:#1a1a2e;border-radius:12px;padding:20px;border-left:5px solid #333;transition:transform .2s}}
.card:hover{{transform:translateY(-3px)}}
.badge{{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.72rem;font-weight:700;color:#000;margin-bottom:10px}}
.card h3{{font-size:.88rem;color:#fff;margin-bottom:6px;line-height:1.4}}
.cat{{font-size:.75rem;color:#666;margin-bottom:14px}}
.metrics{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}}
.m{{background:#0d0d1a;padding:8px 10px;border-radius:8px}}
.m .ml{{font-size:.68rem;color:#555}}
.m .mv{{font-size:.92rem;font-weight:600}}
.profit-val{{color:#00c851;font-size:1rem}}
.alink{{display:inline-block;margin-top:12px;color:#ff9900;font-size:.82rem;text-decoration:none}}
.alink:hover{{text-decoration:underline}}
table{{width:100%;border-collapse:collapse;font-size:.82rem}}
th{{background:#1a1a2e;color:#00c851;padding:10px 12px;text-align:left;white-space:nowrap}}
td{{padding:9px 12px;border-bottom:1px solid #1a1a2e;vertical-align:middle}}
tr:hover td{{background:#1a1a2e}}
.prog-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px}}
.prog{{background:#1a1a2e;border-radius:10px;padding:16px}}
.prog h4{{color:#ffbb33;margin-bottom:6px}}
.prog p{{font-size:.8rem;color:#aaa}}
.foot{{text-align:center;padding:24px;color:#444;font-size:.78rem;border-top:1px solid #1a1a2e}}
</style>
</head>
<body>
<div class="hdr">
  <h1>🤖 Product Research Agent</h1>
  <p>Raport generat: {date_str} &nbsp;|&nbsp; {stats["total"]} produse &nbsp;|&nbsp; {stats["categories"]} categorii</p>
</div>

<div class="stats">
  <div class="stat"><div class="n">{stats["excellent"]}</div><div class="l">Excellent</div></div>
  <div class="stat"><div class="n">{stats["good"]}</div><div class="l">Good</div></div>
  <div class="stat"><div class="n">{stats["total"]}</div><div class="l">Analizate</div></div>
  <div class="stat"><div class="n">{stats["categories"]}</div><div class="l">Categorii</div></div>
</div>

<div class="sec">
  <h2>🏆 Top Oportunitati de Profit</h2>
  <div class="grid">{cards_html}</div>
</div>

<div class="sec">
  <h2>📊 Toate Produsele</h2>
  <table>
    <thead><tr>
      <th>Scor</th><th>Produs</th><th>Categorie</th>
      <th>Pret Amazon</th><th>Cost AliEx~</th><th>Profit~</th><th>Marja</th><th>Trend</th>
    </tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>

{affiliate_html}

<div class="foot">
  <p>⚠️ Estimarile sunt orientative. Verifica preturile reale pe AliExpress/Alibaba inainte de orice decizie.</p>
  <p>Product Research Agent v1.0 — generat automat</p>
</div>
</body>
</html>"""


def _card(p: dict) -> str:
    color = SCORE_COLOR.get(p.get("opportunity_score", "SKIP"), "#555")
    icon  = TREND_ICON.get(p.get("trend_direction", "unknown"), "❓")
    url   = p.get("affiliate_url") or p.get("amazon_url", "")
    link  = f'<a class="alink" href="{url}" target="_blank">View pe Amazon →</a>' if url else ""

    return f"""
<div class="card" style="border-left-color:{color}">
  <span class="badge" style="background:{color}">{p.get("opportunity_score","")}</span>
  <h3>{_trunc(p.get("title",""),80)}</h3>
  <div class="cat">{p.get("category","")}</div>
  <div class="metrics">
    <div class="m"><div class="ml">Pret Amazon</div><div class="mv">${p.get("price",0):.2f}</div></div>
    <div class="m"><div class="ml">Cost AliEx ~</div><div class="mv">${p.get("aliexpress_cost",0):.2f}</div></div>
    <div class="m"><div class="ml">Profit Net ~</div><div class="mv profit-val">${p.get("estimated_profit",0):.2f}</div></div>
    <div class="m"><div class="ml">Marja</div><div class="mv">{p.get("margin_percent",0):.1f}%</div></div>
    <div class="m"><div class="ml">Google Trend {icon}</div><div class="mv">{p.get("avg_interest",0):.0f}/100</div></div>
    <div class="m"><div class="ml">Comision Aff.</div><div class="mv">${p.get("estimated_commission",0):.2f}</div></div>
  </div>
  {link}
</div>"""


def _row(p: dict) -> str:
    color = SCORE_COLOR.get(p.get("opportunity_score", "SKIP"), "#555")
    icon  = TREND_ICON.get(p.get("trend_direction", "unknown"), "❓")
    return f"""<tr>
  <td><span style="color:{color};font-weight:700">{p.get("opportunity_score","")}</span></td>
  <td title="{p.get("title","")}">{_trunc(p.get("title","N/A"),50)}</td>
  <td>{p.get("category","")}</td>
  <td>${p.get("price",0):.2f}</td>
  <td>${p.get("aliexpress_cost",0):.2f}</td>
  <td><strong>${p.get("estimated_profit",0):.2f}</strong></td>
  <td>{p.get("margin_percent",0):.1f}%</td>
  <td>{icon} {p.get("avg_interest",0):.0f}</td>
</tr>"""


def _affiliate_section() -> str:
    programs = get_alternative_programs()
    cards = "".join(
        f'<div class="prog"><h4>{p["name"]}</h4>'
        f'<p>Comision: <strong>{p["commission"]}</strong><br>'
        f'Nisa: {p["niche"]}</p></div>'
        for p in programs
    )
    return f"""
<div class="sec">
  <h2>💰 Programe Affiliate Alternative (Venit 100% Pasiv)</h2>
  <div class="prog-grid">{cards}</div>
  <p style="margin-top:16px;font-size:.82rem;color:#666">
    Inregistreaza-te gratuit, pune link-urile pe blog/YouTube/TikTok si castigi comision automat.
  </p>
</div>"""


def _trunc(s: str, n: int) -> str:
    return s[:n] + "..." if len(s) > n else s
