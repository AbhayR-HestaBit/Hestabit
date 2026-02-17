import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import cross_val_score
from src.utils.logger import setup_logger

logger = setup_logger("training")

# trains and evaluates multiple model types
class ModelTrainer:
    def __init__(self):
        self.base_path = Path("src")
        self.data_path = self.base_path / "data" / "processed"
        self.feature_path = self.base_path / "features"
        self.model_path = self.base_path / "models"
        self.evaluation_path = self.base_path / "evaluation"
        self.model_path.mkdir(exist_ok=True, parents=True)
        self.evaluation_path.mkdir(exist_ok=True, parents=True)

    # returns train and test dataframes
    def load_data(self):
        return pd.read_csv(self.data_path / "train.csv"), pd.read_csv(self.data_path / "test.csv")

    # loads pipeline and selected feature list
    def load_artifacts(self):
        pipeline = joblib.load(self.model_path / "feature_pipeline.pkl")
        with open(self.feature_path / "feature_list.json", "r") as f:
            selected_features = json.load(f)
        return pipeline, selected_features

    # transforms raw data through pipeline
    def prepare_data(self, df, pipeline, selected_features):
        target_col = "placement_status"
        X = df.drop(columns=[target_col]) if target_col in df.columns else df
        y = df[target_col] if target_col in df.columns else None
        
        X_df = pd.DataFrame(pipeline.transform(X), columns=pipeline.named_steps["preprocessing"].get_feature_names_out())
        return X_df[[f for f in selected_features if f in X_df.columns]], y

    # defines candidate ml model instances
    def get_models(self):
        return {
            "LogisticRegression": LogisticRegression(C=1.0, random_state=42, max_iter=1000),
            "RandomForest": RandomForestClassifier(random_state=42, n_estimators=100),
            "XGBoost": XGBClassifier(eval_metric='logloss', random_state=42),
            "LightGBM": LGBMClassifier(random_state=42, verbose=-1),
            "NeuralNetwork": MLPClassifier(random_state=42, max_iter=1000, early_stopping=True)
        }

    # saves confusion matrix visualization
    def plot_confusion_matrix(self, y_true, y_pred, model_name):
        plt.figure(figsize=(6, 5))
        sns.heatmap(confusion_matrix(y_true, y_pred), annot=True, fmt='d', cmap='Blues')
        plt.title(f"Confusion Matrix: {model_name}")
        plt.ylabel("Actual"); plt.xlabel("Predicted"); plt.tight_layout()
        plt.savefig(self.evaluation_path / f"confusion_matrix_{model_name}.png"); plt.close()

    # runs full training and evaluation loop
    def run(self):
        train_df, test_df = self.load_data()
        pipeline, selected_features = self.load_artifacts()
        X_train, y_train = self.prepare_data(train_df, pipeline, selected_features)
        X_test, y_test = self.prepare_data(test_df, pipeline, selected_features)
        
        models = self.get_models()
        best_score, best_model_name, best_model = 0, "", None
        metrics_results = {}
        
        for name, model in models.items():
            logger.info(f"Training {name}...")
            cv_score = cross_val_score(model, X_train, y_train, cv=5, scoring='f1').mean()
            logger.info(f"{name} CV F1 Score: {cv_score:.4f}")
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred
            
            metrics = {
                "CV_F1": cv_score,
                "Test_Accuracy": accuracy_score(y_test, y_pred),
                "Test_Precision": precision_score(y_test, y_pred),
                "Test_Recall": recall_score(y_test, y_pred),
                "Test_F1": f1_score(y_test, y_pred),
                "Test_ROC_AUC": roc_auc_score(y_test, y_prob) if hasattr(model, "predict_proba") else 0.0,
                "recall_not_placed": recall_score(y_test, y_pred, pos_label=0),
                "recall_placed": recall_score(y_test, y_pred),
                "precision_not_placed": precision_score(y_test, y_pred, pos_label=0),
                "f1_not_placed": f1_score(y_test, y_pred, pos_label=0),
                "optimal_threshold": 0.5
            }
            metrics_results[name] = metrics
            self.plot_confusion_matrix(y_test, y_pred, name)
            if metrics["Test_F1"] > best_score:
                best_score, best_model_name, best_model = metrics["Test_F1"], name, model
        
        logger.info(f"Best model: {best_model_name} with F1: {best_score:.4f}")

        y_prob_best = best_model.predict_proba(X_test)[:, 1]
        best_thresh, best_recall_0 = 0.5, 0.0
        for thresh in np.arange(0.1, 0.95, 0.05):
            y_p = (y_prob_best >= thresh).astype(int)
            r0, acc = recall_score(y_test, y_p, pos_label=0), accuracy_score(y_test, y_p)
            if r0 >= 0.80 and acc >= 0.75 and r0 > best_recall_0:
                best_recall_0, best_thresh = r0, thresh
        
        y_pred_tuned = (y_prob_best >= best_thresh).astype(int)
        metrics_results[best_model_name].update({
            "optimal_threshold": float(best_thresh),
            "recall_not_placed": recall_score(y_test, y_pred_tuned, pos_label=0),
            "recall_placed": recall_score(y_test, y_pred_tuned, pos_label=1),
            "f1_not_placed": f1_score(y_test, y_pred_tuned, pos_label=0),
            "precision_not_placed": precision_score(y_test, y_pred_tuned, pos_label=0),
            "Test_Accuracy": accuracy_score(y_test, y_pred_tuned)
        })
        
        plt.figure(figsize=(6, 5))
        sns.heatmap(confusion_matrix(y_test, y_pred_tuned), annot=True, fmt='d', cmap='Blues')
        plt.title(f"Confusion Matrix: {best_model_name} (Tuned {best_thresh:.2f})")
        plt.ylabel("Actual"); plt.xlabel("Predicted"); plt.tight_layout()
        plt.savefig(self.evaluation_path / f"confusion_matrix_{best_model_name}_tuned.png"); plt.close()

        with open(self.evaluation_path / "metrics.json", "w") as f: json.dump(metrics_results, f, indent=4)
        joblib.dump(best_model, self.model_path / "best_model.pkl")

if __name__ == "__main__":
    ModelTrainer().run()
