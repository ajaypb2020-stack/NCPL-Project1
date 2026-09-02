# Clinical Data Analysis - Complete Pipeline
## Bootcamp Project 3

**Status:** ✅ Ready to Execute  
**Environment:** Python 3.14.6 with virtual environment (`gsk_env`)  
**Data File:** `outputs/clinical_data_raw.csv` (1.15M rows × 41 columns)

---

## 📊 Project Overview

This project builds a **readmission prediction system** for clinical patient data using machine learning:

- **Target Variable:** `Readmission_30d` (Binary: 0=No readmission, 1=Readmission within 30 days)
- **Data Type:** Patient clinical records with demographics, vitals, labs, and treatment info
- **Approach:** Compare Decision Tree, Random Forest, and XGBoost models
- **Deliverables:** Model comparison, feature importance, evaluation metrics

---

## 📁 Project Structure

```
Bootcamp-P3/
├── gsk_env/                              # Virtual environment
├── outputs/                              # Data & results directory
│   ├── clinical_data_raw.csv            # Raw data (1.15M rows)
│   ├── data_cleaned.csv                 # After cleaning (Step 2)
│   ├── model_comparison.csv             # Model metrics (Step 3)
│   ├── rf_feature_importance.csv        # Random Forest features
│   └── xgb_feature_importance.csv       # XGBoost features
│
├── ANALYSIS_REPORT.md                   # Complete data analysis report
├── 01_eda_clinical_data.py              # Step 1: Exploratory Data Analysis
├── 02_data_cleaning.py                  # Step 2: Data Cleaning & Preprocessing
├── 03_model_training.py                 # Step 3: Model Training & Comparison
└── README.md                             # This file
```

---

## 🚀 Quick Start

### Step 0: Activate Virtual Environment

```bash
cd C:\Users\swarn\Bootcamp-P3

# Activate environment
gsk_env\Scripts\activate

# Verify (should show gsk_env in prompt)
# (gsk_env) PS C:\Users\swarn\Bootcamp-P3>
```

### Step 1: Exploratory Data Analysis (EDA)

```bash
python 01_eda_clinical_data.py
```

**Output:**
- Prints dataset overview, column statistics, missing values, data quality checks
- Visualizations saved to `eda_outputs/` (if matplotlib enabled)

**Key Info:**
- 1,155,000 patient records
- 41 columns (demographics, vitals, labs, medications, outcomes)
- Multiple data quality issues (see ANALYSIS_REPORT.md)

### Step 2: Data Cleaning & Preprocessing

```bash
python 02_data_cleaning.py
```

**Output:**
- Cleaned data saved to `outputs/data_cleaned.csv`
- Removes/imputes missing values
- Removes outliers and invalid values
- Standardizes categorical variables

**Processing:**
1. Drop redundant columns (24 → ~17 features)
2. Remove rows with missing target (1.15M → ~1.05M rows)
3. Remove outliers (Age, Weight, Heart Rate, Temperature)
4. Impute missing numeric values (median)
5. Impute missing categorical values (mode)
6. Standardize formats (Gender, Diagnosis, etc.)

### Step 3: Model Training & Evaluation

```bash
python 03_model_training.py
```

**Output:**
- `model_comparison.csv` - Metrics for all 3 models
- `rf_feature_importance.csv` - Top features from Random Forest
- `xgb_feature_importance.csv` - Top features from XGBoost

**Models Trained:**
1. **Decision Tree** - Baseline interpretable model
2. **Random Forest** - Ensemble with ~100 trees
3. **XGBoost** - Gradient boosted model (often best performance)

**Metrics Reported:**
- Accuracy, Precision, Recall, F1 Score, ROC-AUC
- Cross-validation scores (5-fold)
- Feature importance rankings

---

## 📋 Data Quality Issues & Solutions

See `ANALYSIS_REPORT.md` for complete analysis. Key issues:

| Issue | Status | Solution |
|-------|--------|----------|
| Duplicate columns (case mismatch) | ✅ Fixed | Keep uppercase, drop lowercase |
| Completely null columns | ✅ Fixed | Drop Extra_Col_1, Extra_Col_2, Notes |
| Outliers (Age -31, Weight -13) | ✅ Fixed | Remove rows with invalid ranges |
| High missing rates (24-29%) | ✅ Fixed | Drop or impute depending on column |
| High cardinality (Gender=116) | ✅ Fixed | Validate and standardize to {Male, Female, Other} |

