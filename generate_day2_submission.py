from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


ROOT = Path(__file__).parent
OUTPUT = ROOT / "day2_results"


def save(dataframe, filename):
    dataframe.to_csv(OUTPUT / filename, index=False)


def load_data():
    sales = pd.read_csv(ROOT / "bm_sales.csv", parse_dates=["date"])
    stores = pd.read_csv(ROOT / "bm_stores.csv", parse_dates=["opening_date"])
    skus = pd.read_csv(ROOT / "bm_skus.csv")
    customers = pd.read_csv(ROOT / "bm_customers.csv", parse_dates=["registration_date"])
    promotions = pd.read_csv(ROOT / "bm_promotions.csv", parse_dates=["start_date", "end_date"])
    return sales, stores, skus, customers, promotions


def create_kpi_sheet():
    path = ROOT / "day2_kpi_definitions.pdf"
    pdf = canvas.Canvas(str(path), pagesize=letter)
    pdf.setTitle("Day 2 KPI Definitions")
    pdf.setFillColor(colors.HexColor("#17324D"))
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(48, 748, "Day 2 KPI Definitions")
    pdf.setFillColor(colors.HexColor("#486581"))
    pdf.setFont("Helvetica", 9)
    pdf.drawString(48, 732, "BlueMart retail analysis | Source: bm_*.csv")

    definitions = [
        ("Revenue", "SUM(bm_sales.total_value), grouped as requested. Currency is preserved as supplied."),
        ("Region", "bm_stores.city, because the source store table has city but no separate region field."),
        ("Store type", "bm_stores.store_type, such as Mall, Community, and High Street."),
        ("Top categories", "Product categories ranked by total revenue after joining sales to bm_skus."),
        ("Spend tier", "Customer lifetime spend split into thirds with NTILE(3): bottom = Low, middle = Medium, top = High."),
        ("Promotion effect", "Comparison of lines, units, revenue, and average line value when discount_pct > 0 versus 0. This is association, not causal proof."),
        ("Above-average customer", "A customer whose total spend exceeds the mean total spend across customers with a non-null customer_id."),
        ("Falling product sales", "A product whose latest available month has fewer units than its immediately previous available month."),
        ("Store rank", "DENSE_RANK by revenue within each region; rank 1 is the highest-revenue store."),
        ("Data quality", "Counts nulls, invalid numeric ranges, duplicate customer IDs, and missing store/SKU references."),
        ("Repeat purchase rate", "Customers with purchases on at least two distinct dates divided by all customers with a non-null purchase."),
        ("Category mix", "Category revenue divided by total revenue in the same region, expressed as a percentage."),
    ]
    y = 700
    for label, definition in definitions:
        pdf.setFillColor(colors.HexColor("#C05621"))
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(48, y, label)
        pdf.setFillColor(colors.HexColor("#243B53"))
        pdf.setFont("Helvetica", 8.5)
        pdf.drawString(150, y, definition)
        y -= 35
    pdf.setFillColor(colors.HexColor("#486581"))
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(48, 34, "Interpret results with the source-data limitations above, especially missing customer IDs and the promotion proxy.")
    pdf.save()
    return path


