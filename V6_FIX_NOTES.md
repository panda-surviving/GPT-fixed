# PSX Hub v6 fixes

## 1. Stock-specific announcements
- Stock detail now calls `/api/psx/announcements?symbol=SYMBOL`.
- Company-page parsing extracts only filing rows from that company's PSX page.
- Generic PSX announcement/repository links are no longer injected into an individual stock's announcement list.
- Added a separate `Announcements` navigation page for the market-wide PSX company-announcement feed and official report/category links.

## 2. PSX live ticker
- The global ticker explicitly includes `PSX LIVE` alongside Crypto Live and Forex Live.
- The old 10-symbol development quote snapshot is no longer exposed as live PSX quotes during a cold start; the ticker shows a warming state until genuine bulk PSX quotes arrive.
- Refresh interval reduced to 30 seconds.

## 3. Divergence scan speed/reliability
- Full regular-equity universe is still required; the 10-symbol development list is never accepted as the market-wide scan universe.
- Added batched Yahoo `.KA` history prefetch (5 years, 50 symbols/request batch, 3 parallel batches) to warm the in-process history cache.
- Per-symbol PSX/single-symbol providers remain fallback paths for symbols that are not available in the batch feed.
- First run reports a history-warming progress state.
- If a prior full-market result exists, `Run Scan` displays it immediately while the new full-market scan runs in the background.
- Fresh result replaces the cached result when complete.

## 4. Technical screener
- Technical indicators now use the same real PSX historical OHLCV provider as the stock chart/divergence engine, instead of waiting for Yalvon360's local recording table to accumulate 20/50/200 days.
- Added real EMA20 comparison support to the screener.
- Technical screener history is batch-prefetched before first-run per-symbol calculations.

## 5. Mathematical behavior preserved
- 1D/1W/1M RSI divergence remains independently calculated on daily, weekly-resampled, and monthly-resampled bars.
- Classic and Fibonacci pivot formulas remain unchanged.
