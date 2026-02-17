# WEEK-6 MACHINE LEARNING ENGINEERING

## Folder Structure

```text
src/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── notebooks/
│
├── pipelines/
│
├── models/
│
├── utils/
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
## Working

Current Dataset is of indian_engineering_student_placement.csv, containing student stats and placement_targets.csv which contains placement status of subsequent students.

The model build in this week focuses over prediction of those student who are at risk and need counseling for placements based on their current stats.


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

### Day 4: Hyperparameter Tuning, Explainability AND Error Analysis

- Hyperparameter tuning with Optuna.
- SHAP analysis: generated summary plot and global importance bar chart.
- Feature importance chart regenerated with proper feature name labels.
- Error analysis: identified False Positives and False Negatives.
- Bias/variance analysis: found which features differ most in error cases.

### Day 5: Model Deployment And Monitoring

- FastAPI `/predict` endpoint
- Risk categorization: High Risk / Medium Risk / Low Risk.
- Dockerfile for containerized deployment.
