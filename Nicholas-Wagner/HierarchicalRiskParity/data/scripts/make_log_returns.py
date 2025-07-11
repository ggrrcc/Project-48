#!/usr/bin/env python3
"""
Create one-period **log returns** from minute bars *or* daily VWMP files.

Examples
    # minute-by-minute
    python make_log_returns.py raw mbmlr Close
    # daily VWMP
    python make_log_returns.py dlyvolwtd dlyvolwtdlr VWMP
"""

import sys, pathlib, numpy as np
import pandas as pd

def logret(series: pd.Series) -> pd.Series:
    return np.log(series / series.shift(1)).dropna()

def process_file(csv_in: pathlib.Path,
                 csv_out: pathlib.Path,
                 price_col: str):
    df = pd.read_csv(csv_in, parse_dates=["Date"])
    lr = logret(df[price_col]).to_frame(name="LogRet")
    # drop the first row lost to shift
    lr.insert(0, "Timestamp", df.loc[lr.index, "Date"].values)
    lr.to_csv(csv_out, index=False)
    print(f"[✓] {csv_in.name} → {csv_out}")

def main(src: str, dst: str, price_col: str):
    src, dst = pathlib.Path(src), pathlib.Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for csv in src.glob("*.csv"):
        process_file(csv, dst / csv.name, price_col)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: make_log_returns.py <src_dir> <dst_dir> <price_column>")
    main(*sys.argv[1:])

