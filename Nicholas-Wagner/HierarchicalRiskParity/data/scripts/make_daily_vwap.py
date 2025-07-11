#!/usr/bin/env python3
"""
Compute **Daily Volume-Weighted Mid-Point Price** (VWMP)
  midpoint  = (High + Low) / 2
  daily_VWMP = Σ(midpoint · Volume) / Σ(Volume)

Usage:
    python make_daily_vwap.py raw dlyvolwtd
"""

import sys, pathlib
import pandas as pd

def daily_vwmp(df: pd.DataFrame) -> pd.DataFrame:
    df["Mid"] = (df["High"] + df["Low"]) / 2
    df["DollarVol"] = df["Mid"] * df["Volume"]
    out = (df
           .groupby("Date", as_index=False)
           .agg({"DollarVol": "sum", "Volume": "sum"}))
    out["VWMP"] = out["DollarVol"] / out["Volume"]
    return out[["Date", "VWMP"]]

def main(src: str, dst: str):
    src, dst = pathlib.Path(src), pathlib.Path(dst)
    dst.mkdir(parents=True, exist_ok=True)

    for csv in src.glob("*.csv"):
        df = pd.read_csv(csv,
                         parse_dates=["Date"],
                         dtype={"High": float, "Low": float, "Volume": float})
        out = daily_vwmp(df)
        out.to_csv(dst / csv.name, index=False)
        print(f"[✓] {csv.name} → {dst/csv.name}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: make_daily_vwap.py <src_dir> <dst_dir>")
    main(*sys.argv[1:])

