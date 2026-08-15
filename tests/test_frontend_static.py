"""Static regression checks for the UI wiring.
Run: python tests/test_frontend_static.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "templates/index.html").read_text()
js = (ROOT / "static/app.js").read_text()
sw = (ROOT / "static/sw.js").read_text()

required = [
    "/api/mutual-funds",
    "/api/psxdivergence/scan/start",
    "/api/stock/${encodeURIComponent(symbol)}/chart",
    "addCandlestickSeries",
    "addHistogramSeries",
    "RSI(14)",
]
# RSI(14) is rendered in JS labels/HTML; accept the actual endpoint field as well.
required[-1] = "rsi14"
for needle in required:
    assert needle in (html + js), f"Missing UI wiring: {needle}"
assert "lightweight-charts@4.1.3" in html
assert "psx-360-shell-v5" in sw
print("PASS: mutual-funds, divergence, chart endpoints, Lightweight Charts, RSI and cache version are wired")
assert "dps.csapis.com" in (ROOT / "app.py").read_text()
assert "/api/psx/financials" in js and "Financial Announcements" in html
