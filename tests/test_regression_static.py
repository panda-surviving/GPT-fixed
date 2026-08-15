from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'app.py').read_text()
JS = (ROOT / 'static' / 'app.js').read_text()
SW = (ROOT / 'static' / 'sw.js').read_text()


def test_psx_historical_request_has_required_parameters():
    assert 'data={"month":m,"year":y,"symbol":symbol}' in APP
    assert 'data={"symbol": symbol.upper()}' not in APP


def test_full_scan_never_uses_ten_symbol_fallback():
    start = APP.index('def run_psx_divergence_scan')
    body = APP[start:APP.index('def _run_psx_divergence_job_in_background', start)]
    assert 'get_symbols_for_full_scan()' in body
    assert 'get_symbols_nonblocking()' not in body
    assert 'FALLBACK_QUOTES' not in body


def test_real_history_fallbacks_exist():
    assert 'PSX_SCRAPER_API_BASE' in APP
    assert 'fetch_psx_scraper_history' in APP
    assert 'query1.finance.yahoo.com/v8/finance/chart/{symbol}.KA' in APP


def test_chart_monthly_resample_is_pandas_compatible():
    assert '"ALL": {"days": None, "resample": "M"}' in APP
    assert '"div_1m", full_df, "M"' in APP


def test_indicator_values_and_pivots_are_rendered():
    assert 'Current Indicator Values' in JS
    assert 'iv.sma20' in JS and 'iv.ema200' in JS
    assert 'pivot_points' in JS
    assert 'Fibonacci Pivot Points' in JS


def test_service_worker_cache_is_bumped():
    assert 'psx-360-shell-v5' in SW
