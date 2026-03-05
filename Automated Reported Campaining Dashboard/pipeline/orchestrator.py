"""
Pipeline Orchestrator — runs the full end-to-end pipeline.

Sequence: create_schema → load_data → validate → compute_metrics
"""

from pipeline.database.schema import create_tables
from pipeline.database.loader import load_all
from pipeline.validation.validator import run_validations
from pipeline.metrics.calculator import compute_all_metrics


def run_pipeline():
    """Execute the complete campaign reporting pipeline."""
    print("=" * 60)
    print("  🚀  Automated Campaign Reporting Pipeline")
    print("=" * 60)

    # Step 1: Create database schema
    print("\n[1/4] Creating database schema...")
    create_tables()

    # Step 2: Load CSV data into SQLite
    print("\n[2/4] Loading CSV data into SQLite...")
    load_all()

    # Step 3: Run validation checks
    print("\n[3/4] Running validation checks...")
    validation_results = run_validations()

    # Step 4: Compute metrics
    print("\n[4/4] Computing campaign metrics...")
    metrics_count = compute_all_metrics()

    # Summary
    print("=" * 60)
    print("  ✅  Pipeline Complete!")
    print(f"  • Validation: {validation_results['passed']}/{validation_results['total']} checks passed")
    print(f"  • Metrics: {metrics_count} metric rows computed")
    print("=" * 60)

    return {
        "validation": validation_results,
        "metrics_count": metrics_count,
    }


if __name__ == "__main__":
    run_pipeline()
