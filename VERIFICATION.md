# PSX Hub — Verification & Change Log

## What was fixed

1. **PSX Divergence Screener**
   - Reuses the existing PSX historical-data infrastructure.
   - Added a 6-hour in-process OHLCV cache so a repeated scan does not re-download the same stock history.
   - Reduced historical-request concurrency from 6 to 4 to avoid the burst pattern that was producing PSX connection/timeout failures.
   - Added PSX AJAX-style request headers and a 15-second per-attempt timeout with the existing retry adapter.
   - Daily, weekly and monthly divergence are computed on separate bars. Weekly/monthly values come from real OHLCV resampling (`W` / `ME`), not relabelled daily results.
   - The scan remains a background job, so the browser does not sit on a long HTTP request.

2. **Mutual Funds**
   - The API is now cache-first and never waits on the 20-second MUFAP scrape during a cold start.
   - A complete bundled MUFAP directory is returned immediately if live NAV data is unavailable.
   - Live MUFAP refresh runs in the background and is single-flight guarded.
   - JSON cleaning remains enabled to convert NaN/Infinity to `null` before browser serialization.

3. **All PSX Stocks / Screener performance**
   - Symbol directory is non-blocking on cold start.
   - Duplicate background directory refreshes are prevented with a single-flight lock.
   - Existing quote/technical caches remain in place.

4. **Interactive stock charts**
   - Keeps the existing Lightweight Charts implementation and real PSX OHLCV source.
   - Added a CDN fallback from unpkg to jsDelivr.
   - Added `requestAnimationFrame()` before chart construction so charts are initialized after the stock-detail layout has a real width.
   - Added `fitContent()` after data loads and more robust resize handling.
   - Candles, volume, SMA/EMA, RSI, MACD and classic support/resistance lines remain connected to the same real PSX history cache.
   - Service-worker cache version was bumped so an old cached JavaScript bundle is not silently reused.

5. **Technical verdict / pivots**
   - Weighted 0–100 score remains transparent and bounded.
   - Breakdown `contribution` now means actual weighted score contribution rather than the unweighted -100..100 signal.
   - Pivot calculations use the most recent **completed** trading day; today's in-progress PSX bar is excluded when available.
   - Classic P/S1-S3/R1-R3 and Fibonacci 38.2%/61.8%/100% levels are both returned.

## Verification performed in this build environment

### Passed

- Python compilation of `app.py` and `psx_screener.py`.
- Node syntax validation of `static/app.js` and `static/sw.js`.
- Pivot formula regression tests.
- Fibonacci pivot formula regression tests.
- RSI bounds test.
- True weekly/monthly OHLCV resampling test.
- Synthetic technical-verdict test: score is bounded 0–100 and weighted contributions sum to `score - 50`.
- Synthetic chart-series test: SMA/EMA/RSI/MACD series lengths and candle data are internally consistent.
- Synthetic endpoint-shape tests for the chart route and divergence scan start route.
- Mutual-fund fallback test confirms 392 bundled funds are returned and NaN/Infinity are converted to JSON-safe nulls.
- Static frontend wiring checks for mutual funds, divergence, chart endpoint, Lightweight Charts and service-worker cache version.

Run the included checks with:

```bash
python tests/test_math.py
python tests/test_frontend_static.py
python -m py_compile app.py psx_screener.py
node --check static/app.js
node --check static/sw.js
```

## Important limitation of this verification

A true live Render/PSX end-to-end test could **not** be completed inside this build sandbox. The sandbox has no DNS/network access to install Flask or make outbound HTTPS requests to `dps.psx.com.pk` / MUFAP, so it would be misleading to claim that a real PSX scan, live MUFAP request, or deployed Render browser session was successfully exercised here.

The code was therefore tested at the calculation, route-shape, serialization, JavaScript syntax, and UI-wiring levels, while the external PSX/MUFAP calls were isolated rather than faked as successful live results.

For final deployment verification, the required live checks are:

1. Open `/healthz` after Render wakes from idle.
2. Open **All PSX Stocks** immediately after wake-up and confirm the fallback/warming state changes to the real PSX directory.
3. Open **Mutual Funds** and confirm the table renders immediately, then confirm live NAV/source updates after the background refresh.
4. Run **PSX Divergence Screener** and allow the background job to finish; confirm 1D/1W/1M columns differ where the underlying bars differ.
5. Open a liquid stock such as OGDC/FFC and confirm candles + volume + RSI + MACD render from real PSX data.
6. Toggle SMA/EMA and S/R, change 1M/3M/6M/1Y/3Y/5Y/ALL, resize the browser, and confirm no new network request occurs for indicator toggles and no blank chart appears.
7. Open the technical verdict and confirm the pivot basis date is the latest completed trading session.


## Second-pass fixes (2026-08-15)

- Added a second PSX-hosted data portal (`dps.csapis.com`) as a transparent fallback for the symbol directory, company pages, intraday series, and historical OHLCV endpoint. This addresses the Render error shown in the supplied screenshot where `dps.psx.com.pk` was closing connections.
- Added a complete Eligible Scrips HTML-directory fallback so the divergence scanner does not intentionally fall back to the 10 development symbols when the JSON symbol endpoint is unavailable.
- Increased the divergence scanner's market-wide worker pool from 4 to 6 and its directory cold-start grace period from 30s to 90s. It now reports `symbols_scanned`, `symbols_with_data`, and `symbols_failed` rather than implying a 10-symbol scan was a full-market scan.
- Added live PSX financial-announcement/report retrieval and official PSX report destinations to the News page and every stock detail page.
- Added a cache-busted `app.js` URL to prevent an old service-worker/browser asset from masking the new frontend.

### Second-pass local verification

- Python compilation: PASS.
- JavaScript syntax (`node --check`): PASS.
- Mathematical regression tests: PASS.
- Static frontend wiring test: PASS.
- The sandbox cannot make outbound HTTPS connections to PSX, so a real Render-hosted market-wide scan and browser interaction against the live PSX service could not be truthfully claimed here. The alternate PSX host was independently confirmed as a live PSX data-portal host during implementation.
