from itertools import combinations
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).parent
OUTPUT = ROOT / "day3_results"
SNAPSHOT_DATE = pd.Timestamp("2025-10-31")


def save(dataframe, filename):
    dataframe.to_csv(OUTPUT / filename, index=False)


def generate():
    OUTPUT.mkdir(exist_ok=True)
    sales = pd.read_csv(ROOT / "bm_sales.csv", parse_dates=["date"])
    customers = pd.read_csv(ROOT / "bm_customers.csv", parse_dates=["registration_date"])
    skus = pd.read_csv(ROOT / "bm_skus.csv")

    identified_sales = sales.dropna(subset=["customer_id"]).copy()
    rfm = (identified_sales.groupby("customer_id", as_index=False)
           .agg(last_purchase=("date", "max"), frequency=("date", "nunique"), monetary=("total_value", "sum")))
    rfm["recency_days"] = (SNAPSHOT_DATE - rfm["last_purchase"]).dt.days
    rfm["recency_score"] = 6 - pd.qcut(rfm["recency_days"].rank(method="first"), 5, labels=False)
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=False) + 1
    rfm["monetary_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=False) + 1
    rfm = rfm.astype({"recency_score": "int64", "frequency_score": "int64", "monetary_score": "int64"})

    def segment(row):
        if row.recency_score >= 4 and row.frequency_score >= 4 and row.monetary_score >= 4:
            return "Champions"
        if row.frequency_score >= 4 and row.monetary_score >= 3:
            return "Loyal"
        if row.recency_score <= 2 and (row.frequency_score >= 3 or row.monetary_score >= 3):
            return "At Risk"
        return "Lost"

    rfm["rfm_segment"] = rfm.apply(segment, axis=1)
    save(rfm[["customer_id", "last_purchase", "recency_days", "frequency", "monetary",
              "recency_score", "frequency_score", "monetary_score", "rfm_segment"]]
         .sort_values(["rfm_segment", "monetary"], ascending=[True, False]).round({"monetary": 2}), "01_rfm_customer_scores.csv")
    summary = (rfm.groupby("rfm_segment", as_index=False)
               .agg(customers=("customer_id", "nunique"), average_recency_days=("recency_days", "mean"),
                    average_frequency=("frequency", "mean"), total_monetary=("monetary", "sum"),
                    average_monetary=("monetary", "mean")))
    summary["customer_pct"] = summary["customers"] / summary["customers"].sum() * 100
    save(summary.round(2), "01b_rfm_segment_summary.csv")

    customer_activity = identified_sales.merge(customers[["cust_id", "registration_date"]], left_on="customer_id", right_on="cust_id", how="inner")
    customer_activity = customer_activity[customer_activity["date"] >= customer_activity["registration_date"]].copy()
    customer_activity["cohort_month"] = customer_activity["registration_date"].dt.to_period("M").dt.to_timestamp()
    customer_activity["activity_month"] = customer_activity["date"].dt.to_period("M").dt.to_timestamp()
    activity = customer_activity[["customer_id", "cohort_month", "activity_month"]].drop_duplicates()
    cohort_sizes = activity.groupby("cohort_month")["customer_id"].nunique().rename("cohort_customers")
    retention = (activity.groupby(["cohort_month", "activity_month"])["customer_id"].nunique().rename("active_customers").reset_index())
    retention["months_since_signup"] = ((retention["activity_month"].dt.year - retention["cohort_month"].dt.year) * 12
                                          + retention["activity_month"].dt.month - retention["cohort_month"].dt.month)
    retention = retention[retention["months_since_signup"] >= 0].copy()
    retention["cohort_customers"] = retention["cohort_month"].map(cohort_sizes)
    retention["retention_pct"] = retention["active_customers"] / retention["cohort_customers"] * 100
    retention = retention.sort_values(["cohort_month", "months_since_signup"])
    retention["retention_pct"] = retention["retention_pct"].round(2)
    save(retention, "02_cohort_retention.csv")

    pair_rows = []
    for (customer_id, purchase_date), group in identified_sales.groupby(["customer_id", "date"]):
        product_ids = sorted(group["sku_id"].drop_duplicates())
        pair_rows.extend((customer_id, purchase_date, left, right) for left, right in combinations(product_ids, 2))
    pairs = pd.DataFrame(pair_rows, columns=["customer_id", "purchase_date", "sku_id_1", "sku_id_2"])
    pair_summary = (pairs.groupby(["sku_id_1", "sku_id_2"], as_index=False)
                    .agg(purchase_occasions=("purchase_date", "size"), customers=("customer_id", "nunique")))
    pair_summary = pair_summary.merge(skus[["sku_id", "sku_name"]].rename(columns={"sku_id": "sku_id_1", "sku_name": "product_1"}), on="sku_id_1")
    pair_summary = pair_summary.merge(skus[["sku_id", "sku_name"]].rename(columns={"sku_id": "sku_id_2", "sku_name": "product_2"}), on="sku_id_2")
    save(pair_summary.sort_values(["purchase_occasions", "customers"], ascending=False).head(50), "03_top_product_pairs.csv")

    yearly = sales.assign(revenue_year=sales["date"].dt.year).groupby("revenue_year", as_index=False)["total_value"].sum().rename(columns={"total_value": "revenue"})
    yearly["prior_year_revenue"] = yearly["revenue"].shift(1)
    yearly["yoy_growth_pct"] = (yearly["revenue"] - yearly["prior_year_revenue"]) / yearly["prior_year_revenue"] * 100
    save(yearly.round(2), "04_revenue_growth_yoy.csv")

    monthly = sales.assign(revenue_month=sales["date"].dt.to_period("M").dt.to_timestamp()).groupby("revenue_month", as_index=False)["total_value"].sum().rename(columns={"total_value": "monthly_revenue"})
    monthly["running_total_revenue"] = monthly["monthly_revenue"].cumsum()
    save(monthly.round(2), "05_monthly_running_revenue.csv")

    return len(rfm), len(retention), len(pair_summary), len(yearly), len(monthly)


if __name__ == "__main__":
    counts = generate()
    print(f"Generated Day 3 outputs in {OUTPUT}: RFM={counts[0]}, cohort rows={counts[1]}, pairs={counts[2]}, years={counts[3]}, months={counts[4]}")