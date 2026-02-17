import joblib
import pandas as pd
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
import numpy as np
from src.features.custom_transformers import CustomFeatureGenerator
from src.utils.logger import setup_logger

logger = setup_logger("feature_engineering")

# handles feature engineering pipeline setup
class FeatureBuilder:
    def __init__(self):
        self.data_path = Path("src/data/processed")
        self.model_path = Path("src/models")
        self.model_path.mkdir(exist_ok=True)

    # loads processed csv files
    def load_data(self):
        train = pd.read_csv(self.data_path / "train.csv")
        val = pd.read_csv(self.data_path / "val.csv")
        test = pd.read_csv(self.data_path / "test.csv")
        return train, val, test

    # creates preprocessing and scaling pipeline
    def build_pipeline(self, X):
        numeric_features = list(X.select_dtypes(include=["int64", "float64"]).columns)
        categorical_features = list(X.select_dtypes(include=["object"]).columns)
        
        numeric_features.extend([
            "academic_strength", "discipline_score", "profile_strength",
            "total_skills", "school_avg", "cgpa_percentage",
            "achievement_score", "efficiency_score", "stress_to_sleep_ratio",
            "overall_rating"
        ])

        numeric_pipeline = Pipeline([
            ("log", FunctionTransformer(np.log1p, validate=False, feature_names_out="one-to-one")),
            ("scaler", StandardScaler())
        ])

        categorical_pipeline = Pipeline([
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ])

        preprocessor = ColumnTransformer([
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features)
        ])

        return Pipeline([
            ("feature_generation", CustomFeatureGenerator()),
            ("preprocessing", preprocessor)
        ])

    # executes training and artifact saving
    def run(self):
        logger.info("FEATURE ENGINEERING STARTING")
        train, val, test = self.load_data()

        y_train = train["placement_status"]
        y_val = val["placement_status"]
        y_test = test["placement_status"]

        X_train = train.drop("placement_status", axis=1)
        X_val = val.drop("placement_status", axis=1)
        X_test = test.drop("placement_status", axis=1)

        pipeline = self.build_pipeline(X_train)
        X_train_transformed = pipeline.fit_transform(X_train, y_train)
        X_val_transformed = pipeline.transform(X_val)
        X_test_transformed = pipeline.transform(X_test)

        joblib.dump(pipeline, self.model_path / "feature_pipeline.pkl")
        logger.info("Saved feature_pipeline.pkl")
        logger.info("FEATURE ENGINEERING COMPLETE")

        return (
            X_train_transformed,
            X_val_transformed,
            X_test_transformed,
            y_train,
            y_val,
            y_test,
        )

if __name__ == "__main__":
    builder = FeatureBuilder()
    builder.run()
