# Feature Engineering 

Implemented a custom `CustomFeatureGenerator` transformer to create new features.

### New Features Created:
1. academic_strength: `cgpa * aptitude_skill_rating`
2. discipline_score: `study_hours_per_day * attendance_percentage`
3. profile_strength: `certifications_count + projects_completed`
4. total_skills: `coding + communication + aptitude`
5. school_avg: `(10th % + 12th %) / 2`
6. cgpa_percentage: `cgpa * 9.5`
7. achievement_score: `(internships * 2) + projects + hackathons`
8. efficiency_score: `cgpa / (study_hours + 1)`
9. stress_to_sleep_ratio: `stress_level / (sleep_hours + 1)`
10. overall_rating: `(total_skills + achievement_score) / 2`

## Data Processing Pipeline
The final pipeline consists of:
1. Custom Feature Generation: Creates the 10 features above.
2. Log Transformation: Applied `np.log1p` to handle skewed numerical data.
3. Numerical Processing: `StandardScaler` for all numerical features.
4. Categorical Processing: `OneHotEncoder` for categorical variables.

## Feature Selection

1. Correlation Threshold: Removed features with correlation > 0.9 to reduce redundancy (collinearity).
2. Recursive Feature Elimination (RFE): Used a Random Forest estimator to recursively prune the least important features.
3. Mutual Information (MI): Measured non-linear dependencies.

### Top Features:

1. overall_rating (Derived)
2. achievement_score (Derived)
3. backlogs
4. total_skills (Derived)
5. coding_skill_rating
6. cgpa_percentage (Derived)
7. projects_completed
8. cgpa
9. twelfth_percentage
10. academic_strength (Derived)
11. profile_strength (Derived)
12. tenth_percentage
13. school_avg (Derived)
14. internships_completed
15. hackathons_participated

## Execution Flow

1. Pipeline Construction: Define transformers for scaling, encoding, and custom features.
2. Data Transformation: Apply the pipeline to raw data to create a numerically processed dataset.
3. Artifact Saving: Save the fitted pipeline as a pickle (`.pkl`) for future inference.
4. Collinearity Check: Automatically drop features with >0.9 correlation.
5. Recursive Selection: Use RFE to prune features down to the top 15 most predictive ones.
6. Feature Indexing: Export the final set of feature names to a JSON file.

## Folder Structure

`src/features/custom_transformers.py` : Contains the class for mathematical feature generation.
`src/features/build_features.py` : Assembles the `ColumnTransformer` and saves the pipeline.
`src/features/feature_selector.py` : Runs RFE and MI scoring to identify the final feature subset.

## Commands


```bash
python3 src/features/build_features.py

python3 src/features/feature_selector.py
```


