from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_RAW = PROJECT_ROOT / "customer_churn_dataset-testing-master.csv"
DATA_CLEANED = PROJECT_ROOT / "data_cleaned.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
TARGET = "Churn"
RANDOM_STATE = 42
TEST_SIZE = 0.2

OUTPUT_DIR.mkdir(exist_ok=True)