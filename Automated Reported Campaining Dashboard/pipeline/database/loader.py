"""
Data Loader — reads CSVs from data/inputs/ and loads into SQLite tables.
"""

import os

import pandas as pd

from pipeline.database.db_utils import get_connection

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUT_DIR = os.path.join(PROJECT_ROOT, "data", "inputs")


FILE_TABLE_MAP = {
    "annual_giving_campaigns.csv": "annual_giving_campaigns",
    "alumni_relations_events.csv": "alumni_relations_events",
    "major_gifts_outreach.csv": "major_gifts_outreach",
}


def load_all():
    """Load all CSV files into their corresponding SQLite tables."""
    conn = get_connection()

    for filename, table_name in FILE_TABLE_MAP.items():
        filepath = os.path.join(INPUT_DIR, filename)
        if not os.path.exists(filepath):
            print(f"⚠️  Skipped {filename} — file not found")
            continue

        df = pd.read_csv(filepath)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"✅  Loaded {filename} → {table_name} ({len(df)} rows)")

    conn.close()
    print("✅  All data loaded into SQLite")


if __name__ == "__main__":
    load_all()
