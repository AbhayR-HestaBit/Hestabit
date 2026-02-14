# DAY-1 DATA PIPELINE, EDA AND PROJECT ARCHITECTURE

## Folder Structure

```text
src/
│
├── data/
│   ├── raw/
│   │   ├── indian_engineering_student_placement.csv
│   │   └── placement_targets.csv
│   │
│   ├── processed/
│   │   ├── final_<hash>.csv
│   │   ├── train.csv
│   │   ├── val.csv
│   │   └── test.csv
│   │
│   └── external/
│
├── notebooks/
│   └── EDA.ipynb
│
├── pipelines/
│   ├── data_loader.py
│   └── data_pipeline.py
│
├── models/
│   └── scaler.pkl
│
├── utils/
│   └── logger.py
│
├── logs/
│   └── data_pipeline_*.log
│
├── features/
├── training/
├── evaluation/
├── deployment/
├── monitoring/
└── config/

```
## Tasks Completed

- Data Loading
- Data Cleaning
- Outlier Detection (IQR Method)
- Dataset Versioning
- Train / Validation / Test Split
- Feature Scaling
- Logging System

## Code Snippets

- Data Loading
```python
class DataLoader:
    def __init__(self, raw_path: str):
        self.raw_path = Path(raw_path)

    def load(self):
        students = pd.read_csv(self.raw_path / "indian_engineering_student_placement.csv")
        placement = pd.read_csv(self.raw_path / "placement_targets.csv")
        df = students.merge(placement, on="Student_ID")
        return df
```
- Data Cleaning
```python
df = df.drop_duplicates()

df["extracurricular_involvement"] = \
    df["extracurricular_involvement"].fillna("None")

df["placement_status"] = \
    df["placement_status"].map({"Placed": 1, "Not Placed": 0})

```

- Outlier Detection (IQR Method)
```python
Q1 = df[col].quantile(0.25)
Q3 = df[col].quantile(0.75)
IQR = Q3 - Q1

```
Outliers defined as:

Below Q1 - 1.5 * IQR
Above Q3 + 1.5 * IQR


- Dataset Versioning

```python
Implemented hash-based dataset fingerprinting:

hash_id = hashlib.md5(
    pd.util.hash_pandas_object(df).values
).hexdigest()

filename = f"final_{hash_id}.csv"
```

- Train / Validation / Test Split
```python
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
)
```

- Final ratio:

70% Train

15% Validation

15% Test

- Feature Scaling

Used StandardScaler:

```python
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)


Saved scaler artifact:

joblib.dump(scaler, "src/models/scaler.pkl")
```

- Logging System

Custom logger used:
```python
logger = setup_logger("data_pipeline")
logger.info("DATA PIPELINE STARTING")
```
