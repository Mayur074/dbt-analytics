"""
scripts/setup_and_run.py
-------------------------
Generates synthetic e-commerce data, loads it into DuckDB,
seeds the dbt raw tables, and runs the full dbt pipeline.
"""

from __future__ import annotations
import os
import logging
import subprocess
from pathlib import Path
from datetime import date, timedelta
import random

import duckdb
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RANDOM_STATE = 42
random.seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)

DB_PATH      = "data/ecommerce.duckdb"
N_CUSTOMERS  = 2_000
N_PRODUCTS   = 150
N_ORDERS     = 20_000


# ── Data generation ───────────────────────────────────────────────────────────

def generate_customers(n: int) -> pd.DataFrame:
    countries  = ["US", "UK", "DE", "FR", "CA", "AU", "JP", "IN"]
    segments   = ["STANDARD", "PREMIUM", "VIP", "ENTERPRISE"]
    seg_weights= [0.60, 0.25, 0.10, 0.05]

    start = date(2020, 1, 1)
    end   = date(2024, 12, 31)
    delta = (end - start).days

    return pd.DataFrame({
        "customer_id":      [f"C{i:05d}" for i in range(1, n+1)],
        "first_name":       [f"FirstName{i}" for i in range(1, n+1)],
        "last_name":        [f"LastName{i}"  for i in range(1, n+1)],
        "email":            [f"user{i}@example.com" for i in range(1, n+1)],
        "country":          np.random.choice(countries, n),
        "segment":          np.random.choice(segments, n, p=seg_weights),
        "signup_date":      [str(start + timedelta(days=random.randint(0, delta))) for _ in range(n)],
        "created_at":       pd.Timestamp.now().isoformat(),
    })


def generate_products(n: int) -> pd.DataFrame:
    categories = ["ELECTRONICS", "CLOTHING", "BOOKS", "HOME", "SPORTS", "BEAUTY"]
    return pd.DataFrame({
        "product_id":     [f"P{i:04d}" for i in range(1, n+1)],
        "product_name":   [f"Product {i}" for i in range(1, n+1)],
        "category":       np.random.choice(categories, n),
        "price":          np.round(np.random.lognormal(3.5, 1.0, n).clip(5, 2000), 2),
        "stock_quantity": np.random.randint(0, 500, n),
        "created_at":     pd.Timestamp.now().isoformat(),
    })


def generate_orders(n: int, customers: pd.DataFrame) -> pd.DataFrame:
    statuses  = ["COMPLETED", "PENDING", "CANCELLED", "DELIVERED", "REFUNDED"]
    s_weights = [0.55, 0.15, 0.10, 0.15, 0.05]
    channels  = ["WEB", "MOBILE", "EMAIL", "SOCIAL", "REFERRAL"]
    c_weights = [0.45, 0.30, 0.10, 0.10, 0.05]

    start = date(2021, 1, 1)
    end   = date(2024, 12, 31)
    delta = (end - start).days

    cust_ids = customers["customer_id"].values
    return pd.DataFrame({
        "order_id":    [f"O{i:07d}" for i in range(1, n+1)],
        "customer_id": np.random.choice(cust_ids, n),
        "order_date":  [str(start + timedelta(days=random.randint(0, delta))) for _ in range(n)],
        "status":      np.random.choice(statuses, n, p=s_weights),
        "amount":      np.round(np.random.lognormal(4.0, 1.2, n).clip(5, 5000), 2),
        "channel":     np.random.choice(channels, n, p=c_weights),
        "created_at":  pd.Timestamp.now().isoformat(),
    })


# ── Database setup ────────────────────────────────────────────────────────────

def setup_database():
    Path("data").mkdir(exist_ok=True)

    logger.info("Generating synthetic e-commerce data...")
    customers = generate_customers(N_CUSTOMERS)
    products  = generate_products(N_PRODUCTS)
    orders    = generate_orders(N_ORDERS, customers)

    logger.info(f"Customers: {len(customers):,} | Products: {len(products):,} | Orders: {len(orders):,}")

    conn = duckdb.connect(DB_PATH)

    for table, df in [
        ("raw_customers", customers),
        ("raw_products",  products),
        ("raw_orders",    orders),
    ]:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.execute(f"CREATE TABLE {table} AS SELECT * FROM df")
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        logger.info(f"Loaded {count:,} rows into {table}")

    conn.close()
    logger.info(f"Database ready at {DB_PATH}")


# ── dbt runner ────────────────────────────────────────────────────────────────

def run_dbt(command: str):
    cmd = f"cd dbt_project && dbt {command} --profiles-dir ."
    logger.info(f"Running: dbt {command}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(result.stderr)
    else:
        logger.info(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    return result.returncode == 0


if __name__ == "__main__":
    setup_database()
    run_dbt("deps")
    run_dbt("run")
    run_dbt("test")
    run_dbt("docs generate")
    logger.info("Pipeline complete. Run 'dbt docs serve' in dbt_project/ to view docs.")
