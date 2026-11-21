"""Central configuration for the Inventory Analytics project."""

from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DATA_DIR = DATA_DIR / "exports"

REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
EXCEL_DIR = BASE_DIR / "excel"
SQL_DIR = BASE_DIR / "sql"
POWERBI_DIR = BASE_DIR / "powerbi"
DASHBOARD_DIR = BASE_DIR / "dashboard"

# Ensure key directories exist
for _dir in (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    EXPORTS_DATA_DIR,
    FIGURES_DIR,
    EXCEL_DIR,
):
    _dir.mkdir(parents=True, exist_ok=True)

# Database configuration (PostgreSQL)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "inventory_analytics")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

def get_database_url() -> str:
    """Build SQLAlchemy PostgreSQL connection URL from environment variables."""
    if DB_PASSWORD:
        return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return f"postgresql+psycopg2://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Analytics & Simulation Parameters
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
DATA_START_DATE = os.getenv("DATA_START_DATE", "2024-11-01")
DATA_END_DATE = os.getenv("DATA_END_DATE", "2026-10-31")
ANALYSIS_DAYS = 730
SLOW_MOVING_DAYS = 90
DEAD_STOCK_DAYS = 180
OVERSTOCK_MULTIPLIER = 2.5
HOLDING_COST_RATE = 0.20  # 20% annual holding cost on inventory value
