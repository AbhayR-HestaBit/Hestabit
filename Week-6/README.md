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

### DAY-1 DATA PIPELINE, EDA AND PROJECT ARCHITECTURE

- Data Loading
- Data Cleaning
- Outlier Detection (IQR Method)
- Dataset Versioning
- Train / Validation / Test Split
- Feature Scaling
- Logging System

