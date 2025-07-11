#!/usr/bin/env python3
"""
Read per-ticker CSVs (Timestamp, LogRet) and append them to a long table
in PostgreSQL:  Ticker | Timestamp | LogRet

Usage:
  python ingest_returns_long_pg.py mbmlr \
         postgresql+psycopg2://mdtuser:Str0ngPwd!@localhost/mdt \
         log_returns
"""

import sys, pathlib, pandas as pd
from sqlalchemy import create_engine, text

CHUNK = 100_000

DDL = """
CREATE TABLE IF NOT EXISTS {tbl} (
    Ticker     VARCHAR(16)   NOT NULL,
    Timestamp  TIMESTAMP     NOT NULL,
    LogRet     DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (Ticker, Timestamp)
);
CREATE INDEX IF NOT EXISTS ix_ts_{tbl} ON {tbl} (Timestamp);
"""

def csv_to_long(csv_path: pathlib.Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["Timestamp"])
    df.insert(0, "Ticker", csv_path.stem.upper())
    return df

def main(src_dir: str, conn_uri: str, table: str):
    eng = create_engine(conn_uri, future=True)
    with eng.begin() as con:
        con.exec_driver_sql(DDL.format(tbl=table))

    for csv in pathlib.Path(src_dir).glob("*.csv"):
        df = csv_to_long(csv)
        df.to_sql(table, eng, if_exists="append",
                  index=False, chunksize=CHUNK, method="multi")
        print(f"[✓] {csv.name}: {len(df):,} rows")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: ingest_returns_long_pg.py <src_dir> <conn_uri> <table>")
    main(*sys.argv[1:])

