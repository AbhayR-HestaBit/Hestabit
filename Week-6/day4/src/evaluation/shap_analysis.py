import shap
import joblib
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# explains model predictions using shapley
class SHAPAnalyzer:
    def __init__(self):
        self.base_path = Path("src")
        self.model_path = self.base_path / "models"
        self.data_path = self.base_path / "data" / "processed"
        self.feature_path = self.base_path / "features"
        self.evaluation_path = self.base_path / "evaluation"
        self.evaluation_path.mkdir(exist_ok=True, parents=True)

    # fetches models and test data
    def load_resources(self):
        df = pd.read_csv(self.data_path / "test.csv")
        pipeline = joblib.load(self.model_path / "feature_pipeline.pkl")
        with open(self.feature_path / "feature_list.json", "r") as f:
            selected_features = json.load(f)
        model_file = self.model_path / "tuned_random_forest.pkl"
        if not model_file.exists(): model_file = self.model_path / "best_model.pkl"
        return df, pipeline, selected_features, joblib.load(model_file)

    # transforms data for shap explanation
    def prepare_data(self, df, pipeline, selected_features):
        X = df.drop(columns=["placement_status"]) if "placement_status" in df.columns else df
        X_df = pd.DataFrame(pipeline.transform(X), columns=pipeline.named_steps["preprocessing"].get_feature_names_out())
        return X_df[[f for f in selected_features if f in X_df.columns]]

    # generates and saves shap plots
    def run(self):
        df, pipeline, selected_features, model = self.load_resources()
        X_test = self.prepare_data(df, pipeline, selected_features)
        
        m_type = type(model).__name__
        try:
            if any(x in m_type for x in ["Forest", "XGB", "Tree"]):
                shap_v = shap.TreeExplainer(model).shap_values(X_test)
            elif any(x in m_type for x in ["Logistic", "Linear"]):
                shap_v = shap.LinearExplainer(model, X_test).shap_values(X_test)
            else:
                shap_v = shap.KernelExplainer(model.predict, X_test.iloc[:50]).shap_values(X_test.iloc[:50])
                X_test = X_test.iloc[:50]
        except:
            shap_v = shap.KernelExplainer(model.predict, X_test.iloc[:20]).shap_values(X_test.iloc[:20])
            X_test = X_test.iloc[:20]

        if isinstance(shap_v, list): shap_v = shap_v[1]
        elif len(shap_v.shape) > 2: shap_v = shap_v[:,:,1]

        plt.figure(figsize=(10, 6)); shap.summary_plot(shap_v, X_test, show=False); plt.tight_layout()
        plt.savefig(self.evaluation_path / "shap_summary.png"); plt.close()
        
        plt.figure(figsize=(10, 6)); shap.summary_plot(shap_v, X_test, plot_type="bar", show=False); plt.tight_layout()
        plt.savefig(self.evaluation_path / "shap_importance.png"); plt.close()

if __name__ == "__main__":
    SHAPAnalyzer().run()
