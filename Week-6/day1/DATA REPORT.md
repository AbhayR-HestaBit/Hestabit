# DATA-REPORT

## Folder Structure

```text
src/
 ├── data/
 │   ├── raw/
 │   ├── processed/
 │   └── external/
 ├── notebooks/
 ├── features/
 ├── pipelines/
 ├── models/
 ├── training/
 ├── evaluation/
 ├── deployment/
 ├── monitoring/
 ├── logs/
 ├── utils/
 └── config/
```
## About structure

```text
raw/ → Immutable original datasets

processed/ → Cleaned & versioned datasets

pipelines/ → Reusable data processing logic

notebooks/ → EDA exploration only (no production logic)

logs/ → Structured logging

models/ → Saved trained models
```


## Data Flow Architecture


```text
Raw Data
   ↓
DataLoader
   ↓
Cleaning
   ↓
Outlier Detection
   ↓
Encoding
   ↓
Train/Validation/Test Split
   ↓
Scaling
   ↓
Versioned Processed Dataset
```

## Dataset Description

Two datasets were merged:

- indian_engineering_student_placement.csv

- placement_targets.csv


Final dataset contains:

- Academic metrics

- Skill indicators

- Extracurricular activity

- Placement status (Target)

Target Variable:

placement_status
Placed → 1
Not Placed → 0

## Data Cleaning Strategy
- Duplicate Handling
```python
df = df.drop_duplicates()
```

Reason: Avoid data leakage and skewed training.

- Missing Values Handling
```python
df['extracurricular_involvement'] = 
    df['extracurricular_involvement'].fillna('None')
```

- Target Encoding
```python
df['placement_status'] =  df['placement_status'].map({'Placed': 1, 'Not Placed': 0})
```

- Outlier Detection

Method Used: IQR (Interquartile Range)

```python
Q1 = df[col].quantile(0.25)
Q3 = df[col].quantile(0.75)
IQR = Q3 - Q1
```

- Outliers defined as:

Below Q1 - 1.5*IQR
Above Q3 + 1.5*IQR


## Data Splitting Strategy

We used a Train / Validation / Test split.

```python 
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)
```

Then:

```python X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
)
```


## Feature Scaling

applied:

StandardScaler

```python scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
```

Why?

Logistic regression & distance-based models require normalized features.

Prevents dominance of large-scale variables.



