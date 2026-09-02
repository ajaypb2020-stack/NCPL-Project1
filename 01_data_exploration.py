"""
Step 1 - Exploratory Data Analysis (EDA)
Loads raw CSV -> prints shape, dtypes, stats, missing values, class balance.
Saves distribution plots to outputs/.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from config import DATA_RAW, OUTPUT_DIR, TARGET
# Load the data
df = pd.read_csv(DATA_RAW)
print("=" * 60)
print("SHAPE:", df.shape)
print("=" * 60)
print("\nCOLUMN TYPES:")
print(df.dtypes)
print("\nFIRST 5 ROWS:")
print(df.head())
print("\nDESCRIPTIVE STATISTICS:")
print(df.describe())
print("\nMISSING VALUES:")
print(df.isnull().sum())
print(f"\nTARGET DISTRIBUTION ({TARGET}):")
print(df[TARGET].value_counts())
print(df[TARGET].value_counts(normalize=True).round(4))
# Get all numeric columns (except CustomerID)
numeric_cols = df.select_dtypes(include="number").columns.tolist()
numeric_cols = [c for c in numeric_cols if c != "CustomerID"]
# Plot histograms for all numeric columns
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
for ax, col in zip(axes.flatten(), numeric_cols):
	sns.histplot(df[col], kde=True, ax=ax)
	ax.set_title(col)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/numeric_distributions.png", dpi=150)
# Plot bar charts for categorical columns
cat_cols = df.select_dtypes(include="object").columns.tolist()
fig, axes = plt.subplots(1, len(cat_cols), figsize=(5 * len(cat_cols), 4))
if len(cat_cols) == 1:
	axes = [axes]
for ax, col in zip(axes, cat_cols):
	df[col].value_counts().plot.bar(ax=ax)
	ax.set_title(col)
	ax.tick_params(axis="x", rotation=45)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/categorical_distributions.png", dpi=150)
# Correlation heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(df[numeric_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Correlation Matrix")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/correlation_matrix.png", dpi=150)
print("EDA complete.")