"""
tests/test_dbt_analytics.py
-----------------------------
Unit tests for dbt model logic and pipeline configuration.
Self-contained — no dbt, DuckDB, or pandas needed in CI.
"""

import os
import pytest
from pathlib import Path


# ── SQL model file existence ──────────────────────────────────────────────────

BASE = Path(__file__).parent.parent / "dbt_project" / "models"

def test_staging_orders_exists():
    assert (BASE / "staging" / "stg_orders.sql").exists()

def test_staging_customers_exists():
    assert (BASE / "staging" / "stg_customers.sql").exists()

def test_staging_products_exists():
    assert (BASE / "staging" / "stg_products.sql").exists()

def test_intermediate_customer_orders_exists():
    assert (BASE / "intermediate" / "int_customer_orders.sql").exists()

def test_mart_customer_ltv_exists():
    assert (BASE / "marts" / "mart_customer_ltv.sql").exists()

def test_mart_revenue_analytics_exists():
    assert (BASE / "marts" / "mart_revenue_analytics.sql").exists()

def test_schema_yml_exists():
    assert (BASE / "schema.yml").exists()


# ── dbt project config ────────────────────────────────────────────────────────

def test_dbt_project_yml_exists():
    path = Path(__file__).parent.parent / "dbt_project" / "dbt_project.yml"
    assert path.exists()

def test_profiles_yml_exists():
    path = Path(__file__).parent.parent / "dbt_project" / "profiles.yml"
    assert path.exists()

def test_dbt_project_yml_has_name():
    path = Path(__file__).parent.parent / "dbt_project" / "dbt_project.yml"
    content = path.read_text()
    assert "ecommerce_analytics" in content

def test_dbt_project_yml_has_models_config():
    path = Path(__file__).parent.parent / "dbt_project" / "dbt_project.yml"
    content = path.read_text()
    assert "models:" in content
    assert "marts:" in content
    assert "staging:" in content


# ── SQL content validation ────────────────────────────────────────────────────

def test_stg_orders_has_null_filter():
    sql = (BASE / "staging" / "stg_orders.sql").read_text()
    assert "is not null" in sql.lower()

def test_stg_orders_references_raw_orders():
    sql = (BASE / "staging" / "stg_orders.sql").read_text()
    assert "raw_orders" in sql

def test_stg_customers_has_email_validation():
    sql = (BASE / "staging" / "stg_customers.sql").read_text()
    assert "email" in sql.lower()

def test_mart_ltv_has_rfm_segments():
    sql = (BASE / "marts" / "mart_customer_ltv.sql").read_text()
    assert "CHAMPION" in sql
    assert "LOYAL" in sql
    assert "AT_RISK" in sql

def test_mart_revenue_has_window_function():
    sql = (BASE / "marts" / "mart_revenue_analytics.sql").read_text()
    assert "over (" in sql.lower()

def test_intermediate_uses_ref():
    sql = (BASE / "intermediate" / "int_customer_orders.sql").read_text()
    assert "{{ ref(" in sql

def test_schema_yml_has_unique_tests():
    schema = (BASE / "schema.yml").read_text()
    assert "unique" in schema

def test_schema_yml_has_not_null_tests():
    schema = (BASE / "schema.yml").read_text()
    assert "not_null" in schema

def test_schema_yml_has_accepted_values():
    schema = (BASE / "schema.yml").read_text()
    assert "accepted_values" in schema


# ── Layered architecture validation ──────────────────────────────────────────

def test_staging_layer_has_three_models():
    staging = list((BASE / "staging").glob("*.sql"))
    assert len(staging) >= 3

def test_marts_layer_has_two_models():
    marts = list((BASE / "marts").glob("*.sql"))
    assert len(marts) >= 2

def test_intermediate_layer_exists():
    intermediate = list((BASE / "intermediate").glob("*.sql"))
    assert len(intermediate) >= 1


# ── Supporting files ──────────────────────────────────────────────────────────

def test_setup_script_exists():
    path = Path(__file__).parent.parent / "scripts" / "setup_and_run.py"
    assert path.exists()

def test_dashboard_app_exists():
    path = Path(__file__).parent.parent / "dashboard" / "app.py"
    assert path.exists()

def test_requirements_exists():
    path = Path(__file__).parent.parent / "requirements.txt"
    assert path.exists()
