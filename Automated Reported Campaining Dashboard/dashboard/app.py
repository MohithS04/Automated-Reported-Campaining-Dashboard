"""
Automated Campaign Reporting Dashboard
=======================================
Premium Streamlit monitoring dashboard for university advancement campaigns.

5 Pages:
  1. Executive Summary — top-line KPIs & department overview
  2. Department Comparison — side-by-side analysis
  3. Campaign Performance — deep dive with filters
  4. Validation & Data Quality — audit trail
  5. Trend Analysis — time-series patterns

Run: streamlit run dashboard/app.py
"""

import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Add project root to path ───────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from pipeline.database.db_utils import get_connection

# ── Page Config ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Campaign Reporting Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium Dark Theme CSS ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #a5b4fc !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(168,85,247,0.08) 100%);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 16px;
        padding: 20px 24px;
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(99,102,241,0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(99,102,241,0.15);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-weight: 500;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-weight: 700;
        font-size: 2rem;
    }

    /* Headers */
    h1 {
        background: linear-gradient(135deg, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    h2 {
        color: #a5b4fc !important;
        font-weight: 700 !important;
        border-bottom: 2px solid rgba(99,102,241,0.2);
        padding-bottom: 8px;
    }
    h3 {
        color: #c4b5fd !important;
        font-weight: 600 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15,15,35,0.5);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        color: #94a3b8;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(168,85,247,0.2));
        color: #e2e8f0 !important;
    }

    /* Dataframes */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(99,102,241,0.15);
    }

    /* Divider */
    hr {
        border-color: rgba(99,102,241,0.15) !important;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: #475569;
        font-size: 0.8rem;
        padding: 24px 0;
        border-top: 1px solid rgba(99,102,241,0.1);
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)

# ── Plotly Theme ────────────────────────────────────────────────────────
PLOTLY_TEMPLATE = "plotly_dark"
COLORS = {
    "Annual Giving": "#818cf8",
    "Alumni Relations": "#c084fc",
    "Major Gifts": "#f472b6",
}
COLOR_SEQUENCE = ["#818cf8", "#c084fc", "#f472b6", "#34d399", "#fbbf24", "#f87171"]


# ══════════════════════════════════════════════════════════════════════════
# Data Loading
# ══════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def load_table(table_name: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


def load_all_data():
    ag = load_table("annual_giving_campaigns")
    ar = load_table("alumni_relations_events")
    mg = load_table("major_gifts_outreach")
    vl = load_table("validation_log")
    cm = load_table("campaign_metrics")
    return ag, ar, mg, vl, cm


