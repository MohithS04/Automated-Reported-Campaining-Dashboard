"""
Synthetic Data Generator for Automated Campaign Reporting Pipeline.

Generates realistic campaign data for 3 university advancement departments:
  - Annual Giving (120 campaigns)
  - Alumni Relations (80 events)
  - Major Gifts (50 prospects)

Run once before the pipeline: python pipeline/generator/generator.py
Saves all files to data/inputs/
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# Resolve paths relative to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "inputs")


def ensure_output_dir():
    """Create the output directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# File 1: Annual Giving Campaigns  (120 rows)
# ---------------------------------------------------------------------------

ANNUAL_GIVING_CAMPAIGN_NAMES = [
    "Spring Annual Fund 2024",
    "Homecoming Appeal 2023",
    "Year-End Giving Drive",
    "Faculty Excellence Fund",
    "Student Scholarship Push",
    "Alumni Loyalty Campaign",
    "Giving Tuesday Blitz",
    "President's Circle Appeal",
    "Legacy Giving Initiative",
    "Senior Class Gift",
    "Parents Fund Campaign",
    "Athletics Booster Drive",
    "Library Enrichment Fund",
    "STEM Innovation Campaign",
    "Arts & Culture Appeal",
    "Community Impact Drive",
    "Research Excellence Fund",
    "Campus Beautification",
    "Emergency Relief Fund",
    "Digital Learning Initiative",
    "Global Outreach Campaign",
    "Diversity & Inclusion Fund",
    "Health Sciences Appeal",
    "Sustainability Initiative",
    "First-Gen Student Fund",
]

SEGMENTS = [
    "All Alumni",
    "Lapsed Donors",
    "First-Time Donors",
    "Major Gift Prospects",
    "Young Alumni",
]


