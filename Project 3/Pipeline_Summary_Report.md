# 🏥 Clinical Readmission Pipeline — Executive Summary
**Pipeline:** Steps 1–3 (EDA → Cleaning → Feature Engineering) | **Date:** 2026-09-01 | **Target:** `Readmission_30d`

---

## 📊 Step 1 — Data Collection & Exploration
| Metric | Value |
|---|---|
| Raw records loaded | **1,155,000 patients** |
| Raw columns | **41 features** |
| Target class balance | 🟢 Not Readmitted: **84.98%** (910,243) &nbsp;·&nbsp; 🔴 Readmitted: **15.02%** (160,918) — *imbalanced* |
| Key issues found | Duplicate case-mismatched columns (`Age`/`age`, `Gender`/`gender`, `Drug_Name`/`drug_name`), 100% null columns (`Extra_Col_1/2`), invalid values (Age up to 999, negative weights) |
| Outputs generated | ✅ `step1_clinical_distributions.png` &nbsp;·&nbsp; ✅ `step1_correlation_matrix.png` |

---

## 🧹 Step 2 — Data Cleaning & Preprocessing
| Phase | Result |
|---|---|
| Column reduction | Dropped 11 columns (nulls, duplicates, redundant) → **41 → 30 columns** |
| Row validation | Removed 37,988 rows with invalid Age/Weight |
| Missing target rows | Dropped 81,110 rows (no `Readmission_30d` label) |
| Imputation | Numeric → median, categorical → mode (all columns filled) |
| Duplicates removed | 63,351 duplicate rows dropped |
| Outlier capping (IQR) | Applied to Age, BMI, Dosage, Hemoglobin, Creatinine, ALT/AST enzymes |
| Encoding | Label-encoded `Gender`; one-hot encoded `Drug_Name`, `Route` |
| **Final output** | **`data_cleaned.csv` → 972,551 rows × 553 columns** |

⚠️ **Data quality note:** `Gender` retains messy raw values (`MAL`, `FEMAL`, `O`, `N/A`, etc.); high-cardinality `Drug_Name` one-hot encoding inflated column count. Recommend consolidating before modeling.

---

## 🧬 Step 3 — Feature Engineering
7 new clinical features derived from cleaned data:

| Feature | Clinical Logic |
|---|---|
| `kidney_stage` | eGFR-based staging (Normal/Mild/Moderate/Severe) |
| `liver_risk` | Flag if ALT or AST > 40 |
| `polypharmacy` | Flag if ≥5 concurrent medications |
| `bmi_category` | Underweight/Normal/Overweight/Obese |
| `age_group` | Pediatric → Elderly bands |
| `elderly_high_dose` | Age > 65 **and** above-median dosage |
| `de_ritis_ratio` | AST/ALT ratio (liver disease indicator) |

**Final output:** **`data_engineered.csv` → 972,551 rows × 560 columns**

---

## ✅ Pipeline Status
| Step | Status | Runtime Notes |
|---|---|---|
| 1. EDA | ✅ Complete | No errors |
| 2. Cleaning | ✅ Complete | Minor deprecation warnings only |
| 3. Feature Engineering | ✅ Complete | Performance warnings (fragmentation) only, no data loss |

**➡️ Next Step:** Step 4 — Model Training & Evaluation on `data_engineered.csv`
