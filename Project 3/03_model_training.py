"""
Step 3 - Feature Engineering & Model Training
Builds Decision Tree, Random Forest, and XGBoost models for readmission prediction.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("STEP 3: FEATURE ENGINEERING & MODEL TRAINING")
print("=" * 80)

# ---- Configuration ----
DATA_CLEANED = 'outputs/data_cleaned.csv'
OUTPUT_DIR = 'outputs'
TARGET = 'Readmission_30d'
RANDOM_STATE = 42
TEST_SIZE = 0.2

# ---- Load Cleaned Data ----
print(f"\nLoading cleaned data: {DATA_CLEANED}")
df = pd.read_csv(DATA_CLEANED)
print(f"✓ Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ---- Feature Engineering ----
print("\n" + "=" * 80)
print("FEATURE ENGINEERING")
print("=" * 80)

# Create age groups
print("\nCreating Age Groups:")
df['Age_Group'] = pd.cut(df['Age'], bins=[0, 30, 50, 70, 150], 
                          labels=['Young', 'Middle', 'Senior', 'Elderly'])
print(f"  Age_Group: {df['Age_Group'].nunique()} categories")

# Create BMI categories
print("Creating BMI Categories:")
df['BMI_Category'] = pd.cut(df['BMI'], bins=[0, 18.5, 25, 30, 100],
                             labels=['Underweight', 'Normal', 'Overweight', 'Obese'])
print(f"  BMI_Category: {df['BMI_Category'].nunique()} categories")

# Create hypertension flag
print("Creating Clinical Flags:")
df['Has_Hypertension'] = ((df['Systolic_BP'] >= 140) | (df['Diastolic_BP'] >= 90)).astype(int)
print(f"  Has_Hypertension: {df['Has_Hypertension'].sum():,} patients")

# Create lab abnormality flags
df['Abnormal_WBC'] = ((df['WBC_Count'] < 4.5) | (df['WBC_Count'] > 11)).astype(int)
df['Abnormal_Creatinine'] = (df['Creatinine'] > 1.2).astype(int)
df['Abnormal_ALT'] = (df['ALT_Enzyme'] > 40).astype(int)
print(f"  Abnormal_WBC: {df['Abnormal_WBC'].sum():,} patients")
print(f"  Abnormal_Creatinine: {df['Abnormal_Creatinine'].sum():,} patients")
print(f"  Abnormal_ALT: {df['Abnormal_ALT'].sum():,} patients")

# Encode categorical variables
print("\nEncoding Categorical Variables:")
label_encoders = {}
cat_cols = df.select_dtypes(include='object').columns.tolist()
if TARGET in cat_cols:
    cat_cols.remove(TARGET)

for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le
    print(f"  {col}: {len(le.classes_)} classes")

# Prepare features and target
print("\n" + "=" * 80)
print("DATA PREPARATION FOR MODELING")
print("=" * 80)

X = df.drop(columns=[TARGET])
y = df[TARGET].astype(int)

print(f"\nFeature Matrix: {X.shape}")
print(f"Target Distribution:")
print(y.value_counts())

# Train-Test Split
print(f"\nTrain-Test Split (80-20):")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)
print(f"  Train: {X_train.shape[0]:,} samples")
print(f"  Test: {X_test.shape[0]:,} samples")

# ---- Model Training ----
print("\n" + "=" * 80)
print("MODEL TRAINING")
print("=" * 80)

# Decision Tree
print("\n1. DECISION TREE")
print("-" * 40)
dt_model = DecisionTreeClassifier(
    max_depth=10, min_samples_split=20, min_samples_leaf=10,
    random_state=RANDOM_STATE
)
dt_model.fit(X_train, y_train)
dt_pred = dt_model.predict(X_test)
dt_prob = dt_model.predict_proba(X_test)[:, 1]

print(f"Accuracy:  {accuracy_score(y_test, dt_pred):.4f}")
print(f"Precision: {precision_score(y_test, dt_pred):.4f}")
print(f"Recall:    {recall_score(y_test, dt_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, dt_pred):.4f}")
print(f"ROC-AUC:   {roc_auc_score(y_test, dt_prob):.4f}")

# Cross-validation
dt_cv = cross_val_score(dt_model, X_train, y_train, cv=5, scoring='f1')
print(f"CV F1 Score: {dt_cv.mean():.4f} (+/- {dt_cv.std():.4f})")

# Random Forest
print("\n2. RANDOM FOREST")
print("-" * 40)
rf_model = RandomForestClassifier(
    n_estimators=100, max_depth=15, min_samples_split=20,
    min_samples_leaf=10, random_state=RANDOM_STATE, n_jobs=-1
)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_prob = rf_model.predict_proba(X_test)[:, 1]

print(f"Accuracy:  {accuracy_score(y_test, rf_pred):.4f}")
print(f"Precision: {precision_score(y_test, rf_pred):.4f}")
print(f"Recall:    {recall_score(y_test, rf_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, rf_pred):.4f}")
print(f"ROC-AUC:   {roc_auc_score(y_test, rf_prob):.4f}")

# Cross-validation
rf_cv = cross_val_score(rf_model, X_train, y_train, cv=5, scoring='f1')
print(f"CV F1 Score: {rf_cv.mean():.4f} (+/- {rf_cv.std():.4f})")

# XGBoost
print("\n3. XGBOOST")
print("-" * 40)
xgb_model = XGBClassifier(
    n_estimators=100, max_depth=8, learning_rate=0.1,
    subsample=0.8, colsample_bytree=0.8, random_state=RANDOM_STATE,
    verbosity=0
)
xgb_model.fit(X_train, y_train)
xgb_pred = xgb_model.predict(X_test)
xgb_prob = xgb_model.predict_proba(X_test)[:, 1]

print(f"Accuracy:  {accuracy_score(y_test, xgb_pred):.4f}")
print(f"Precision: {precision_score(y_test, xgb_pred):.4f}")
print(f"Recall:    {recall_score(y_test, xgb_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, xgb_pred):.4f}")
print(f"ROC-AUC:   {roc_auc_score(y_test, xgb_prob):.4f}")

# Cross-validation
xgb_cv = cross_val_score(xgb_model, X_train, y_train, cv=5, scoring='f1')
print(f"CV F1 Score: {xgb_cv.mean():.4f} (+/- {xgb_cv.std():.4f})")

# ---- Model Comparison ----
print("\n" + "=" * 80)
print("MODEL COMPARISON")
print("=" * 80)

comparison = pd.DataFrame({
    'Model': ['Decision Tree', 'Random Forest', 'XGBoost'],
    'Accuracy': [
        accuracy_score(y_test, dt_pred),
        accuracy_score(y_test, rf_pred),
        accuracy_score(y_test, xgb_pred)
    ],
    'Precision': [
        precision_score(y_test, dt_pred),
        precision_score(y_test, rf_pred),
        precision_score(y_test, xgb_pred)
    ],
    'Recall': [
        recall_score(y_test, dt_pred),
        recall_score(y_test, rf_pred),
        recall_score(y_test, xgb_pred)
    ],
    'F1 Score': [
        f1_score(y_test, dt_pred),
        f1_score(y_test, rf_pred),
        f1_score(y_test, xgb_pred)
    ],
    'ROC-AUC': [
        roc_auc_score(y_test, dt_prob),
        roc_auc_score(y_test, rf_prob),
        roc_auc_score(y_test, xgb_prob)
    ]
})

print("\n" + comparison.to_string(index=False))

# Save comparison
comparison.to_csv(f'{OUTPUT_DIR}/model_comparison.csv', index=False)
print(f"\n✓ Saved: {OUTPUT_DIR}/model_comparison.csv")

# Feature Importance
print("\n" + "=" * 80)
print("TOP 10 MOST IMPORTANT FEATURES")
print("=" * 80)

print("\nRandom Forest Feature Importance:")
rf_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False).head(10)
print(rf_importance.to_string(index=False))

print("\nXGBoost Feature Importance:")
xgb_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': xgb_model.feature_importances_
}).sort_values('Importance', ascending=False).head(10)
print(xgb_importance.to_string(index=False))

# Save feature importance
rf_importance.to_csv(f'{OUTPUT_DIR}/rf_feature_importance.csv', index=False)
xgb_importance.to_csv(f'{OUTPUT_DIR}/xgb_feature_importance.csv', index=False)

print("\n" + "=" * 80)
print("✓ MODEL TRAINING COMPLETE")
print("=" * 80)
print("\nOutputs saved to:")
print(f"  - {OUTPUT_DIR}/model_comparison.csv")
print(f"  - {OUTPUT_DIR}/rf_feature_importance.csv")
print(f"  - {OUTPUT_DIR}/xgb_feature_importance.csv")

# Best model recommendation
best_model_name = comparison.loc[comparison['F1 Score'].idxmax(), 'Model']
best_f1 = comparison['F1 Score'].max()
print(f"\n✓ BEST MODEL: {best_model_name} (F1 Score: {best_f1:.4f})")
