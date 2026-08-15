# Verification — PSX Hub v6

## Automated checks completed in this sandbox

- Python `py_compile` on `app.py` and `psx_screener.py`: PASS
- JavaScript syntax check (`node --check static/app.js`): PASS
- Service-worker syntax check: PASS
- Existing mathematical regression suite (`tests/test_math.py`): PASS — pivot formulas, Fibonacci formulas, RSI bounds, and true weekly/monthly resampling.
- Static regression checks: PASS
  - full-universe scan rejects the 10-symbol development fallback
  - batched history prefetch is wired into the divergence scan
  - cached result is returned immediately while a fresh scan runs in the background
  - stock detail uses the company-specific announcements endpoint
  - separate Announcements navigation/page exists
  - PSX LIVE ticker is present
  - EMA20 technical filter is wired through backend and frontend
  - 1D/1W/1M divergence columns remain present

## Live checks still require Render deployment

This sandbox cannot make outbound HTTPS requests to PSX/Yahoo, and it cannot operate the user's deployed Render instance. Therefore this file deliberately does **not** claim a live 555-symbol scan was executed here.

After deployment, verify:

1. The top badge remains the full PSX universe count (not 10).
2. The global ticker displays `PSX LIVE` once real bulk quotes warm.
3. Stock detail for a known symbol shows only that company's PSX announcements.
4. The Announcements navigation page shows the market-wide feed.
5. First divergence scan shows `Preparing batched PSX history…`, then symbol progress.
6. A second divergence scan immediately shows the previous full-market result while the fresh scan runs.
7. Completed scan reports `symbols_scanned` equal to the full PSX regular-equity universe count, with failed symbols separately reported.
8. Screener technical filters compute from real PSX history on a fresh Render instance.