def generate_results():
    OUTPUT.mkdir(exist_ok=True)
    sales, stores, skus, customers, promotions = load_data()
    sales_stores = sales.merge(stores, on="store_id", how="left", validate="many_to_one")
    sales_skus = sales_stores.merge(skus, on="sku_id", how="left", validate="many_to_one")

    revenue_region_type = (sales_stores.groupby(["city", "store_type"], as_index=False)
                           .agg(revenue=("total_value", "sum"))
                           .rename(columns={"city": "region"})
                           .sort_values(["region", "revenue"], ascending=[True, False]))
    save(revenue_region_type.round({"revenue": 2}), "01_revenue_by_region_store_type.csv")

    top_categories = (sales_skus.groupby("category", as_index=False)
                      .agg(revenue=("total_value", "sum"))
                      .sort_values("revenue", ascending=False).head(5))
    save(top_categories.round({"revenue": 2}), "02_top_5_categories_by_revenue.csv")

    customer_spend = (sales.dropna(subset=["customer_id"])
                      .groupby("customer_id", as_index=False)
                      .agg(total_spend=("total_value", "sum")))
    customer_spend["spend_tier"] = pd.qcut(customer_spend["total_spend"].rank(method="first"), 3,
                                             labels=["Low", "Medium", "High"])
    save(customer_spend.sort_values("total_spend", ascending=False).round({"total_spend": 2}), "03_customer_spend_tiers.csv")

    promotion_comparison = (sales.assign(promotion_status=sales["discount_pct"].gt(0).map({True: "Promotion", False: "No promotion"}))
                             .groupby("promotion_status", as_index=False)
                             .agg(sales_lines=("total_value", "size"), units=("quantity", "sum"),
                                  revenue=("total_value", "sum"), average_line_value=("total_value", "mean")))
    save(promotion_comparison.round(2), "04_promotion_comparison.csv")

    average_spend = customer_spend["total_spend"].mean()
    above_average = customer_spend.loc[customer_spend["total_spend"] > average_spend].copy()
    above_average["average_customer_spend"] = average_spend
    save(above_average.sort_values("total_spend", ascending=False).round(2), "05_above_average_customers.csv")

    monthly = (sales.assign(sales_month=sales["date"].dt.to_period("M").dt.to_timestamp())
               .groupby(["sku_id", "sales_month"], as_index=False)
               .agg(units=("quantity", "sum"), revenue=("total_value", "sum")))
    monthly["prior_units"] = monthly.groupby("sku_id")["units"].shift(1)
    monthly["prior_revenue"] = monthly.groupby("sku_id")["revenue"].shift(1)
    latest = monthly.sort_values("sales_month").groupby("sku_id").tail(1)
    falling = latest[latest["units"] < latest["prior_units"]].merge(skus[["sku_id", "sku_name", "category"]], on="sku_id")
    falling["unit_change_pct"] = 100 * (falling["units"] - falling["prior_units"]) / falling["prior_units"]
    falling = falling.rename(columns={"sales_month": "latest_month", "units": "latest_units", "revenue": "latest_revenue"})
    save(falling.sort_values("unit_change_pct").round(2), "06_products_falling_month_over_month.csv")

    store_revenue = (sales_stores.groupby(["city", "store_id", "store_name", "store_type"], as_index=False)
                     .agg(revenue=("total_value", "sum")).rename(columns={"city": "region"}))
    store_revenue["region_rank"] = store_revenue.groupby("region")["revenue"].rank(method="dense", ascending=False).astype(int)
    save(store_revenue.sort_values(["region", "region_rank", "store_id"]).round({"revenue": 2}), "07_store_ranking_by_region.csv")

    quality = pd.DataFrame([
        ["bm_sales", "customer_id", sales["customer_id"].isna().sum(), "nullable customer ID"],
        ["bm_sales", "quantity", (sales["quantity"].isna() | sales["quantity"].le(0)).sum(), "must be positive"],
        ["bm_sales", "unit_price", (sales["unit_price"].isna() | sales["unit_price"].lt(0)).sum(), "must be non-negative"],
        ["bm_sales", "total_value", (sales["total_value"].isna() | sales["total_value"].lt(0)).sum(), "must be non-negative"],
        ["bm_sales", "discount_pct", (sales["discount_pct"].isna() | sales["discount_pct"].lt(0) | sales["discount_pct"].gt(100)).sum(), "must be 0 to 100"],
        ["bm_sales", "store_id FK", sales["store_id"].isin(stores["store_id"]).eq(False).sum(), "missing store reference"],
        ["bm_sales", "sku_id FK", sales["sku_id"].isin(skus["sku_id"]).eq(False).sum(), "missing SKU reference"],
        ["bm_customers", "cust_id duplicate", customers["cust_id"].duplicated().sum(), "duplicate primary key values"],
    ], columns=["table_name", "field_name", "issue_count", "check_description"])
    save(quality, "08_data_quality_check.csv")

    purchase_days = (sales.dropna(subset=["customer_id"])
                     .groupby("customer_id")["date"].nunique())
    repeat = pd.DataFrame([{"purchasing_customers": len(purchase_days), "repeat_customers": (purchase_days >= 2).sum(),
                            "repeat_purchase_rate_pct": 100 * (purchase_days >= 2).mean()}])
    save(repeat.round(2), "09_repeat_purchase_rate.csv")

    category_region = (sales_skus.groupby(["city", "category"], as_index=False)
                       .agg(revenue=("total_value", "sum")).rename(columns={"city": "region"}))
    category_region["region_mix_pct"] = category_region["revenue"] / category_region.groupby("region")["revenue"].transform("sum") * 100
    save(category_region.sort_values(["region", "revenue"], ascending=[True, False]).round(2), "10_category_mix_by_region.csv")

    return len(sales), average_spend, create_kpi_sheet()


if __name__ == "__main__":
    rows, average_spend, kpi_path = generate_results()
    print(f"Generated 10 CSV result files for {rows:,} sales rows in {OUTPUT}")
    print(f"Average customer spend: {average_spend:.2f}")
    print(f"Created {kpi_path}")