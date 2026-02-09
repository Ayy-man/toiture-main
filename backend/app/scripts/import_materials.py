"""Import Laurent's materials CSV to Supabase materials table.

Usage:
    python -m app.scripts.import_materials [--csv-path PATH] [--dry-run]

Environment variables required:
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from dotenv import load_dotenv
from supabase import Client, create_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Column mapping from CSV to database
COLUMN_MAPPING = {
    "NAME": "name",
    "COST": "cost",
    "SELL": "sell_price",
    "UNIT": "unit",
    "CATEGORY": "category",
    "SUPPLIER": "supplier",
    "CODE": "code",
    "NOTE": "note",
    "S en pi2": "area_sqft",
    "Long en pi": "length_ft",
    "Larg en pi": "width_ft",
    "Ep en pi": "thickness_ft",
}

# Categories that indicate labor items
LABOR_CATEGORIES = ["Main d'oeuvre", "Sous-traitant pose"]


def clean_currency(value: Any) -> Optional[float]:
    """Convert currency string to float."""
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    # Remove $ and comma, convert to float
    cleaned = str(value).replace("$", "").replace(",", "").strip()
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def is_complete_material(row: pd.Series) -> bool:
    """Check if material has all required fields.

    Uses original CSV column names (before rename).
    """
    required = ["NAME", "COST", "SELL", "UNIT", "CATEGORY"]
    return all(pd.notna(row.get(col)) and str(row.get(col)).strip() != "" for col in required)


def process_csv(csv_path: Path) -> tuple[list[dict], dict[str, int]]:
    """Load and clean CSV data.

    Returns:
        tuple: (cleaned_rows, stats_dict)
    """
    logger.info(f"Reading CSV from: {csv_path}")

    # Read CSV with UTF-8 BOM handling
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    logger.info(f"Loaded {len(df)} rows")

    # Strip whitespace from all string columns
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.strip()

    # Clean price columns
    df["COST"] = df["COST"].apply(clean_currency)
    df["SELL"] = df["SELL"].apply(clean_currency)

    # Clean dimension columns
    for col in ["S en pi2", "Long en pi", "Larg en pi", "Ep en pi"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Detect labor items
    df["item_type"] = df["CATEGORY"].apply(
        lambda x: "labor" if str(x).strip() in LABOR_CATEGORIES else "material"
    )

    # Detect duplicates (keep first occurrence)
    df["is_duplicate"] = df.duplicated(subset=["NAME"], keep="first")

    # Classify completeness and set review status
    df["is_complete"] = df.apply(is_complete_material, axis=1)

    def get_review_status(row):
        if row["is_duplicate"]:
            return "duplicate"
        if row["item_type"] == "labor":
            return "flagged"
        if not row["is_complete"]:
            return "flagged"
        return "approved"

    df["review_status"] = df.apply(get_review_status, axis=1)

    # Rename columns according to mapping
    rename_map = {k: v for k, v in COLUMN_MAPPING.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    # Select columns for database
    db_columns = list(COLUMN_MAPPING.values()) + ["item_type", "review_status"]
    df_export = df[[col for col in db_columns if col in df.columns]]

    # Convert to list of dicts
    rows = df_export.to_dict(orient="records")

    # Calculate stats
    stats = {
        "total": len(df),
        "approved": len(df[df["review_status"] == "approved"]),
        "flagged": len(df[df["review_status"] == "flagged"]),
        "duplicate": len(df[df["review_status"] == "duplicate"]),
        "labor": len(df[df["item_type"] == "labor"]),
    }

    return rows, stats


def check_table_exists(client: Client) -> bool:
    """Check if materials table exists in Supabase."""
    try:
        response = client.from_("materials").select("id").limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"Materials table does not exist or is not accessible: {e}")
        return False


def batch_insert(client: Client, rows: list[dict], batch_size: int = 500) -> None:
    """Insert rows in batches to Supabase."""
    total = len(rows)
    for i in range(0, total, batch_size):
        batch = rows[i : i + batch_size]
        logger.info(f"Inserting batch {i // batch_size + 1} ({len(batch)} rows)")
        response = client.from_("materials").insert(batch).execute()
        logger.debug(f"Batch response: {response}")
    logger.info(f"Successfully inserted {total} rows")


def main() -> None:
    """Main import script."""
    parser = argparse.ArgumentParser(description="Import materials CSV to Supabase")
    parser.add_argument(
        "--csv-path",
        type=Path,
        default=Path(__file__).parent.parent.parent.parent / "cortex-data" / "LV Material List.csv",
        help="Path to CSV file (default: ../../cortex-data/LV Material List.csv)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print stats without inserting to database",
    )
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Validate CSV path
    if not args.csv_path.exists():
        logger.error(f"CSV file not found: {args.csv_path}")
        sys.exit(1)

    # Process CSV
    try:
        rows, stats = process_csv(args.csv_path)
    except Exception as e:
        logger.error(f"Failed to process CSV: {e}", exc_info=True)
        sys.exit(1)

    # Print summary stats
    logger.info("=" * 60)
    logger.info("IMPORT SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total rows parsed:       {stats['total']}")
    logger.info(f"Approved (clean):        {stats['approved']}")
    logger.info(f"Flagged (incomplete):    {stats['flagged']}")
    logger.info(f"Duplicates detected:     {stats['duplicate']}")
    logger.info(f"Labor items:             {stats['labor']}")
    logger.info("=" * 60)

    if args.dry_run:
        logger.info("DRY RUN MODE - No database operations performed")
        return

    # Check Supabase credentials
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        logger.error(
            "ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set.\n"
            "Please configure these environment variables and try again."
        )
        sys.exit(1)

    # Connect to Supabase
    logger.info("Connecting to Supabase...")
    client = create_client(supabase_url, supabase_key)

    # Check if table exists
    if not check_table_exists(client):
        logger.error(
            "\nERROR: materials table does not exist.\n\n"
            "Please run create_materials_table.sql in Supabase Dashboard first:\n"
            "1. Go to Supabase Dashboard > SQL Editor\n"
            "2. Open backend/app/scripts/create_materials_table.sql\n"
            "3. Copy and paste the SQL\n"
            "4. Click 'Run'\n"
            "5. Re-run this import script\n"
        )
        sys.exit(1)

    # Insert data
    try:
        batch_insert(client, rows)
        logger.info("Import completed successfully!")
    except Exception as e:
        logger.error(f"Failed to insert data: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