def generate_annual_giving(n: int = 120) -> pd.DataFrame:
    """Generate annual giving campaign records."""
    rows = []
    for i in range(1, n + 1):
        campaign_id = f"AG-2023-{i:03d}"
        # AG-2023-001 through AG-2024-120
        if i > 60:
            campaign_id = f"AG-2024-{i:03d}"

        campaign_name = random.choice(ANNUAL_GIVING_CAMPAIGN_NAMES)
        department = "Annual Giving"

        # launch_date between Jan 2023 and Dec 2024
        launch_date = fake.date_between(
            start_date=datetime(2023, 1, 1), end_date=datetime(2024, 12, 1)
        )
        end_date = launch_date + timedelta(days=random.randint(14, 60))

        segment_name = random.choice(SEGMENTS)
        records_sent = random.randint(500, 5000)

        # Delivery: 90–99% of sent
        delivery_rate = random.uniform(0.90, 0.99)
        emails_delivered = int(records_sent * delivery_rate)

        # Opens: 15–35% of delivered
        open_rate = random.uniform(0.15, 0.35)
        emails_opened = int(emails_delivered * open_rate)

        # Clicks: 20–50% of opened
        click_rate = random.uniform(0.20, 0.50)
        links_clicked = int(emails_opened * click_rate)

        # Gifts: 1–6% of sent
        gift_rate = random.uniform(0.01, 0.06)
        gifts_received = int(records_sent * gift_rate)

        total_raised = round(random.uniform(500, 50000), 2)
        campaign_cost = round(random.uniform(200, 5000), 2)

        rows.append(
            {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "department": department,
                "launch_date": launch_date.isoformat(),
                "end_date": end_date.isoformat(),
                "segment_name": segment_name,
                "records_sent": records_sent,
                "emails_delivered": emails_delivered,
                "emails_opened": emails_opened,
                "links_clicked": links_clicked,
                "gifts_received": gifts_received,
                "total_raised": total_raised,
                "campaign_cost": campaign_cost,
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# File 2: Alumni Relations Events  (80 rows)
# ---------------------------------------------------------------------------

EVENT_TYPES = ["Reunion", "Networking", "Homecoming", "Fundraiser", "Volunteer"]

EVENT_NAMES = [
    "Class of 2014 Reunion",
    "Spring Networking Mixer",
    "Homecoming Weekend Gala",
    "Annual Charity Auction",
    "Campus Volunteer Day",
    "Regional Alumni Meetup",
    "Career Mentorship Night",
    "Founders Day Celebration",
    "Alumni Awards Dinner",
    "Tailgate & Traditions",
    "Family Weekend Brunch",
    "Winter Holiday Social",
    "Summer Alumni Picnic",
    "Tech Alumni Symposium",
    "Young Alumni Happy Hour",
]


def generate_alumni_relations(n: int = 80) -> pd.DataFrame:
    """Generate alumni relations event records."""
    rows = []
    for i in range(1, n + 1):
        event_id = f"AR-EVT-{i:03d}"
        event_name = random.choice(EVENT_NAMES)
        department = "Alumni Relations"
        event_type = random.choice(EVENT_TYPES)
        event_date = fake.date_between(
            start_date=datetime(2023, 1, 1), end_date=datetime(2024, 12, 1)
        )

        invitations_sent = random.randint(200, 3000)

        # RSVPs: 15–45% of invitations
        rsvp_rate = random.uniform(0.15, 0.45)
        rsvps_received = int(invitations_sent * rsvp_rate)

        # Attendees: 75–95% of RSVPs
        attendance_rate = random.uniform(0.75, 0.95)
        attendees = int(rsvps_received * attendance_rate)

        donations_collected = round(random.uniform(0, 25000), 2)
        new_contacts = random.randint(5, 50)

        # Follow-ups: 80–100% of attendees
        follow_up_rate = random.uniform(0.80, 1.00)
        follow_ups_sent = int(attendees * follow_up_rate)

        satisfaction_score = round(random.uniform(3.0, 5.0), 1)

        rows.append(
            {
                "event_id": event_id,
                "event_name": event_name,
                "department": department,
                "event_type": event_type,
                "event_date": event_date.isoformat(),
                "invitations_sent": invitations_sent,
                "rsvps_received": rsvps_received,
                "attendees": attendees,
                "donations_collected": donations_collected,
                "new_contacts": new_contacts,
                "follow_ups_sent": follow_ups_sent,
                "satisfaction_score": satisfaction_score,
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# File 3: Major Gifts Outreach  (50 rows)
# ---------------------------------------------------------------------------

GIFT_OFFICERS = [
    "Sarah Mitchell",
    "James Crawford",
    "Linda Park",
    "Robert Chen",
    "Emma Davis",
    "Michael Torres",
    "Jennifer Wu",
    "David Okafor",
]


def generate_major_gifts(n: int = 50) -> pd.DataFrame:
    """Generate major gifts outreach records."""
    rows = []
    for i in range(1, n + 1):
        prospect_id = f"MG-PR-{i:03d}"
        prospect_name = fake.name()
        department = "Major Gifts"
        gift_officer = random.choice(GIFT_OFFICERS)
        outreach_date = fake.date_between(
            start_date=datetime(2023, 1, 1), end_date=datetime(2024, 12, 1)
        )

        total_touches = random.randint(3, 20)
        meetings_held = random.randint(1, min(8, total_touches))
        proposals_sent = random.randint(0, min(3, meetings_held))

        proposal_amount = round(random.uniform(10000, 500000), 2) if proposals_sent > 0 else 0.0

        # Gift committed: 0 or 50–100% of proposal
        if proposals_sent > 0 and random.random() > 0.35:
            commit_rate = random.uniform(0.50, 1.00)
            gift_committed = round(proposal_amount * commit_rate, 2)
            commitment_date = (
                outreach_date + timedelta(days=random.randint(30, 180))
            ).isoformat()
        else:
            gift_committed = 0.0
            commitment_date = ""

        cultivation_days = random.randint(30, 365)

        rows.append(
            {
                "prospect_id": prospect_id,
                "prospect_name": prospect_name,
                "department": department,
                "gift_officer": gift_officer,
                "outreach_date": outreach_date.isoformat(),
                "total_touches": total_touches,
                "meetings_held": meetings_held,
                "proposals_sent": proposals_sent,
                "proposal_amount": proposal_amount,
                "gift_committed": gift_committed,
                "commitment_date": commitment_date,
                "cultivation_days": cultivation_days,
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Generate all synthetic data files."""
    ensure_output_dir()

    print("=" * 60)
    print("  Automated Campaign Reporting — Data Generator")
    print("=" * 60)

    # Annual Giving
    ag = generate_annual_giving(120)
    ag_path = os.path.join(OUTPUT_DIR, "annual_giving_campaigns.csv")
    ag.to_csv(ag_path, index=False)
    print(f"✅  annual_giving_campaigns.csv  → {len(ag)} rows")

    # Alumni Relations
    ar = generate_alumni_relations(80)
    ar_path = os.path.join(OUTPUT_DIR, "alumni_relations_events.csv")
    ar.to_csv(ar_path, index=False)
    print(f"✅  alumni_relations_events.csv   → {len(ar)} rows")

    # Major Gifts
    mg = generate_major_gifts(50)
    mg_path = os.path.join(OUTPUT_DIR, "major_gifts_outreach.csv")
    mg.to_csv(mg_path, index=False)
    print(f"✅  major_gifts_outreach.csv      → {len(mg)} rows")

    print(f"\nAll files saved to: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
