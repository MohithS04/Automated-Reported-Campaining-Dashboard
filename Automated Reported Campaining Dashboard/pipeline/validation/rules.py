"""
Validation Rules — defines the 10 validation checks for the pipeline.

Each rule is a dict with:
  - name: human-readable name
  - table: which table to check
  - check_fn: function(df) -> (pass_count, fail_count, details)
"""

import pandas as pd


def _check_nulls(df: pd.DataFrame, required_cols: list[str]):
    """Check for null values in required columns."""
    fails = 0
    details = []
    for col in required_cols:
        if col in df.columns:
            n = df[col].isna().sum()
            if n > 0:
                fails += n
                details.append(f"{col}: {n} nulls")
    return len(df) * len(required_cols) - fails, fails, "; ".join(details) or "All clear"


def _check_date_logic(df: pd.DataFrame, start_col: str, end_col: str):
    """Check that end_date > start_date."""
    if start_col not in df.columns or end_col not in df.columns:
        return 0, 0, "Columns not found"
    start = pd.to_datetime(df[start_col], errors="coerce")
    end = pd.to_datetime(df[end_col], errors="coerce")
    mask = end > start
    fails = int((~mask).sum())
    return int(mask.sum()), fails, f"{fails} rows with end <= start" if fails else "All clear"


def _check_lte(df: pd.DataFrame, col_a: str, col_b: str, label: str):
    """Check that col_a <= col_b (e.g., delivered <= sent)."""
    if col_a not in df.columns or col_b not in df.columns:
        return 0, 0, "Columns not found"
    mask = df[col_a] <= df[col_b]
    fails = int((~mask).sum())
    return int(mask.sum()), fails, f"{fails} rows where {label}" if fails else "All clear"


def _check_rate_bounds(df: pd.DataFrame, numerator: str, denominator: str, label: str):
    """Check that a rate (numerator/denominator) is between 0 and 1."""
    if numerator not in df.columns or denominator not in df.columns:
        return 0, 0, "Columns not found"
    denom = df[denominator].replace(0, 1)  # avoid div by zero
    rate = df[numerator] / denom
    mask = (rate >= 0) & (rate <= 1)
    fails = int((~mask).sum())
    return int(mask.sum()), fails, f"{fails} rows with {label} out of bounds" if fails else "All clear"


def _check_non_negative(df: pd.DataFrame, col: str, label: str):
    """Check that values are >= 0."""
    if col not in df.columns:
        return 0, 0, "Column not found"
    mask = df[col] >= 0
    fails = int((~mask).sum())
    return int(mask.sum()), fails, f"{fails} rows with negative {label}" if fails else "All clear"


def _check_no_duplicates(df: pd.DataFrame, id_col: str):
    """Check for duplicate IDs."""
    if id_col not in df.columns:
        return 0, 0, "Column not found"
    dupes = df[id_col].duplicated().sum()
    return len(df) - int(dupes), int(dupes), f"{dupes} duplicate IDs" if dupes else "All clear"


def _check_department(df: pd.DataFrame, expected: str):
    """Check that department column matches expected value."""
    if "department" not in df.columns:
        return 0, 0, "Column not found"
    mask = df["department"] == expected
    fails = int((~mask).sum())
    return int(mask.sum()), fails, f"{fails} rows with wrong department" if fails else "All clear"


# ── Rule Definitions ─────────────────────────────────────────────────────