# ══════════════════════════════════════════════════════════════════════════
# Sidebar Navigation
# ══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("# 📊 Campaign Reporter")
    st.markdown("---")
    st.markdown("### Navigation")
    page = st.radio(
        "Select Page",
        [
            "🏠 Executive Summary",
            "🏢 Department Comparison",
            "🎯 Campaign Performance",
            "✅ Validation & Quality",
            "📈 Trend Analysis",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align:center; color:#64748b; font-size:0.75rem;'>
        University Advancement<br/>
        Automated Reporting Pipeline<br/>
        <span style='color:#818cf8;'>v1.0</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════
# Load data
# ══════════════════════════════════════════════════════════════════════════

ag, ar, mg, vl, cm = load_all_data()


# ══════════════════════════════════════════════════════════════════════════
# PAGE 1: Executive Summary
# ══════════════════════════════════════════════════════════════════════════

if page == "🏠 Executive Summary":
    st.markdown("# Executive Summary")
    st.markdown("Top‑line performance metrics across all university advancement departments.")

    # KPI row
    total_campaigns = len(ag) + len(ar) + len(mg)
    total_raised = ag["total_raised"].sum() + ar["donations_collected"].sum() + mg["gift_committed"].sum()
    total_cost = ag["campaign_cost"].sum()
    avg_roi = cm[cm["metric_name"] == "roi"]["metric_value"].mean()
    validation_pass_rate = (vl["status"] == "PASS").mean() * 100

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Campaigns", f"{total_campaigns:,}")
    col2.metric("Total Raised", f"${total_raised:,.0f}")
    col3.metric("Total Cost", f"${total_cost:,.0f}")
    col4.metric("Avg ROI", f"{avg_roi:.1f}x")
    col5.metric("Validation Pass", f"{validation_pass_rate:.0f}%")

    st.markdown("---")

    # Department summary chart
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Revenue by Department")
        dept_revenue = pd.DataFrame({
            "Department": ["Annual Giving", "Alumni Relations", "Major Gifts"],
            "Revenue": [
                ag["total_raised"].sum(),
                ar["donations_collected"].sum(),
                mg["gift_committed"].sum(),
            ],
        })
        fig = px.bar(
            dept_revenue,
            x="Department",
            y="Revenue",
            color="Department",
            color_discrete_map=COLORS,
            template=PLOTLY_TEMPLATE,
            text_auto="$.2s",
        )
        fig.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis_title="Revenue ($)",
            font=dict(family="Inter"),
            height=400,
        )
        fig.update_traces(textposition="outside", marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### Campaign Distribution")
        dist_df = pd.DataFrame({
            "Department": ["Annual Giving", "Alumni Relations", "Major Gifts"],
            "Count": [len(ag), len(ar), len(mg)],
        })
        fig = px.pie(
            dist_df,
            values="Count",
            names="Department",
            color="Department",
            color_discrete_map=COLORS,
            template=PLOTLY_TEMPLATE,
            hole=0.55,
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=400,
        )
        fig.update_traces(textinfo="label+percent", textfont_size=12)
        st.plotly_chart(fig, use_container_width=True)

    # Recent metrics summary table
    st.markdown("### 📋 Key Metrics Summary")
    summary_metrics = cm.groupby(["department", "metric_name"])["metric_value"].mean().reset_index()
    summary_pivot = summary_metrics.pivot(index="metric_name", columns="department", values="metric_value")
    summary_pivot = summary_pivot.round(4)
    st.dataframe(summary_pivot, use_container_width=True, height=400)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 2: Department Comparison
# ══════════════════════════════════════════════════════════════════════════

elif page == "🏢 Department Comparison":
    st.markdown("# Department Comparison")
    st.markdown("Side-by-side analysis of all three advancement departments.")

    tab1, tab2, tab3 = st.tabs(["📊 Performance", "🕸️ Radar View", "📋 Detailed Stats"])

    with tab1:
        st.markdown("### Average Metrics by Department")
        avg_metrics = cm.groupby(["department", "metric_name"])["metric_value"].mean().reset_index()

        # Show grouped bar chart for common metrics
        fig = px.bar(
            avg_metrics,
            x="metric_name",
            y="metric_value",
            color="department",
            barmode="group",
            color_discrete_map=COLORS,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Metric",
            yaxis_title="Average Value",
            font=dict(family="Inter"),
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("### Department Radar Comparison")

        # Build radar for Annual Giving (use normalized values)
        ag_metrics = cm[cm["department"] == "Annual Giving"].groupby("metric_name")["metric_value"].mean()
        ar_metrics = cm[cm["department"] == "Alumni Relations"].groupby("metric_name")["metric_value"].mean()
        mg_metrics = cm[cm["department"] == "Major Gifts"].groupby("metric_name")["metric_value"].mean()

        # Common categories for radar
        col_l, col_r = st.columns(2)

        with col_l:
            if len(ag_metrics) > 0:
                cats = ag_metrics.index.tolist()
                vals = ag_metrics.values.tolist()
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=cats + [cats[0]],
                    fill="toself",
                    name="Annual Giving",
                    line_color="#818cf8",
                    fillcolor="rgba(129,140,248,0.15)",
                ))
                fig.update_layout(
                    polar=dict(bgcolor="rgba(0,0,0,0)"),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#94a3b8"),
                    title="Annual Giving Metrics",
                    height=400,
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_r:
            if len(ar_metrics) > 0:
                cats = ar_metrics.index.tolist()
                vals = ar_metrics.values.tolist()
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=cats + [cats[0]],
                    fill="toself",
                    name="Alumni Relations",
                    line_color="#c084fc",
                    fillcolor="rgba(192,132,252,0.15)",
                ))
                fig.update_layout(
                    polar=dict(bgcolor="rgba(0,0,0,0)"),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#94a3b8"),
                    title="Alumni Relations Metrics",
                    height=400,
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("### Detailed Department Statistics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 🎯 Annual Giving")
            st.metric("Campaigns", len(ag))
            st.metric("Total Raised", f"${ag['total_raised'].sum():,.0f}")
            st.metric("Avg Open Rate", f"{ag['emails_opened'].sum() / max(ag['emails_delivered'].sum(), 1) * 100:.1f}%")
            st.metric("Avg Conversion", f"{ag['gifts_received'].sum() / max(ag['records_sent'].sum(), 1) * 100:.1f}%")

        with col2:
            st.markdown("#### 🎉 Alumni Relations")
            st.metric("Events", len(ar))
            st.metric("Total Donations", f"${ar['donations_collected'].sum():,.0f}")
            st.metric("Avg RSVP Rate", f"{ar['rsvps_received'].sum() / max(ar['invitations_sent'].sum(), 1) * 100:.1f}%")
            st.metric("Avg Satisfaction", f"{ar['satisfaction_score'].mean():.1f}/5.0")

        with col3:
            st.markdown("#### 💎 Major Gifts")
            st.metric("Prospects", len(mg))
            st.metric("Total Committed", f"${mg['gift_committed'].sum():,.0f}")
            st.metric("Close Rate", f"{(mg['gift_committed'] > 0).mean() * 100:.1f}%")
            st.metric("Avg Gift", f"${mg[mg['gift_committed'] > 0]['gift_committed'].mean():,.0f}")


# ══════════════════════════════════════════════════════════════════════════
# PAGE 3: Campaign Performance Deep Dive
# ══════════════════════════════════════════════════════════════════════════

elif page == "🎯 Campaign Performance":
    st.markdown("# Campaign Performance Deep Dive")
    st.markdown("Filter and explore individual campaign metrics.")

    dept_choice = st.selectbox(
        "Select Department",
        ["Annual Giving", "Alumni Relations", "Major Gifts"],
    )

    if dept_choice == "Annual Giving":
        st.markdown("### 📧 Annual Giving Campaigns")

        # Filters
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            segments = ["All"] + sorted(ag["segment_name"].unique().tolist())
            seg_filter = st.selectbox("Filter by Segment", segments)
        with col_f2:
            sort_by = st.selectbox("Sort by", ["total_raised", "gifts_received", "emails_opened", "campaign_cost"])

        df = ag.copy()
        if seg_filter != "All":
            df = df[df["segment_name"] == seg_filter]
        df = df.sort_values(sort_by, ascending=False)

        # Scatter plot
        st.markdown("### Performance Scatter")
        fig = px.scatter(
            df,
            x="records_sent",
            y="total_raised",
            size="gifts_received",
            color="segment_name",
            hover_name="campaign_name",
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=COLOR_SEQUENCE,
            size_max=30,
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Table
        st.markdown("### Campaign Data")
        st.dataframe(df, use_container_width=True, height=400)

    elif dept_choice == "Alumni Relations":
        st.markdown("### 🎉 Alumni Relations Events")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            types = ["All"] + sorted(ar["event_type"].unique().tolist())
            type_filter = st.selectbox("Filter by Event Type", types)
        with col_f2:
            sort_by = st.selectbox("Sort by", ["donations_collected", "attendees", "satisfaction_score", "invitations_sent"])

        df = ar.copy()
        if type_filter != "All":
            df = df[df["event_type"] == type_filter]
        df = df.sort_values(sort_by, ascending=False)

        # Bar chart
        st.markdown("### Event Attendance vs Donations")
        fig = px.bar(
            df.head(20),
            x="event_name",
            y=["attendees", "rsvps_received"],
            barmode="group",
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=["#c084fc", "#818cf8"],
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=450,
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True, height=400)

    else:  # Major Gifts
        st.markdown("### 💎 Major Gifts Outreach")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            officers = ["All"] + sorted(mg["gift_officer"].unique().tolist())
            officer_filter = st.selectbox("Filter by Gift Officer", officers)
        with col_f2:
            sort_by = st.selectbox("Sort by", ["gift_committed", "proposal_amount", "total_touches", "cultivation_days"])

        df = mg.copy()
        if officer_filter != "All":
            df = df[df["gift_officer"] == officer_filter]
        df = df.sort_values(sort_by, ascending=False)

        # Funnel visualization
        st.markdown("### Prospect Funnel")
        funnel_data = pd.DataFrame({
            "Stage": ["Total Touches", "Meetings Held", "Proposals Sent", "Gifts Committed"],
            "Count": [
                df["total_touches"].sum(),
                df["meetings_held"].sum(),
                df["proposals_sent"].sum(),
                (df["gift_committed"] > 0).sum(),
            ],
        })
        fig = px.funnel(
            funnel_data,
            x="Count",
            y="Stage",
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=["#f472b6"],
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True, height=400)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 4: Validation & Data Quality
# ══════════════════════════════════════════════════════════════════════════

elif page == "✅ Validation & Quality":
    st.markdown("# Validation & Data Quality")
    st.markdown("Audit trail of all validation checks across the pipeline.")

    # Summary KPIs
    total_checks = len(vl)
    passed = (vl["status"] == "PASS").sum()
    failed = (vl["status"] == "FAIL").sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Checks", total_checks)
    col2.metric("Passed ✅", int(passed))
    col3.metric("Failed ❌", int(failed))

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Pass/Fail Distribution")
        pf_df = pd.DataFrame({
            "Status": ["PASS", "FAIL"],
            "Count": [int(passed), int(failed)],
        })
        colors = ["#34d399", "#f87171"]
        fig = px.pie(
            pf_df,
            values="Count",
            names="Status",
            color="Status",
            color_discrete_map={"PASS": "#34d399", "FAIL": "#f87171"},
            template=PLOTLY_TEMPLATE,
            hole=0.6,
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=350,
        )
        fig.update_traces(textinfo="label+value", textfont_size=14)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### Checks per Table")
        table_counts = vl.groupby("table_name")["status"].value_counts().unstack(fill_value=0).reset_index()
        fig = px.bar(
            vl.groupby("table_name").size().reset_index(name="count"),
            x="table_name",
            y="count",
            color="table_name",
            color_discrete_sequence=COLOR_SEQUENCE,
            template=PLOTLY_TEMPLATE,
            text_auto=True,
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            showlegend=False,
            height=350,
            xaxis_title="Table",
            yaxis_title="Number of Checks",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap of validation checks
    st.markdown("### Validation Heatmap")
    heatmap_data = vl.pivot_table(
        index="rule_name",
        columns="table_name",
        values="fail_count",
        aggfunc="sum",
        fill_value=-1,
    )
    # Replace -1 with NaN for non-applicable cells
    heatmap_data = heatmap_data.replace(-1, float("nan"))

    fig = px.imshow(
        heatmap_data.values,
        x=heatmap_data.columns.tolist(),
        y=heatmap_data.index.tolist(),
        color_continuous_scale=["#34d399", "#fbbf24", "#f87171"],
        template=PLOTLY_TEMPLATE,
        aspect="auto",
        labels=dict(color="Fail Count"),
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Full log table
    st.markdown("### 📋 Full Validation Log")
    st.dataframe(
        vl[["rule_name", "table_name", "status", "fail_count", "details", "run_ts"]],
        use_container_width=True,
        height=400,
    )


# ══════════════════════════════════════════════════════════════════════════
# PAGE 5: Trend Analysis
# ══════════════════════════════════════════════════════════════════════════

elif page == "📈 Trend Analysis":
    st.markdown("# Trend Analysis")
    st.markdown("Time-series patterns and seasonal analysis across campaigns.")

    tab1, tab2, tab3 = st.tabs(["📧 Annual Giving Trends", "🎉 Event Trends", "💎 Gift Pipeline"])

    with tab1:
        st.markdown("### Campaign Performance Over Time")
        ag_copy = ag.copy()
        ag_copy["launch_date"] = pd.to_datetime(ag_copy["launch_date"])
        ag_copy = ag_copy.sort_values("launch_date")
        ag_copy["month"] = ag_copy["launch_date"].dt.to_period("M").astype(str)

        monthly = ag_copy.groupby("month").agg(
            total_raised=("total_raised", "sum"),
            campaigns=("campaign_id", "count"),
            avg_open_rate=("emails_opened", "sum"),
            avg_delivered=("emails_delivered", "sum"),
        ).reset_index()
        monthly["open_rate"] = monthly["avg_open_rate"] / monthly["avg_delivered"].clip(lower=1) * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["month"],
            y=monthly["total_raised"],
            name="Total Raised ($)",
            line=dict(color="#818cf8", width=3),
            fill="tonexty" if len(monthly) > 1 else None,
            fillcolor="rgba(129,140,248,0.1)",
        ))
        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=400,
            yaxis_title="Total Raised ($)",
            xaxis_title="Month",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Rolling average
        st.markdown("### Open Rate Trend")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=monthly["month"],
            y=monthly["open_rate"],
            name="Open Rate (%)",
            line=dict(color="#c084fc", width=2),
            mode="lines+markers",
        ))
        if len(monthly) >= 3:
            fig2.add_trace(go.Scatter(
                x=monthly["month"],
                y=monthly["open_rate"].rolling(3, min_periods=1).mean(),
                name="3‑Month Avg",
                line=dict(color="#fbbf24", width=2, dash="dash"),
            ))
        fig2.update_layout(
            template=PLOTLY_TEMPLATE,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=350,
            yaxis_title="Open Rate (%)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown("### Event Attendance Trends")
        ar_copy = ar.copy()
        ar_copy["event_date"] = pd.to_datetime(ar_copy["event_date"])
        ar_copy = ar_copy.sort_values("event_date")
        ar_copy["month"] = ar_copy["event_date"].dt.to_period("M").astype(str)

        ev_monthly = ar_copy.groupby("month").agg(
            total_attendees=("attendees", "sum"),
            total_donations=("donations_collected", "sum"),
            events=("event_id", "count"),
            avg_satisfaction=("satisfaction_score", "mean"),
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=ev_monthly["month"],
            y=ev_monthly["total_attendees"],
            name="Attendees",
            marker_color="#c084fc",
        ))
        fig.add_trace(go.Scatter(
            x=ev_monthly["month"],
            y=ev_monthly["total_donations"],
            name="Donations ($)",
            line=dict(color="#f472b6", width=3),
            yaxis="y2",
        ))
        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=400,
            yaxis=dict(title="Attendees"),
            yaxis2=dict(title="Donations ($)", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Satisfaction trend
        st.markdown("### Satisfaction Score Trend")
        fig3 = px.line(
            ev_monthly,
            x="month",
            y="avg_satisfaction",
            template=PLOTLY_TEMPLATE,
            markers=True,
            color_discrete_sequence=["#34d399"],
        )
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            yaxis_title="Avg Satisfaction (out of 5)",
            height=350,
        )
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.markdown("### Major Gifts Pipeline")
        mg_copy = mg.copy()
        mg_copy["outreach_date"] = pd.to_datetime(mg_copy["outreach_date"])
        mg_copy = mg_copy.sort_values("outreach_date")
        mg_copy["quarter"] = mg_copy["outreach_date"].dt.to_period("Q").astype(str)

        q_data = mg_copy.groupby("quarter").agg(
            total_proposals=("proposal_amount", "sum"),
            total_committed=("gift_committed", "sum"),
            prospects=("prospect_id", "count"),
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=q_data["quarter"],
            y=q_data["total_proposals"],
            name="Proposals ($)",
            marker_color="rgba(244,114,182,0.4)",
        ))
        fig.add_trace(go.Bar(
            x=q_data["quarter"],
            y=q_data["total_committed"],
            name="Committed ($)",
            marker_color="#f472b6",
        ))
        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=400,
            barmode="overlay",
            yaxis_title="Amount ($)",
            xaxis_title="Quarter",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Gift officer performance
        st.markdown("### Gift Officer Performance")
        officer_perf = mg_copy.groupby("gift_officer").agg(
            prospects=("prospect_id", "count"),
            total_committed=("gift_committed", "sum"),
            avg_cultivation=("cultivation_days", "mean"),
        ).reset_index().sort_values("total_committed", ascending=False)

        fig = px.bar(
            officer_perf,
            x="gift_officer",
            y="total_committed",
            color="total_committed",
            color_continuous_scale=["#4c1d95", "#818cf8", "#c084fc", "#f472b6"],
            template=PLOTLY_TEMPLATE,
            text_auto="$.2s",
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=400,
            xaxis_title="Gift Officer",
            yaxis_title="Total Committed ($)",
            showlegend=False,
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)


# ── Footer ──────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer-text">Automated Campaign Reporting Pipeline · University Advancement · Built with Streamlit & Plotly</div>',
    unsafe_allow_html=True,
)
