# PSX Hub v4 — Verification & Change Log

## v4 fixes implemented

### 1. Complete PSX equity universe — no 10-stock masquerade
- The **All PSX Stocks** directory now treats the official PSX **Eligible Scrips → Regular Deliverable Equity Market** as the authoritative universe.
- The JSON `/symbols` endpoint is accepted only when it demonstrably contains a large directory (100+ entries). A 10-symbol development response is rejected as partial data.
- `/api/symbols` no longer returns the 10-symbol development snapshot. On a true upstream outage it returns an explicit 503 instead of misleadingly displaying 10 stocks.
- The divergence scan uses `get_symbols_for_full_scan()` and therefore cannot silently scan the development fallback.
- The official PSX Eligible Scrips page currently exposes the regular equity directory; this is the source the deployed app is designed to use.

### 2. Personalized PSX Divergence Screener
The screen now visibly documents and returns the requested rules rather than only showing generic divergence lists:
- 52-week low proximity: within **3%** of the 52-week low.
- RSI divergence independently calculated on **1D, 1W and 1M** bars.
- Bullish divergence pivot RSI flags at **≤30** and **≤50**.
- Bearish divergence pivot RSI flags at **≥70** and **≥90**.
- True recursive **Heikin-Ashi** latest-candle confirmation.
- Higher-high/higher-low vs lower-high/lower-low structure.
- Master **Personalized PSX Setup — All Matches** table with the above columns.
- Existing dedicated sections remain: 52W-low + bullish divergence, all near-low stocks, all bullish divergence, all bearish divergence, uptrend divergence and downtrend divergence.
- Scan progress reports the actual universe count, checked count, usable-history count and failures.

### 3. Interactive chart / Price Graph
- The stock-detail **Price Graph** now falls back to the real historical chart data when PSX intraday data is unavailable. It no longer disappears simply because the intraday endpoint fails.
- Interactive chart continues to use real historical OHLCV and Lightweight Charts.
- Added backend and frontend OHLC validation so malformed upstream `high`/`low` values cannot draw impossible candle wicks to zero.
- This specifically addresses the screenshot where vertical lines extended abnormally far below the candle bodies.
- The vertical line on a normal candlestick is a wick; the v4 sanitizer removes only malformed/extreme values, not legitimate wicks.
- Volume, RSI, MACD, SMA20/50/200, EMA20/50/200 and classic S/R remain available.
- Chart API now identifies its real-market-data provider chain in `data_source`.
- Static app asset query string and service-worker cache are both bumped to v4.

### 4. Stock quote robustness
- `/api/stock/<symbol>` always returns JSON even if the optional intraday provider throws an exception.
- The exact browser-visible `The string did not match the expected pattern.` failure can no longer blank the whole stock-detail response merely because intraday data failed.

### 5. Existing financial features retained
- Financial announcements and official financial/analysis report destinations remain included on stock detail and News.
- Mutual Funds JSON safety/cache fixes remain included.
- Consolidated technical verdict and classic/Fibonacci pivot calculations remain included.

## Local verification completed

PASS:
- `python -m py_compile app.py psx_screener.py`
- `node --check static/app.js`
- `node --check static/sw.js`
- `python tests/test_frontend_static.py`
- `pytest -q tests/test_math.py tests/test_regression_static.py` → **6 passed**
- Static regression confirms the full-scan route uses `get_symbols_for_full_scan()` and does not contain a `FALLBACK_QUOTES` scan path.
- Static regression confirms the historical PSX POST shape includes `month`, `year`, and `symbol`.
- Static regression confirms chart, RSI, EMA/SMA, pivot and financial-announcement UI wiring.

A separate `tests/test_v4_regressions.py` is included for a real Flask environment. It covers malformed OHLC wick sanitization, stock-detail JSON resilience, rejection of the 10-symbol directory fallback, full-universe scan accounting, and recursive Heikin-Ashi calculation. This sandbox does not have Flask installed and has no outbound package/network access, so that Flask endpoint suite could not be executed here. The source itself compiles successfully.

## Live deployment verification still required

This build environment cannot establish outbound HTTPS connections to PSX/Yahoo/MUFAP and cannot interact with the user's Render deployment. Therefore I am **not** claiming a live 700+ stock scan was executed here.

After deploying v4, verify:
1. `/api/symbols` returns the full PSX regular-equity directory and **not 10**.
2. **All PSX Stocks** shows the same directory count.
3. **Divergence Screener → Run Scan** reports the actual universe count and progresses through every symbol.
4. A stock detail page shows the Price Graph even when intraday PSX data is unavailable, using the real historical chart fallback.
5. Interactive candles have normal OHLC wicks; no repeated vertical lines dropping to an impossible zero/baseline.
6. 1M/3M/6M/1Y/3Y/5Y/ALL, SMA/EMA, RSI, MACD and S/R toggles render correctly.
7. The Personalized PSX Setup table contains 1D/1W/1M divergence and RSI-zone columns.
8. Financial announcements/reports and Mutual Funds continue to load.
