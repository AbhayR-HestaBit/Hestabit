# Model Interpretation 

## Hyperparameter Tuning

Used Optuna to tune the hyperparameters of our Random Forest model.

### Best Parameters Found:
- n_estimators: 67 (Number of trees)
- max_depth: 17 (Max depth of each tree)
- min_samples_split: 8
- min_samples_leaf: 4

### Performance:
- Tuned F1 Score: ~0.937
- Baseline Random Forest F1: ~0.939
- Logistic Regression F1: ~0.941

Observation: Logistic Regression remains best, which means data is linear. Here Tuned Random Forest is used as it is more robust to overfitting due to the `min_samples_leaf` constraints.

## SHAP Analysis

Used SHAP (SHapley Additive exPlanations) to understand the models predictions.

### Key Drivers:
Based on the SHAP summary plot (`src/evaluation/shap_summary.png`), the most influential features are:

1. overall_rating / cgpa: High values push the prediction towards "Placed".
2. backlogs: The presence of backlogs has a strong negative impact.
3. internships_completed: Practical experience is a positive driver.

## Error Analysis

Analyzing the confusion matrices from Day 3:
- False Positives (Type I Error): Predicting "Placed" when the student was NOT placed.
    - *Cause*: High CGPA but perhaps low aptitude/coding scores (though `overall_rating` tries to capture this).
- False Negatives (Type II Error): Predicting "Not Placed" when the student WAS placed.
    - *Cause*: Low abstract scores but maybe high specific skills (like hackathons) that the model weighed less.

## Conclusion
While the Tuned Random Forest is a strong, explainable model, But prefering Logistic Regression for its simplicity, speed, and slightly higher accuracy on this specific dataset.

### SHAP Analysis Results
![SHAP Summary](src/evaluation/shap_summary.png)
Shows how high and low values of each feature influence the model's placement predictions.