ANNUAL_GIVING_RULES = [
    {
        "name": "Null Check — Annual Giving",
        "table": "annual_giving_campaigns",
        "check_fn": lambda df: _check_nulls(
            df,
            ["campaign_id", "campaign_name", "department", "launch_date", "end_date",
             "records_sent", "emails_delivered", "emails_opened"],
        ),
    },
    {
        "name": "Date Logic — end_date > launch_date",
        "table": "annual_giving_campaigns",
        "check_fn": lambda df: _check_date_logic(df, "launch_date", "end_date"),
    },
    {
        "name": "Email Delivery — delivered ≤ sent",
        "table": "annual_giving_campaigns",
        "check_fn": lambda df: _check_lte(
            df, "emails_delivered", "records_sent", "delivered > sent"
        ),
    },
    {
        "name": "Open Rate Bounds — 0–100%",
        "table": "annual_giving_campaigns",
        "check_fn": lambda df: _check_rate_bounds(
            df, "emails_opened", "emails_delivered", "open rate"
        ),
    },
    {
        "name": "Click-Through Bounds — clicks ≤ opens",
        "table": "annual_giving_campaigns",
        "check_fn": lambda df: _check_lte(
            df, "links_clicked", "emails_opened", "clicks > opens"
        ),
    },
    {
        "name": "Gift Count Bounds — gifts ≤ sent",
        "table": "annual_giving_campaigns",
        "check_fn": lambda df: _check_lte(
            df, "gifts_received", "records_sent", "gifts > sent"
        ),
    },
    {
        "name": "Financial Sanity — total_raised ≥ 0",
        "table": "annual_giving_campaigns",
        "check_fn": lambda df: _check_non_negative(df, "total_raised", "total_raised"),
    },
    {
        "name": "Cost Sanity — campaign_cost ≥ 0",
        "table": "annual_giving_campaigns",
        "check_fn": lambda df: _check_non_negative(df, "campaign_cost", "campaign_cost"),
    },
    {
        "name": "Duplicate ID Check — campaign_id",
        "table": "annual_giving_campaigns",
        "check_fn": lambda df: _check_no_duplicates(df, "campaign_id"),
    },
    {
        "name": "Department Consistency — Annual Giving",
        "table": "annual_giving_campaigns",
        "check_fn": lambda df: _check_department(df, "Annual Giving"),
    },
]

ALUMNI_RELATIONS_RULES = [
    {
        "name": "Null Check — Alumni Relations",
        "table": "alumni_relations_events",
        "check_fn": lambda df: _check_nulls(
            df,
            ["event_id", "event_name", "department", "event_type", "event_date",
             "invitations_sent", "rsvps_received", "attendees"],
        ),
    },
    {
        "name": "RSVP Rate Bounds — RSVPs ≤ invitations",
        "table": "alumni_relations_events",
        "check_fn": lambda df: _check_lte(
            df, "rsvps_received", "invitations_sent", "RSVPs > invitations"
        ),
    },
    {
        "name": "Attendance Bounds — attendees ≤ RSVPs",
        "table": "alumni_relations_events",
        "check_fn": lambda df: _check_lte(
            df, "attendees", "rsvps_received", "attendees > RSVPs"
        ),
    },
    {
        "name": "Financial Sanity — donations ≥ 0",
        "table": "alumni_relations_events",
        "check_fn": lambda df: _check_non_negative(df, "donations_collected", "donations"),
    },
    {
        "name": "Duplicate ID Check — event_id",
        "table": "alumni_relations_events",
        "check_fn": lambda df: _check_no_duplicates(df, "event_id"),
    },
    {
        "name": "Department Consistency — Alumni Relations",
        "table": "alumni_relations_events",
        "check_fn": lambda df: _check_department(df, "Alumni Relations"),
    },
]

MAJOR_GIFTS_RULES = [
    {
        "name": "Null Check — Major Gifts",
        "table": "major_gifts_outreach",
        "check_fn": lambda df: _check_nulls(
            df,
            ["prospect_id", "prospect_name", "department", "gift_officer",
             "outreach_date", "total_touches", "meetings_held"],
        ),
    },
    {
        "name": "Meetings ≤ Touches",
        "table": "major_gifts_outreach",
        "check_fn": lambda df: _check_lte(
            df, "meetings_held", "total_touches", "meetings > touches"
        ),
    },
    {
        "name": "Financial Sanity — gift_committed ≥ 0",
        "table": "major_gifts_outreach",
        "check_fn": lambda df: _check_non_negative(df, "gift_committed", "gift_committed"),
    },
    {
        "name": "Duplicate ID Check — prospect_id",
        "table": "major_gifts_outreach",
        "check_fn": lambda df: _check_no_duplicates(df, "prospect_id"),
    },
    {
        "name": "Department Consistency — Major Gifts",
        "table": "major_gifts_outreach",
        "check_fn": lambda df: _check_department(df, "Major Gifts"),
    },
]

ALL_RULES = ANNUAL_GIVING_RULES + ALUMNI_RELATIONS_RULES + MAJOR_GIFTS_RULES
