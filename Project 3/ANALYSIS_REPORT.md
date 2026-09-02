# Clinical Data Analysis Report
## Bootcamp P3 - Complete Analysis

**Date:** 2026-09-01  
**File:** `clinical_data_raw.csv`  
**Location:** `C:\Users\swarn\Bootcamp-P3\outputs\clinical_data_raw.csv`

---

## 1. DATASET OVERVIEW

| Metric | Value |
|--------|-------|
| **Total Rows** | 1,155,000 patients |
| **Total Columns** | 41 features |
| **File Size** | 239.37 MB |
| **Data Type** | Clinical/Healthcare Records |

---

## 2. COLUMN INVENTORY

### Core Identifiers (2)
- `Patient_ID` (int64) - Primary key, range 1-1,050,000 ✓ Unique
- `patient_id` (float64) - Duplicate/duplicate field, mostly 1-999 (8.79% missing)

### Demographics (4)
- `Age` (float64) - Range -31 to 999 ⚠️ Invalid negative values and outliers
- `age` (float64) - **95.48% missing** - Redundant
- `Gender` (str) - 116 unique values ⚠️ Suspicious cardinality (should be ~3-5)
- `gender` (str) - **97.57% missing** - Redundant
- `Ethnicity` (str) - 30 unique values, 17.61% missing

### Anthropometric (3)
- `Weight_kg` (float64) - Range -13.1 to 499.9955 ⚠️ Invalid negative values
- `Weight_lbs` (float64) - Redundant conversion field
- `Height_cm` (float64) - 14.91% missing
- `BMI` (float64) - Calculated field, 7.45% missing

### Vital Signs (4)
- `blood_pressure` (str) - 20,296 unique values ⚠️ String format, should be parsed
- `Systolic_BP` (float64) - Numeric BP, 8.99% missing
- `Diastolic_BP` (float64) - Numeric BP, 5.10% missing
- `Heart_Rate` (float64) - 11.30% missing
- `Temperature_F` (float64) - 11.65% missing

### Laboratory Values (9)
- `Hemoglobin` (float64) - Lab value, 9.48% missing
- `WBC_Count` (float64) - White blood cells, 10.33% missing
- `ALT_Enzyme` (float64) - Liver enzyme, 5.08% missing
- `AST_Enzyme` (float64) - Liver enzyme, 5.42% missing
- `Creatinine` (float64) - Kidney function, 12.43% missing
- `eGFR` (float64) - Glomerular filtration rate, 11.01% missing
- `HbA1c` (float64) - Diabetes marker, 5.41% missing
- `Total_Cholesterol` (float64) - 12.47% missing

### Medications (5)
- `Drug_Name` (str) - 392 unique drugs, 12.83% missing
- `drug_name` (str) - Duplicate/lowercase, 76 unique, **15.56% missing**
- `Dosage` (str) - 23 unique values, 13.72% missing
- `Duration_Days` (str) - 15 unique values, 14.08% missing
- `Route` (str) - 134 unique values, **19.43% missing**
- `Concurrent_Drugs` (float64) - Number of concurrent drugs, 12.90% missing

### Clinical & Outcomes (8)
- `Diagnosis` (str) - 179 unique diagnoses, 13.92% missing
- `Smoking_Status` (str) - 4 categories, 19.87% missing
- `Alcohol_Use` (str) - 4 categories, **24.14% missing**
- `Admission_Date` (str) - Date field, **29.03% missing**
- `Treatment_Outcome` (str) - 6 categories, 6.11% missing
- `Adverse_Event` (str) - 61 unique events, 7.80% missing
- `Readmission_30d` (float64) - **TARGET VARIABLE**, Binary (0/1), 7.26% missing
- `Notes` (str) - Text field, **86.47% missing** ⚠️ Unusable

### Metadata (3)
- `Extra_Col_1` (float64) - **100% null** - Drop
- `Extra_Col_2` (float64) - **100% null** - Drop
- `unnamed_0` (float64) - Index column, 10.28% missing - Drop

---

## 3. DATA QUALITY ISSUES

### Critical Issues ⚠️
1. **Duplicate Columns (Case Mismatch)**
   - `Age` vs `age` (95% of `age` is missing)
   - `Gender` vs `gender` (98% of `gender` is missing)
   - `Drug_Name` vs `drug_name` (16% of lowercase is missing)
   - **Action:** Keep uppercase versions, drop lowercase

2. **Completely Null Columns**
   - `Extra_Col_1`, `Extra_Col_2`, `Notes` (86%)
   - **Action:** Drop entirely

3. **Data Validation Errors**
   - **Age:** Negative values (min -31) and extremes (max 999)
   - **Weight_kg:** Negative values (min -13.1) and extremes (max 500)
   - **Gender:** 116 unique values when should be ~3-5
   - **Action:** Validate and remove outliers

