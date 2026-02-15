# WEEK-6 MACHINE LEARNING ENGINEERING

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
│
├── utils/
│   └── logger.py
│
├── logs/
│
├── features/
├── training/
├── evaluation/
├── deployment/
├── monitoring/
└── config/

```
## Tasks Completed

### DAY-1 DATA PIPELINE, EDA AND PROJECT ARCHITECTURE

- Data Loading
- Data Cleaning
- Outlier Detection (IQR Method)
- Dataset Versioning
- Train / Validation / Test Split
- Feature Scaling
- Logging System

### Day 2: Feature Engineering & Selection

- Built Processing Pipeline for Log Transformation, numeric Scaling, Categorical Encoding.
- Feature Selection
- Correlation Filter For Removing redundant features.

### Day 3: Model Building & Training

- Training Pipeline to handle data loading, model definition, training, and evaluation in one go.
- Trained 4 Models: Evaluated Logistic Regression (L2 Regularized), Random Forest, XGBoost, LightGBM And Neural Network.
- 5-Fold Cross-Validation Implemented.
- Evaluation Of Models.
- Model Comparison.