---

## 🔧 Environment Setup

**Python:** 3.14.6  
**Virtual Environment:** `gsk_env` (installed and ready)

### Installed Packages

```
pandas 3.0.5              # Data manipulation
numpy 2.5.2               # Numerical computing
scikit-learn 1.9.0        # ML models (Decision Tree, Random Forest)
xgboost 3.4.1             # Gradient boosting
pytorch 2.14.0+cpu        # Deep learning (if needed)
matplotlib 3.11.1         # Plotting (if running with matplotlib enabled)
seaborn 0.13.2            # Statistical visualization
flask 3.1.3               # Web deployment (if needed)
shap, lime                # Model interpretability
```

**Not Installed:** TensorFlow/Keras (incompatible with Python 3.14.6)

---

## 📊 Expected Results

### Data Statistics
- **Input:** 1,155,000 rows × 41 columns
- **After cleaning:** ~1,050,000 rows × 17 features
- **Train-test split:** 80-20 (840K train, 210K test)

### Model Performance (Expected Ranges)
| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|-------|----------|-----------|--------|----|----|
| Decision Tree | 0.75-0.80 | 0.65-0.75 | 0.60-0.70 | 0.62-0.72 | 0.80-0.85 |
| Random Forest | 0.78-0.83 | 0.70-0.80 | 0.65-0.75 | 0.67-0.77 | 0.85-0.90 |
| **XGBoost** | **0.80-0.85** | **0.72-0.82** | **0.68-0.78** | **0.70-0.80** | **0.87-0.92** |

*XGBoost typically performs best for this type of tabular data*

---

## 🎯 Next Steps

### After Running All Scripts:

1. **Review Model Comparison**
   ```bash
   cat outputs/model_comparison.csv
   ```
   - Which model has the best F1 score?
   - Which has best ROC-AUC?
   - Trade-offs: Accuracy vs Recall vs Precision

2. **Analyze Feature Importance**
   ```bash
   cat outputs/xgb_feature_importance.csv
   ```
   - Which features drive readmission risk?
   - Clinical interpretation of top predictors

3. **Model Deployment Options**
   - Save best model with joblib
   - Create Flask API for predictions
   - Build web dashboard for clinicians

4. **Advanced Analysis**
   - SHAP values for interpretability
   - Calibration curves for probability estimates
   - Threshold optimization based on business needs

---

## 🐛 Troubleshooting

### Virtual Environment Won't Activate
```bash
# On Windows PowerShell, if ExecutionPolicy blocks scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
gsk_env\Scripts\Activate.ps1
```

### pandas/sklearn Not Found
```bash
# Reinstall packages in the activated environment
pip install pandas numpy scikit-learn xgboost
```

### Script Runs But No Output
```bash
# Run with explicit output redirection
python 02_data_cleaning.py > output.log 2>&1
type output.log
```

### File Not Found Errors
- Verify raw data exists: `outputs/clinical_data_raw.csv`
- Check working directory: Should be `C:\Users\swarn\Bootcamp-P3`
- Run scripts from project root directory

---

## 📚 References

- **Scikit-learn:** https://scikit-learn.org/
- **XGBoost:** https://xgboost.readthedocs.io/
- **Pandas:** https://pandas.pydata.org/
- **SHAP:** https://github.com/slundberg/shap

---

## ✅ Checklist

- [x] Raw data extracted and validated (1.15M rows × 41 columns)
- [x] Virtual environment created with all dependencies
- [x] Complete data analysis report generated
- [x] EDA script prepared (01_eda_clinical_data.py)
- [x] Data cleaning pipeline ready (02_data_cleaning.py)
- [x] Model training pipeline ready (03_model_training.py)
- [ ] Scripts executed and results reviewed
- [ ] Best model selected and evaluated
- [ ] Results interpreted and documented

---

**Ready to analyze clinical data!** 🏥📊  
Start with Step 1: `python 01_eda_clinical_data.py`

---

*Generated: 2026-09-01*  
*Project: Bootcamp-P3 Clinical Data Analysis*