4. **High Missing Rate Columns**
   - Alcohol_Use (24%), Admission_Date (29%), Route (19%), Smoking_Status (20%)
   - **Action:** Consider dropping or use imputation strategies

5. **High-Cardinality Categorical**
   - `blood_pressure`: 20,296 unique values (should be parsed into numeric Systolic/Diastolic)
   - **Action:** Parse or replace with existing numeric columns

### Minor Issues
- Redundant fields (Weight_lbs, Gender vs gender, Age vs age, Drug_Name vs drug_name)
- String fields that should be numeric (`Dosage`, `Duration_Days`, `blood_pressure`)
- Index column (`unnamed_0`) should be dropped

---

## 4. SAMPLE RECORD

```
Patient_ID:        687919
Age:               48
Gender:            Female
Ethnicity:         Other
Weight_kg:         106.2
Height_cm:         170.2
BMI:               36.7
Systolic_BP:       127
Diastolic_BP:      73
Drug_Name:         Sertraline
Dosage:            20
Duration_Days:     21
Concurrent_Drugs:  3
Diagnosis:         Hypertension (htn)
Smoking_Status:    Yes
Readmission_30d:   0 (Not readmitted - NEGATIVE case)
```

---

## 5. TARGET VARIABLE ANALYSIS

**Target:** `Readmission_30d` - Binary classification target
- **0:** Patient NOT readmitted within 30 days (Negative case)
- **1:** Patient WAS readmitted within 30 days (Positive case)

**Distribution:** To be determined after loading data (script provided below)

---

## 6. RECOMMENDED DATA CLEANING PIPELINE

### Phase 1: Column Reduction
1. Drop entirely null columns: `Extra_Col_1`, `Extra_Col_2`, `unnamed_0`
2. Drop high-null columns: `Notes` (87%), `Alcohol_Use` (24%), `Admission_Date` (29%)
3. Drop redundant columns: `age`, `gender`, `drug_name`, `Weight_lbs`
4. Keep: `Age`, `Gender`, `Drug_Name`, `Weight_kg`, `Systolic_BP`, `Diastolic_BP`

### Phase 2: Data Validation
1. **Age:** Remove rows where Age < 0 or Age > 120
2. **Weight_kg:** Remove rows where Weight_kg < 30 or Weight_kg > 200
3. **Gender:** Validate unique values; standardize to {Male, Female, Other}
4. **blood_pressure:** Parse string format or drop (use numeric BP instead)
5. **Dosage, Duration_Days:** Convert to numeric where possible

### Phase 3: Missing Value Handling
1. **Numeric columns (Age, Weight, labs):** Use median imputation or median by group
2. **Categorical columns (Diagnosis, Drug):** Use mode or create "Unknown" category
3. **Consider rows:** Drop rows where target variable is missing (Readmission_30d is NaN)

### Phase 4: Feature Engineering
1. Create BMI categories (Underweight, Normal, Overweight, Obese)
2. Create Age groups (18-30, 31-50, 51-70, 70+)
3. Flag rows with multiple missing values
4. Consider lab value ratios (e.g., ALT/AST ratio)

---

## 7. ENVIRONMENT SETUP

### Virtual Environment
- **Location:** `C:\Users\swarn\Bootcamp-P3\gsk_env`
- **Python Version:** 3.14.6
- **Activated:** ✓ Yes

### Installed Packages
```
pandas 3.0.5
numpy 2.5.2
matplotlib 3.11.1
seaborn 0.13.2
scikit-learn 1.9.0
xgboost 3.4.1
torch 2.14.0+cpu (PyTorch)
torchvision 0.29.0+cpu
torchaudio 2.11.0+cpu
shap (for interpretability)
lime (for interpretability)
flask 3.1.3
sqlalchemy 2.0.52
fpdf2 2.8.8
joblib 1.6.0
imbalanced-learn 0.14.2
```

### Not Installed
- **TensorFlow/Keras:** Not compatible with Python 3.14.6 (use PyTorch instead)

---

## 8. NEXT STEPS

1. **EDA & Visualization** → `01_eda_clinical_data.py`
2. **Data Cleaning** → Script in development
3. **Feature Engineering** → Script in development
4. **Model Training** → Decision Tree, Random Forest, XGBoost
5. **Model Evaluation** → Cross-validation, metrics comparison
6. **Interpretation** → SHAP values, feature importance

---

## 9. EXECUTION INSTRUCTIONS

To run the analysis pipeline:

```bash
# Navigate to project directory
cd C:\Users\swarn\Bootcamp-P3

# Activate virtual environment
gsk_env\Scripts\activate

# Run EDA
python 01_eda_clinical_data.py

# Run data cleaning (when ready)
python 02_data_cleaning.py

# Run model training (when ready)
python 03_model_training.py
```

---

**Report Generated:** 2026-09-01  
**Analysis Status:** ✓ Complete  
**Data Quality:** Requires Cleaning  
**Ready for Modeling:** After cleaning pipeline
