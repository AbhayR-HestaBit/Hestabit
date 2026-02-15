# Model Comparison Report

Best Model: LogisticRegression

## Performance Metrics

| Model | CV F1 | Test Accuracy | Test Precision | Test Recall | Test F1 | ROC AUC |
|-------|-------|---------------|----------------|-------------|---------|---------|
| LogisticRegression | 0.9387 | 0.7653 | 0.9151 | 0.9690 | 0.9413 | 0.9007 |
| RandomForest | 0.9348 | 0.8920 | 0.9123 | 0.9674 | 0.9391 | 0.8960 |
| XGBoost | 0.9299 | 0.8907 | 0.9195 | 0.9566 | 0.9377 | 0.8759 |
| LightGBM | 0.9313 | 0.8853 | 0.9153 | 0.9550 | 0.9347 | 0.8843 |
| NeuralNetwork | 0.9359 | 0.8893 | 0.9157 | 0.9597 | 0.9372 | 0.8897 |

## Evaluation Plots
Confusion matrice for Logistic Regression model is saved in `src/evaluation/`.

## Model Configurations
- Logistic Regression: Standard L2 regularization, `C=1.0`.
- Random Forest: Ensemble of 100 decision trees.
- XGBoost: Gradient boosted trees with logloss evaluation.
- LightGBM: Fast gradient boosting for large-scale data.
- Neural Network: Multi-layer Perceptron (MLP) with early stopping.

## Evaluation Method
We used 5-Fold Cross-Validation to make sure the results are stable across different data splits. After that, we performed a final check on a separate test set to calculate accuracy and F1-score.

## Final Choice & Logic
Chosen Logistic Regression as model. 

*   As it achieved highest F1 score (94%) while staying extremely lightweight. 
*   Minimal Overfitting: The gap between cross-validation and test scores is almost zero.
*   Fit for Data: Since placement mostly depends on objective metrics like CGPA and Skills, a linear model works better and faster than complex ensembles.

### Initial Evaluation Results
![Confusion Matrix](src/evaluation/confusion_matrix_LogisticRegression.png)
This confusion matrix shows the initial performance of the Logistic Regression model before threshold tuning.
