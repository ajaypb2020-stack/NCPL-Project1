"""
Create tables in SQL Server database retail_db and import all bm_*.csv files.

Defaults target local named instance: SWARNAAARNA\\SQLEXPRESS using Windows auth.

Usage:
  1) pip install pandas sqlalchemy pyodbc
  2) python load_to_sqlserver.py

Optional environment variables:
    SQLSERVER_HOST=SWARNAAARNA\\SQLEXPRESS
  SQLSERVER_DATABASE=retail_db
  SQLSERVER_DRIVER=ODBC Driver 17 for SQL Server
  SQLSERVER_TRUSTED_CONNECTION=yes
"""

import glob
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


SQLSERVER_HOST = os.getenv("SQLSERVER_HOST", r"SWARNAAARNA\SQLEXPRESS")
SQLSERVER_DATABASE = os.getenv("SQLSERVER_DATABASE", "retail_db")
SQLSERVER_DRIVER = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server")
SQLSERVER_TRUSTED_CONNECTION = os.getenv("SQLSERVER_TRUSTED_CONNECTION", "yes")

CSV_DIR = Path(__file__).parent
CSV_PATTERN = "bm_*.csv"
CHUNK_SIZE = 5000


def get_engine(database: str):
    url = URL.create(
        "mssql+pyodbc",
        host=SQLSERVER_HOST,
        database=database,
        query={
            "driver": SQLSERVER_DRIVER,
            "trusted_connection": SQLSERVER_TRUSTED_CONNECTION,
            "TrustServerCertificate": "yes",
        },
    )
    return create_engine(url, fast_executemany=True)


def ensure_database_exists():
    engine = get_engine("master")
    safe_db = SQLSERVER_DATABASE.replace("'", "''").replace("]", "]]")
    create_db_sql = (
        "IF DB_ID(N'" + safe_db + "') IS NULL "
        "BEGIN EXEC('CREATE DATABASE [" + safe_db + "]') END"
    )
    with engine.execution_options(isolation_level='AUTOCOMMIT').connect() as conn:
        conn.exec_driver_sql(create_db_sql)
    engine.dispose()


def normalize_types(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        lower = col.lower()
        if lower.endswith("_id") or lower in {"cust_id", "customer_id", "store_id", "sku_id", "promo_id"}:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df


def load_csv_files():
    files = sorted(glob.glob(str(CSV_DIR / CSV_PATTERN)))
    if not files:
        print(f"No files matching {CSV_PATTERN} found in {CSV_DIR}")
        return

    engine = get_engine(SQLSERVER_DATABASE)

    for csv_path in files:
        table_name = Path(csv_path).stem
        print(f"Loading {Path(csv_path).name} into {table_name} ...")

        headers = pd.read_csv(csv_path, nrows=0)
        date_cols = [c for c in headers.columns if "date" in c.lower()]

        first_chunk = True
        total_rows = 0
        for chunk in pd.read_csv(csv_path, parse_dates=date_cols or None, chunksize=CHUNK_SIZE):
            chunk = normalize_types(chunk)
            chunk.to_sql(
                table_name,
                con=engine,
                if_exists="replace" if first_chunk else "append",
                index=False,
            )
            first_chunk = False
            total_rows += len(chunk)

        print(f"  Imported {total_rows} rows")

    engine.dispose()


if __name__ == "__main__":
    ensure_database_exists()
    load_csv_files()
    print("Done")