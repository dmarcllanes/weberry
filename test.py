from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
)
from pathlib import Path
import sys

# -----------------------------
# Config
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
CRED_PATH = BASE_DIR / "secrets" / "cred.json"

PROPERTY_ID = "523567550"  # GA4 property ID (numbers only)

# -----------------------------
# Client init
# -----------------------------
def get_client():
    if not CRED_PATH.exists():
        raise FileNotFoundError(f"Credential file not found: {CRED_PATH}")

    return BetaAnalyticsDataClient.from_service_account_file(
        str(CRED_PATH)
    )

client = get_client()

# -----------------------------
# Overview metrics
# -----------------------------
def get_ga_overview():
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
        ],
    )

    response = client.run_report(request)

    if not response.rows:
        return {"users": 0, "sessions": 0, "pageviews": 0}

    metrics = response.rows[0].metric_values

    return {
        "users": int(metrics[0].value),
        "sessions": int(metrics[1].value),
        "pageviews": int(metrics[2].value),
    }

# -----------------------------
# Top pages + time spent
# -----------------------------
def get_top_pages(limit=5):
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        dimensions=[
            Dimension(name="pagePath"),
            Dimension(name="pageTitle"),
        ],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="userEngagementDuration"),
        ],
        order_bys=[{
            "metric": {"metric_name": "screenPageViews"},
            "desc": True
        }],
        limit=limit,
    )

    response = client.run_report(request)

    pages = []
    for row in response.rows:
        views = int(row.metric_values[0].value)
        engagement = float(row.metric_values[1].value)
        avg_time = round(engagement / views, 1) if views > 0 else 0

        pages.append({
            "path": row.dimension_values[0].value,
            "title": row.dimension_values[1].value,
            "views": views,
            "avg_time_sec": avg_time,
        })

    return pages

# -----------------------------
# Traffic sources
# -----------------------------
def get_traffic_sources(limit=5):
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        dimensions=[
            Dimension(name="sessionSourceMedium"),
        ],
        metrics=[
            Metric(name="sessions"),
        ],
        order_bys=[{
            "metric": {"metric_name": "sessions"},
            "desc": True
        }],
        limit=limit,
    )

    response = client.run_report(request)

    sources = []
    for row in response.rows:
        sources.append({
            "source": row.dimension_values[0].value or "(direct)",
            "sessions": int(row.metric_values[0].value),
        })

    return sources

# -----------------------------
# Device types
# -----------------------------
def get_device_types():
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        dimensions=[
            Dimension(name="deviceCategory"),
        ],
        metrics=[
            Metric(name="sessions"),
        ],
        order_bys=[{
            "metric": {"metric_name": "sessions"},
            "desc": True
        }],
    )

    response = client.run_report(request)

    devices = []
    for row in response.rows:
        devices.append({
            "device": row.dimension_values[0].value,
            "sessions": int(row.metric_values[0].value),
        })

    return devices

# -----------------------------
# Test runner
# -----------------------------
if __name__ == "__main__":
    try:
        print("Testing Google Analytics connection...")

        overview = get_ga_overview()
        pages = get_top_pages()
        sources = get_traffic_sources()
        devices = get_device_types()

        print("\nGA Overview (last 7 days)")
        print("------------------------")
        print(f"Users     : {overview['users']}")
        print(f"Sessions  : {overview['sessions']}")
        print(f"Pageviews : {overview['pageviews']}")

        print("\nTop Pages (last 30 days)")
        print("------------------------")
        for p in pages:
            mins = int(p["avg_time_sec"] // 60)
            secs = int(p["avg_time_sec"] % 60)
            print(f"{p['path']} | {p['views']} views | ⏱ {mins}m {secs}s")

        print("\nTraffic Sources")
        print("------------------------")
        for s in sources:
            print(f"{s['source']} | {s['sessions']} sessions")

        print("\nDevice Types")
        print("------------------------")
        for d in devices:
            print(f"{d['device']} | {d['sessions']} sessions")

    except Exception as e:
        print("\n❌ GA test failed")
        print(type(e).__name__, "-", e)
        sys.exit(1)
