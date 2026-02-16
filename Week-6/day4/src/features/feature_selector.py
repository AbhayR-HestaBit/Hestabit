import json
import joblib
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.feature_selection import mutual_info_classif
from src.features.custom_transformers import CustomFeatureGenerator

# selects best features for model
class FeatureSelector:
    def __init__(self):
        self.base_path = Path("src")
        self.data_path = self.base_path / "data" / "processed"
        self.model_path = self.base_path / "models"
        self.logger = logging.getLogger("feature_selection")
        logging.basicConfig(level=logging.INFO)

    # fetches raw processed training data
    def load_data(self):
        train_df = pd.read_csv(self.data_path / "train.csv")
        possible_targets = ["placed", "target", "Placement_Status", "placement_status"]
        target_col = next((col for col in possible_targets if col in train_df.columns), None)
        if target_col is None:
            raise ValueError("Target column not found in train.csv")
        return train_df.drop(columns=[target_col]), train_df[target_col]

    # loads saved feature engineering pipeline
    def load_pipeline(self):
        return joblib.load(self.model_path / "feature_pipeline.pkl")

    # performs selection via mi and rfe
    def run(self):
        self.logger.info("FEATURE SELECTION STARTING")
        X, y = self.load_data()
        pipeline = self.load_pipeline()
        X_transformed = pipeline.transform(X)
        feature_names = pipeline.named_steps["preprocessing"].get_feature_names_out()

        corr_matrix = pd.DataFrame(X_transformed, columns=feature_names).corr().abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        to_drop = [column for column in upper.columns if any(upper[column] > 0.9)]
        
        keep_indices = [i for i, f in enumerate(feature_names) if f not in to_drop]
        X_filtered = X_transformed[:, keep_indices]
        filtered_names = feature_names[keep_indices]

        mi_scores = mutual_info_classif(X_filtered, y, random_state=42)
        
        from sklearn.feature_selection import RFE
        from sklearn.ensemble import RandomForestClassifier
        rfe_selector = RFE(estimator=RandomForestClassifier(n_jobs=-1, random_state=42), n_features_to_select=15, step=1)
        rfe_selector.fit(X_filtered, y)
        rfe_support = rfe_selector.support_
        
        rfe_selected_features = filtered_names[rfe_support]
        sorted_indices = np.argsort(mi_scores)[::-1]
        sorted_features = [filtered_names[i] for i in sorted_indices]
        sorted_scores = mi_scores[sorted_indices]

        plt.figure(figsize=(14, 6))
        plt.bar(range(len(sorted_features[:20])), sorted_scores[:20])
        plt.xticks(range(len(sorted_features[:20])), sorted_features[:20], rotation=45, ha='right')
        plt.xlabel("Feature Names")
        plt.ylabel("Mutual Information Score")
        plt.title("Mutual Information Feature Importance (Top 18)")
        plt.tight_layout()
        plt.savefig(self.base_path / "evaluation" / "feature_importance.png")
        plt.close()

        selected_features = list(rfe_selected_features)
        if len(selected_features) < 15:
            remaining = 15 - len(selected_features)
            for f in sorted_features:
                 if f not in selected_features and remaining > 0:
                     selected_features.append(f)
                     remaining -= 1

        selected_features = [str(x) for x in selected_features]
        with open(self.base_path / "features" / "feature_list.json", "w") as f:
            json.dump(selected_features, f, indent=4)

        self.logger.info("FEATURE SELECTION COMPLETE")

if __name__ == "__main__":
    selector = FeatureSelector()
    selector.run()
