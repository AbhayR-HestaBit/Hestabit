import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report
from src.utils.logger import setup_logger

logger = setup_logger("error_analysis")
BASE_PATH = Path("src")
EVAL_DIR = BASE_PATH / "evaluation"
EVAL_DIR.mkdir(exist_ok=True, parents=True)

# identifies model failures and patterns
def run_error_analysis():
    model = joblib.load(BASE_PATH / "models" / "best_model.pkl")
    pipeline = joblib.load(BASE_PATH / "models" / "feature_pipeline.pkl")
    with open(BASE_PATH / "features" / "feature_list.json") as f: selected_features = json.load(f)
    with open(BASE_PATH / "evaluation" / "metrics.json") as f: metrics = json.load(f)

    model_key = next((v for k, v in {"LogisticRegression": "LogisticRegression", "RandomForestClassifier": "RandomForest", "XGBClassifier": "XGBoost", "LGBMClassifier": "LightGBM", "MLPClassifier": "NeuralNetwork"}.items() if k == type(model).__name__), type(model).__name__)
    thresh = metrics.get(model_key, {}).get("optimal_threshold", 0.5)

    df = pd.read_csv(BASE_PATH / "data" / "processed" / "test.csv")
    X_raw, y_true = df.drop(columns=["placement_status"]), df["placement_status"]
    X_df = pd.DataFrame(pipeline.transform(X_raw), columns=pipeline.named_steps["preprocessing"].get_feature_names_out())
    X_final = X_df[[f for f in selected_features if f in X_df.columns]]

    y_prob = model.predict_proba(X_final)[:, 1]
    y_pred = (y_prob >= thresh).astype(int)

    results = X_raw.copy(); results["actual"], results["predicted"], results["is_error"] = y_true, y_pred, y_true != y_pred
    error_df, correct_df = results[results["is_error"]], results[~results["is_error"]]

    # calculates distribution difference for errors
    stats = []
    for col in X_raw.select_dtypes(include=[np.number]).columns:
        stats.append({"feature": col, "diff": error_df[col].mean() - results[col].mean(), "abs_diff": abs(error_df[col].mean() - results[col].mean()), "error_mean": error_df[col].mean(), "overall_mean": results[col].mean()})
    pd.DataFrame(stats).sort_values("abs_diff", ascending=False).to_csv(EVAL_DIR / "error_patterns.csv", index=False)

    # generates error metrics and plots
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.heatmap(confusion_matrix(y_true, y_pred), annot=True, fmt="d", cmap="Blues", xticklabels=["Not Placed", "Placed"], yticklabels=["Not Placed", "Placed"], ax=axes[0])
    axes[0].set_title(f"Error Heatmap (Threshold={thresh:.2f})")

    top = pd.DataFrame(stats).sort_values("abs_diff", ascending=False).head(10)
    axes[1].barh(top["feature"], top["diff"], color=["#e74c3c" if d > 0 else "#2ecc71" for d in top["diff"]])
    axes[1].axvline(0, color="black", linestyle="--"); axes[1].set_title("Feature Bias in Error Cases"); axes[1].invert_yaxis()
    plt.tight_layout(); plt.savefig(EVAL_DIR / "error_heatmap.png"); plt.close()

    with open(EVAL_DIR / "error_analysis_report.txt", "w") as f:
        f.write(f"Errors: {results['is_error'].sum()}/{len(results)}\n")
        f.write(classification_report(y_true, y_pred, target_names=["Not Placed", "Placed"]))

if __name__ == "__main__":
    run_error_analysis()
