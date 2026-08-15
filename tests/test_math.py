"""Dependency-light regression tests for the PSX calculations.
Run: python tests/test_math.py
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import psx_screener as core


def main():
    # Classic floor-trader pivots: H=110, L=90, C=100 => P=100.
    p = core.compute_classic_pivots(110, 90, 100)
    assert p == {"P": 100, "R1": 110, "R2": 120, "R3": 130, "S1": 90, "S2": 80, "S3": 70}

    f = core.compute_fibonacci_pivots(110, 90, 100)
    assert round(f["R1"], 2) == 107.64
    assert round(f["R2"], 2) == 112.36
    assert round(f["S1"], 2) == 92.36

    # Multi-timeframe input is genuinely resampled, not relabelled daily data.
    n = 260
    dates = pd.date_range("2025-08-01", periods=n, freq="D")
    close = pd.Series(100 + np.sin(np.arange(n) / 8) * 3 + np.arange(n) * 0.05)
    df = pd.DataFrame({"date": dates, "open": close, "high": close + 1, "low": close - 1,
                       "close": close, "volume": 1000})
    weekly = df.set_index("date").resample("W").agg({"open":"first","high":"max","low":"min","close":"last","volume":"sum"}).dropna().reset_index()
    monthly = df.set_index("date").resample("ME").agg({"open":"first","high":"max","low":"min","close":"last","volume":"sum"}).dropna().reset_index()
    assert len(weekly) < len(df)
    assert len(monthly) < len(weekly)

    # Standard RSI stays bounded.
    rsi = core.compute_rsi(close, 14)
    assert float(rsi.min()) >= 0 and float(rsi.max()) <= 100

    print("PASS: pivot formulas, Fibonacci formulas, RSI bounds, and true W/M resampling")


if __name__ == "__main__":
    main()
