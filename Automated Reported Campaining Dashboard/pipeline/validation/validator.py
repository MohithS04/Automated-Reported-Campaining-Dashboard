"""
Validation Engine — runs all validation rules and logs results to SQLite.
"""

from datetime import datetime

import pandas as pd

from pipeline.database.db_utils import get_connection
from pipeline.validation.rules import ALL_RULES


def run_validations():
    """Execute all validation rules and log results to the validation_log table."""
    conn = get_connection()
    now = datetime.now().isoformat()

    total_pass = 0
    total_fail = 0

    print("\n📋  Running Validation Checks")
    print("-" * 60)

    for rule in ALL_RULES:
        table = rule["table"]
        name = rule["name"]

        # Load the table into a DataFrame
        try:
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
        except Exception as e:
            print(f"  ❌  {name}: Could not read table {table} — {e}")
            continue

        # Run the check
        passed, failed, details = rule["check_fn"](df)
        status = "PASS" if failed == 0 else "FAIL"
        icon = "✅" if status == "PASS" else "⚠️"

        total_pass += (1 if status == "PASS" else 0)
        total_fail += (1 if status == "FAIL" else 0)

        print(f"  {icon}  {name}: {status} (fails: {failed}) — {details}")

        # Log to database
        conn.execute(
            """
            INSERT INTO validation_log (rule_name, table_name, status, fail_count, details, run_ts)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, table, status, failed, details, now),
        )

    conn.commit()
    conn.close()

    print("-" * 60)
    print(f"  Total: {total_pass} passed, {total_fail} failed out of {total_pass + total_fail} checks")
    print("✅  Validation results logged to database\n")

    return {"passed": total_pass, "failed": total_fail, "total": total_pass + total_fail}


if __name__ == "__main__":
    run_validations()
