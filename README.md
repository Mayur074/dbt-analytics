# 🏗️ dbt Data Warehouse with Analytics Layer

A production-grade **analytics engineering project** using dbt and DuckDB implementing a full **Medallion architecture** (Staging → Intermediate → Marts) for e-commerce analytics, with data quality tests, documentation, and a Streamlit BI dashboard.

![dbt](https://img.shields.io/badge/dbt-1.8-orange)
![DuckDB](https://img.shields.io/badge/DuckDB-1.0-yellow)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38-red)
![CI](https://github.com/Mayur074/dbt-analytics/actions/workflows/ci.yml/badge.svg)

---

## Architecture

```
Raw Sources (DuckDB)
raw_orders / raw_customers / raw_products
        │
        ▼ Staging Layer (views)
stg_orders      stg_customers      stg_products
Type casting · Null filtering · Field renaming · Deduplication
        │
        ▼ Intermediate Layer (views)
int_customer_orders
Joins · Derived fields · Date parts · Completion flags
        │
        ▼ Marts Layer (tables — optimized for BI)
mart_customer_ltv          mart_revenue_analytics
RFM segmentation           Monthly revenue trends
Cohort metrics             MoM growth · Channel perf
        │
        ▼ Streamlit Dashboard
Revenue trends · LTV segments · Channel share · Top customers
```

## dbt Tests

| Test Type | Models Covered |
|-----------|---------------|
| `unique` | order_id, customer_id, email, product_id |
| `not_null` | All primary keys and critical metrics |
| `accepted_values` | order_status, customer_segment, ltv_segment |

## Quickstart

```bash
git clone https://github.com/Mayur074/dbt-analytics.git
cd dbt-analytics
pip install -r requirements.txt

# Generate data, load DuckDB, run dbt pipeline
python scripts/setup_and_run.py

# Launch BI dashboard
streamlit run dashboard/app.py

# Run dbt commands manually
cd dbt_project
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

## Project Structure

```
dbt-analytics/
├── dbt_project/
│   ├── models/
│   │   ├── staging/          # stg_orders, stg_customers, stg_products
│   │   ├── intermediate/     # int_customer_orders
│   │   ├── marts/            # mart_customer_ltv, mart_revenue_analytics
│   │   └── schema.yml        # Column tests: unique, not_null, accepted_values
│   ├── dbt_project.yml
│   └── profiles.yml
├── scripts/
│   └── setup_and_run.py      # Data generation + full pipeline runner
├── dashboard/
│   └── app.py                # Streamlit BI dashboard
├── tests/
│   └── test_dbt_analytics.py # 26 unit tests for SQL and config
└── requirements.txt
```

## Author

**Mayur Sangle** — M.S. Data Science, University of Maryland
[LinkedIn](https://linkedin.com/in/mayur-sangle-04m) • [GitHub](https://github.com/Mayur074)
