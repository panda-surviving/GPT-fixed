import numpy as np
import pandas as pd
import app


def synthetic_history(n=520):
    dates = pd.bdate_range(end=pd.Timestamp('2026-08-14'), periods=n)
    t = np.arange(n, dtype=float)
    close = 100 + 0.06*t + 4*np.sin(t/9) + 2*np.sin(t/27)
    open_ = close + 0.4*np.sin(t/5)
    high = np.maximum(open_, close) + 1.5
    low = np.minimum(open_, close) - 1.5
    volume = 100000 + 1000*(t % 20)
    return pd.DataFrame({'date':dates,'open':open_,'high':high,'low':low,'close':close,'volume':volume})


def test_stock_chart_sanitizes_bad_wicks(monkeypatch):
    df = synthetic_history(520)
    df.loc[100, 'low'] = 0
    df.loc[101, 'high'] = 999999
    monkeypatch.setattr(app, 'get_full_history_cached', lambda symbol: df.copy())
    c = app.app.test_client()
    r = c.get('/api/stock/TEST/chart?timeframe=1Y')
    assert r.status_code == 200
    body = r.get_json()
    assert body['available'] is True
    assert body['candles']
    for x in body['candles']:
        assert x['low'] > 0
        assert x['high'] >= max(x['open'], x['close'])
        assert x['low'] <= min(x['open'], x['close'])


def test_stock_detail_does_not_fail_when_intraday_provider_errors(monkeypatch):
    monkeypatch.setattr(app, 'get_quote', lambda symbol: {'symbol':symbol.upper(), 'price':100})
    monkeypatch.setattr(app, 'get_intraday', lambda symbol: (_ for _ in ()).throw(ValueError('The string did not match the expected pattern.')))
    c = app.app.test_client()
    r = c.get('/api/stock/TEST')
    assert r.status_code == 200
    body = r.get_json()
    assert body['symbol'] == 'TEST'
    assert body['series'] == []


def test_symbols_endpoint_never_returns_ten_symbol_development_fallback(monkeypatch):
    monkeypatch.setattr(app, 'fetch_psx_symbols', lambda force=False: (_ for _ in ()).throw(RuntimeError('upstream unavailable')))
    with app._symbol_lock:
        app._symbol_cache['items'] = []
        app._symbol_cache['time'] = None
    c = app.app.test_client()
    r = c.get('/api/symbols')
    assert r.status_code == 503
    body = r.get_json()
    assert body['count'] == 0
    assert body['symbols'] == []


def test_full_scan_uses_complete_universe_and_personalized_columns(monkeypatch):
    df = synthetic_history(520)
    symbols = [{'symbol': f'S{i:03d}', 'company': f'Company {i}', 'sector': 'Test'} for i in range(120)]
    monkeypatch.setattr(app, 'fetch_psx_symbols', lambda force=False: symbols)
    monkeypatch.setattr(app, 'get_divergence_history_cached', lambda symbol: df.copy())
    result = app.run_psx_divergence_scan()
    assert result['universe_count'] == 120
    assert result['symbols_scanned'] == 120
    assert 'personalized_matches' in result
    assert 'div_1d' in result['personalized_matches'][0] if result['personalized_matches'] else True


def test_heikin_ashi_is_recursive_not_body_only():
    df = pd.DataFrame({
        'date': pd.bdate_range('2026-01-01', periods=3),
        'open':[10,20,30], 'high':[22,32,42], 'low':[8,18,28], 'close':[20,30,40], 'volume':[1,1,1]
    })
    ha = app._latest_heikin_ashi(df)
    # First HA open = (10+20)/2 = 15; first HA close = 15.
    # Second HA open = (15+15)/2 = 15; second close = 25.
    # Third HA open = (15+25)/2 = 20; third close = 35.
    assert round(ha['open'], 6) == 20
    assert round(ha['close'], 6) == 35
    assert ha['color'] == 'green'
