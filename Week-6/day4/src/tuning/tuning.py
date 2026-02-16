import optuna
import joblib
import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from src.utils.logger import setup_logger

logger = setup_logger("tuning")

# tunes random forest hyperparameters
class ModelTuner:
    def __init__(self):
        self.base_path = Path("src")
        self.data_path = self.base_path / "data" / "processed"
        self.model_path = self.base_path / "models"
        self.feature_path = self.base_path / "features"
        self.tuning_path = self.base_path / "tuning"
        self.tuning_path.mkdir(exist_ok=True, parents=True)

    # loads data and pipeline artifacts
    def load_data(self):
        train_df = pd.read_csv(self.data_path / "train.csv")
        pipeline = joblib.load(self.model_path / "feature_pipeline.pkl")
        with open(self.feature_path / "feature_list.json", "r") as f:
            selected_features = json.load(f)
        return train_df, pipeline, selected_features

    # transforms data for tuning process
    def prepare_data(self, df, pipeline, selected_features):
        target_col = "placement_status"
        X, y = df.drop(columns=[target_col]), df[target_col]
        X_df = pd.DataFrame(pipeline.transform(X), columns=pipeline.named_steps["preprocessing"].get_feature_names_out())
        return X_df[[f for f in selected_features if f in X_df.columns]], y

    # optuna trial evaluation function
    def objective(self, trial, X, y):
        clf = RandomForestClassifier(
            n_estimators=trial.suggest_int("n_estimators", 50, 300),
            max_depth=trial.suggest_int("max_depth", 5, 30),
            min_samples_split=trial.suggest_int("min_samples_split", 2, 20),
            min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 10),
            random_state=42, n_jobs=-1
        )
        return cross_val_score(clf, X, y, cv=3, scoring="f1").mean()

    # runs hyperparameter optimization study
    def run(self):
        train_df, pipeline, selected_features = self.load_data()
        X, y = self.prepare_data(train_df, pipeline, selected_features)
        
        study = optuna.create_study(direction="maximize")
        study.optimize(lambda trial: self.objective(trial, X, y), n_trials=20)
        
        results = {"best_score": study.best_trial.value, "best_params": study.best_trial.params, "n_trials": 20}
        with open(self.tuning_path / "results.json", "w") as f:
            json.dump(results, f, indent=4)
            
        best_rf = RandomForestClassifier(**study.best_trial.params, random_state=42)
        best_rf.fit(X, y)
        joblib.dump(best_rf, self.model_path / "tuned_random_forest.pkl")

if __name__ == "__main__":
    ModelTuner().run()
