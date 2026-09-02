from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


ROOT = Path(__file__).parent


def build_summary_metrics():
    monthly = pd.read_csv(ROOT / "day3_results" / "05_monthly_running_revenue.csv", parse_dates=["revenue_month"])
    region = pd.read_csv(ROOT / "day2_results" / "01_revenue_by_region_store_type.csv")
    rfm = pd.read_csv(ROOT / "day3_results" / "01b_rfm_segment_summary.csv")
    yoy = pd.read_csv(ROOT / "day3_results" / "04_revenue_growth_yoy.csv")
    repeat = pd.read_csv(ROOT / "day2_results" / "09_repeat_purchase_rate.csv")

    total_revenue = float(monthly["monthly_revenue"].sum())
    latest_month = monthly.sort_values("revenue_month").iloc[-1]
    highest_region = region.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False).iloc[0]
    champions = rfm.loc[rfm["rfm_segment"] == "Champions", "customers"]
    champions_count = int(champions.iloc[0]) if not champions.empty else 0
    champions_pct = float(rfm.loc[rfm["rfm_segment"] == "Champions", "customer_pct"].iloc[0]) if not champions.empty else 0.0
    latest_yoy = yoy.sort_values("revenue_year").iloc[-1]
    repeat_rate = float(repeat["repeat_purchase_rate_pct"].iloc[0])

    metrics = pd.DataFrame([
        {"metric_name": "total_revenue", "metric_value": round(total_revenue, 2), "metric_unit": "AED", "metric_notes": "Sum of monthly revenue across all months"},
        {"metric_name": "latest_month", "metric_value": latest_month["revenue_month"].strftime("%Y-%m"), "metric_unit": "month", "metric_notes": "Most recent month in dataset"},
        {"metric_name": "latest_month_revenue", "metric_value": round(float(latest_month["monthly_revenue"]), 2), "metric_unit": "AED", "metric_notes": "Revenue in most recent month"},
        {"metric_name": "highest_revenue_region", "metric_value": highest_region["region"], "metric_unit": "region", "metric_notes": "Region with maximum total revenue"},
        {"metric_name": "highest_revenue_region_value", "metric_value": round(float(highest_region["revenue"]), 2), "metric_unit": "AED", "metric_notes": "Total revenue for top region"},
        {"metric_name": "champions_customers", "metric_value": champions_count, "metric_unit": "customers", "metric_notes": "RFM segment count"},
        {"metric_name": "champions_pct", "metric_value": round(champions_pct, 2), "metric_unit": "percent", "metric_notes": "Champions share of customer base"},
        {"metric_name": "latest_yoy_growth_pct", "metric_value": round(float(latest_yoy["yoy_growth_pct"]), 2), "metric_unit": "percent", "metric_notes": "Latest year-over-year revenue growth"},
        {"metric_name": "repeat_purchase_rate_pct", "metric_value": round(repeat_rate, 2), "metric_unit": "percent", "metric_notes": "Customers with >=2 distinct purchase days"},
    ])
    metrics.to_csv(ROOT / "summary_metrics.csv", index=False)
    return metrics


def create_executive_summary(metrics):
    summary_map = {row.metric_name: row.metric_value for row in metrics.itertuples(index=False)}
    pdf_path = ROOT / "executive_summary.pdf"
    pdf = canvas.Canvas(str(pdf_path), pagesize=letter)
    pdf.setTitle("Executive Summary - Retail Analytics Day 4")

    pdf.setFillColor(colors.HexColor("#0B2545"))
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(48, 760, "Executive Summary - Retail Analytics")
    pdf.setFillColor(colors.HexColor("#134074"))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(48, 744, "Scope: Day 2 and Day 3 outputs | Period: 2021-01 to 2025-10")

    y = 710
    sections = [
        ("Business Question 1: How is revenue trending?",
         [
             f"Total revenue reached AED {summary_map['total_revenue']:,} across the observed period.",
             f"The most recent month ({summary_map['latest_month']}) recorded AED {summary_map['latest_month_revenue']:,}.",
             f"Latest YoY growth is {summary_map['latest_yoy_growth_pct']}%, indicating a recent slowdown that needs category-level action.",
         ]),
        ("Business Question 2: Where is revenue concentrated?",
         [
             f"{summary_map['highest_revenue_region']} is the top-contributing region with AED {summary_map['highest_revenue_region_value']:,}.",
             "Regional/store-type analysis shows that Mall and High Street formats carry most revenue concentration.",
             "This supports region-specific assortment and pricing plans rather than a single national strategy.",
         ]),
        ("Business Question 3: What does customer quality look like?",
         [
             f"Champions represent {summary_map['champions_pct']}% of customers ({int(summary_map['champions_customers'])} customers).",
             f"Repeat purchase rate is {summary_map['repeat_purchase_rate_pct']}% under the current definition (>=2 purchase dates).",
             "Retention heatmaps show stable engagement for active cohorts, but At Risk/Lost segments still need reactivation programs.",
         ]),
    ]

    for title, bullets in sections:
        pdf.setFillColor(colors.HexColor("#0B2545"))
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(48, y, title)
        y -= 18
        pdf.setFillColor(colors.HexColor("#1D3557"))
        pdf.setFont("Helvetica", 10)
        for bullet in bullets:
            pdf.drawString(60, y, f"- {bullet}")
            y -= 15
        y -= 12

    pdf.setFillColor(colors.HexColor("#134074"))
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(48, 54, "Prepared for Day 4 submission: retail_eda.ipynb, executive_summary.pdf, summary_metrics.csv")
    pdf.save()


if __name__ == "__main__":
    metrics_df = build_summary_metrics()
    create_executive_summary(metrics_df)
    print("Created summary_metrics.csv and executive_summary.pdf")