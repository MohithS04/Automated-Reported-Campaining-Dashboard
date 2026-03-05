"""
Database Schema — creates all tables for the campaign reporting pipeline.

Tables:
  - annual_giving_campaigns   (raw data)
  - alumni_relations_events   (raw data)
  - major_gifts_outreach      (raw data)
  - validation_log            (validation results)
  - campaign_metrics          (computed KPIs)
"""

from pipeline.database.db_utils import get_connection


def create_tables():
    """Create all tables in the SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Annual Giving Campaigns ──────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS annual_giving_campaigns (
            campaign_id       TEXT PRIMARY KEY,
            campaign_name     TEXT NOT NULL,
            department        TEXT NOT NULL,
            launch_date       TEXT NOT NULL,
            end_date          TEXT NOT NULL,
            segment_name      TEXT NOT NULL,
            records_sent      INTEGER NOT NULL,
            emails_delivered  INTEGER NOT NULL,
            emails_opened     INTEGER NOT NULL,
            links_clicked     INTEGER NOT NULL,
            gifts_received    INTEGER NOT NULL,
            total_raised      REAL NOT NULL,
            campaign_cost     REAL NOT NULL
        )
    """)

    # ── Alumni Relations Events ──────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumni_relations_events (
            event_id            TEXT PRIMARY KEY,
            event_name          TEXT NOT NULL,
            department          TEXT NOT NULL,
            event_type          TEXT NOT NULL,
            event_date          TEXT NOT NULL,
            invitations_sent    INTEGER NOT NULL,
            rsvps_received      INTEGER NOT NULL,
            attendees           INTEGER NOT NULL,
            donations_collected REAL NOT NULL,
            new_contacts        INTEGER NOT NULL,
            follow_ups_sent     INTEGER NOT NULL,
            satisfaction_score  REAL NOT NULL
        )
    """)

    # ── Major Gifts Outreach ─────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS major_gifts_outreach (
            prospect_id       TEXT PRIMARY KEY,
            prospect_name     TEXT NOT NULL,
            department        TEXT NOT NULL,
            gift_officer      TEXT NOT NULL,
            outreach_date     TEXT NOT NULL,
            total_touches     INTEGER NOT NULL,
            meetings_held     INTEGER NOT NULL,
            proposals_sent    INTEGER NOT NULL,
            proposal_amount   REAL NOT NULL,
            gift_committed    REAL NOT NULL,
            commitment_date   TEXT,
            cultivation_days  INTEGER NOT NULL
        )
    """)

    # ── Validation Log ───────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validation_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name   TEXT NOT NULL,
            table_name  TEXT NOT NULL,
            status      TEXT NOT NULL,
            fail_count  INTEGER NOT NULL DEFAULT 0,
            details     TEXT,
            run_ts      TEXT NOT NULL
        )
    """)

    # ── Campaign Metrics ─────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaign_metrics (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id       TEXT NOT NULL,
            department      TEXT NOT NULL,
            metric_name     TEXT NOT NULL,
            metric_value    REAL NOT NULL,
            computed_ts     TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("✅  Database schema created (5 tables)")


if __name__ == "__main__":
    create_tables()
