
# Day 3: Model Building & Training

## Folder Structure
```text
src/
│
├── data/
│   └── processed/
│       ├── train.csv
│       ├── test.csv
│       └── val.csv
│
├── training/
│   └── train.py         
│
├── evaluation/
│   ├── metrics.json     
│   └── confusion_matrix_LogisticRegression.png
│
├── models/
│   ├── best_model.pkl   
│
├── features/
│   └── feature_list.json
│
└── utils/
```

## Tasks Completed
- Training Pipeline to handle data loading, model definition, training, and evaluation in one go.
- Trained 4 Models: Evaluated Logistic Regression (L2 Regularized), Random Forest, XGBoost, LightGBM And Neural Network.
- 5-Fold Cross-Validation Implemented.
- Evaluation Of Models.
- Model Comparison.

## Code Snippets

### Defining the Models (`src/training/train.py`)
```python
def get_models(self):
    
    lr = LogisticRegression(penalty='l2', C=1.0, random_state=42)
    
    
    rf = RandomForestClassifier(n_estimators=100)
    
    
    xgb = XGBClassifier(eval_metric='logloss')

    return {"LogisticRegression": lr, "RandomForest": rf, "XGBoost": xgb }
```
 
### 5-Fold Cross-Validation (`src/training/train.py`)
```python
def evaluate_model(self, model, X, y, cv=5):
    
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring='f1')
    return cv_scores.mean()
```

### Evaluation & Best Model Selection (`src/training/train.py`)
```python

if f1 > best_score:
    best_score = f1
    best_model_name = name
    best_model = model


joblib.dump(best_model, self.model_path / "best_model.pkl")
```

### Initial Evaluation Results
![Confusion Matrix](src/evaluation/confusion_matrix_LogisticRegression.png)
This confusion matrix shows the initial performance of the Logistic Regression model before threshold tuning.
