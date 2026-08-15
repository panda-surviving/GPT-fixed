# PSX Hub second-pass build notes — 2026-08-15

## Fixes in this package

1. **Full PSX divergence scan**
   - The scanner now resolves the complete PSX eligible-scrip directory instead of falling back to the 10 development symbols when the primary symbol JSON endpoint is unavailable.
   - Added the PSX-hosted `dps.csapis.com` fallback for the symbol directory and historical OHLCV.
   - Increased market-wide concurrency to 6 workers.
   - The UI reports exact `symbols_scanned`, `symbols_with_data`, and `symbols_failed` counts.
   - Daily, weekly and monthly RSI divergence are independently calculated from daily/weekly/monthly bars.

2. **Live stock chart data**
   - Chart data now uses the same PSX historical source with the alternate PSX host fallback.
   - Candles, volume, SMA/EMA, RSI, MACD and pivot levels remain real computed data; there is no demo series fallback.
   - A cache-busted frontend asset URL prevents an old service-worker/browser asset from hiding the new chart code.

3. **Technical verdict / support & resistance**
   - Existing weighted 0–100 verdict and indicator breakdown retained.
   - Classic and Fibonacci pivots retained and returned by both verdict and chart endpoints.

4. **Financial announcements and reports**
   - Added `/api/psx/financials`.
   - Added live PSX announcement/report cards to the News page and each stock detail page.
   - Added official PSX financial reports, analysis reports and downloads destinations.

5. **Mutual funds**
   - Existing NaN/Infinity-safe JSON handling and MUFAP cache-first fallback retained.

## Render deployment

Build command:

`pip install -r requirements.txt`

Start command:

`gunicorn app:app --workers 1 --threads 8 --timeout 120 --keep-alive 5`

Health check:

`/healthz`

## Verification performed in this sandbox

- `python -m py_compile app.py psx_screener.py` — PASS
- `node --check static/app.js` — PASS
- `python tests/test_math.py` — PASS
- `python tests/test_frontend_static.py` — PASS
- Live outbound HTTPS from this sandbox to PSX is unavailable, so a live Render scan/browser session against PSX could not be honestly claimed as completed here. The code therefore uses the second PSX-hosted data portal as an explicit runtime fallback rather than pretending that the first host is always reachable.

## v3 regression fix (2026-08-15)

The supplied production screenshots exposed a concrete defect that was still present in v2: `/historical` was POSTed with only `symbol`. The current PSX historical page requires the month/year/symbol request parameters. The invalid request was surfacing in the browser as `The string did not match the expected pattern.`

This build changes the historical provider chain to:
1. Dedicated PSX scraper API cache (5-year daily OHLCV, if reachable).
2. Yahoo Finance `.KA` daily OHLCV (one request returns the full daily series).
3. Correct PSX Data Portal monthly `month/year/symbol` requests as the final fallback.

The full divergence scan no longer uses the 10-symbol development fallback. It obtains the real universe from PSX or the dedicated PSX scraper API and fails explicitly if neither complete universe is available.

The chart now reports its data source, uses real OHLCV, and the stock-detail technical verdict visibly renders the current RSI/MACD/SMA/EMA values as well as the classic and Fibonacci pivot tables. The monthly resampling rule was changed from `ME` to `M` for pandas compatibility.
