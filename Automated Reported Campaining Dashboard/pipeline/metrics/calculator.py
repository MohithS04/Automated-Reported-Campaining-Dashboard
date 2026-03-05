"""
Metrics Calculator — computes department-specific KPIs and stores in campaign_metrics table.

Annual Giving:  open_rate, ctr, conversion_rate, avg_gift, cost_per_dollar_raised, ROI
Alumni Relations: rsvp_rate, attendance_rate, cost_per_attendee, satisfaction_avg, donation_per_attendee
Major Gifts: meetings_per_touch, proposal_rate, close_rate, avg_gift_size, cultivation_efficiency
"""

from datetime import datetime

import pandas as pd

from pipeline.database.db_utils import get_connection


def _insert_metric(conn, record_id: str, department: str, name: str, value: float, ts: str):
    """Insert a single metric row."""
    conn.execute(
        """
        INSERT INTO campaign_metrics (record_id, department, metric_name, metric_value, computed_ts)
        VALUES (?, ?, ?, ?, ?)
        """,
        (record_id, department, name, round(value, 4), ts),
    )


def compute_annual_giving(conn, ts: str):
    """Compute KPIs for Annual Giving campaigns."""
    df = pd.read_sql("SELECT * FROM annual_giving_campaigns", conn)

    for _, row in df.iterrows():
        rid = row["campaign_id"]
        dept = "Annual Giving"

        # Open rate
        open_rate = row["emails_opened"] / max(row["emails_delivered"], 1)
        _insert_metric(conn, rid, dept, "open_rate", open_rate, ts)

        # Click-through rate
        ctr = row["links_clicked"] / max(row["emails_opened"], 1)
        _insert_metric(conn, rid, dept, "ctr", ctr, ts)

        # Conversion rate (gifts / records_sent)
        conversion = row["gifts_received"] / max(row["records_sent"], 1)
        _insert_metric(conn, rid, dept, "conversion_rate", conversion, ts)

        # Average gift
        avg_gift = row["total_raised"] / max(row["gifts_received"], 1)
        _insert_metric(conn, rid, dept, "avg_gift", avg_gift, ts)

        # Cost per dollar raised
        cpdr = row["campaign_cost"] / max(row["total_raised"], 1)
        _insert_metric(conn, rid, dept, "cost_per_dollar_raised", cpdr, ts)

        # ROI
        roi = (row["total_raised"] - row["campaign_cost"]) / max(row["campaign_cost"], 1)
        _insert_metric(conn, rid, dept, "roi", roi, ts)

    print(f"  ✅  Annual Giving: {len(df)} campaigns × 6 metrics = {len(df) * 6} rows")
    return len(df) * 6


def compute_alumni_relations(conn, ts: str):
    """Compute KPIs for Alumni Relations events."""
    df = pd.read_sql("SELECT * FROM alumni_relations_events", conn)

    for _, row in df.iterrows():
        rid = row["event_id"]
        dept = "Alumni Relations"

        # RSVP rate
        rsvp_rate = row["rsvps_received"] / max(row["invitations_sent"], 1)
        _insert_metric(conn, rid, dept, "rsvp_rate", rsvp_rate, ts)

        # Attendance rate
        att_rate = row["attendees"] / max(row["rsvps_received"], 1)
        _insert_metric(conn, rid, dept, "attendance_rate", att_rate, ts)

        # Donation per attendee
        dpa = row["donations_collected"] / max(row["attendees"], 1)
        _insert_metric(conn, rid, dept, "donation_per_attendee", dpa, ts)

        # Satisfaction avg (single row, just store it)
        _insert_metric(conn, rid, dept, "satisfaction_avg", row["satisfaction_score"], ts)

        # New contacts per event
        _insert_metric(conn, rid, dept, "new_contacts_per_event", row["new_contacts"], ts)

    print(f"  ✅  Alumni Relations: {len(df)} events × 5 metrics = {len(df) * 5} rows")
    return len(df) * 5


def compute_major_gifts(conn, ts: str):
    """Compute KPIs for Major Gifts outreach."""
    df = pd.read_sql("SELECT * FROM major_gifts_outreach", conn)

    for _, row in df.iterrows():
        rid = row["prospect_id"]
        dept = "Major Gifts"

        # Meetings per touch
        mpt = row["meetings_held"] / max(row["total_touches"], 1)
        _insert_metric(conn, rid, dept, "meetings_per_touch", mpt, ts)

        # Proposal rate
        prop_rate = row["proposals_sent"] / max(row["meetings_held"], 1)
        _insert_metric(conn, rid, dept, "proposal_rate", prop_rate, ts)

        # Close rate (gift_committed > 0 if proposals > 0)
        close = 1.0 if (row["proposals_sent"] > 0 and row["gift_committed"] > 0) else 0.0
        _insert_metric(conn, rid, dept, "close_rate", close, ts)

        # Average gift size
        _insert_metric(conn, rid, dept, "avg_gift_size", row["gift_committed"], ts)

        # Cultivation efficiency (gift / cultivation_days)
        eff = row["gift_committed"] / max(row["cultivation_days"], 1)
        _insert_metric(conn, rid, dept, "cultivation_efficiency", eff, ts)

    print(f"  ✅  Major Gifts: {len(df)} prospects × 5 metrics = {len(df) * 5} rows")
    return len(df) * 5


def compute_all_metrics():
    """Compute metrics for all departments."""
    conn = get_connection()
    ts = datetime.now().isoformat()

    # Clear old metrics
    conn.execute("DELETE FROM campaign_metrics")

    print("\n📊  Computing Campaign Metrics")
    print("-" * 60)

    total = 0
    total += compute_annual_giving(conn, ts)
    total += compute_alumni_relations(conn, ts)
    total += compute_major_gifts(conn, ts)

    conn.commit()
    conn.close()

    print("-" * 60)
    print(f"  Total: {total} metric rows computed")
    print("✅  Metrics stored in campaign_metrics table\n")

    return total


if __name__ == "__main__":
    compute_all_metrics()
