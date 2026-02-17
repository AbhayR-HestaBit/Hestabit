import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from src.utils.logger import setup_logger

logger = setup_logger("drift_checker")
BASE = Path("src")
TRAIN_P = BASE / "data" / "processed" / "train.csv"
LOG_P = Path("prediction_logs.csv")
REPORT_P = BASE / "monitoring" / "drift_report.json"
THRESH = 0.05

# checks data distribution shift over time
class DriftChecker:
    # loads reference and incoming data
    def load_data(self):
        if not TRAIN_P.exists() or not LOG_P.exists(): return False
        self.train = pd.read_csv(TRAIN_P).drop(columns=["placement_status"], errors="ignore")
        self.pred = pd.read_csv(LOG_P)
        meta = ["request_id", "timestamp", "model_version", "threshold_used", "probability", "prediction", "risk_category", "prob", "pred", "risk"]
        self.pred = self.pred[[c for c in self.pred.columns if c not in meta]]
        cols = [c for c in self.train.columns if c in self.pred.columns]
        self.train, self.pred = self.train[cols], self.pred[cols]
        self.nums = self.train.select_dtypes(include=[np.number]).columns.tolist()
        return True

    # executes statistical testing for drift
    def run(self):
        if not self.load_data(): return
        res, drifted = {}, []
        for c in self.nums:
            if len(self.pred[c]) < 5: continue
            ks, p = stats.ks_2samp(self.train[c].dropna(), self.pred[c].dropna())
            d = p < THRESH
            res[c] = {"ks_statistic": round(float(ks), 4), "p_value": round(float(p), 4), "drift_detected": d, "train_mean": round(float(self.train[c].mean()), 4), "incoming_mean": round(float(self.pred[c].mean()), 4)}
            if d: drifted.append(c)

        report = {"drift_detected": len(drifted) > 0, "drifted_features": drifted, "total_checked": len(res), "feature_details": res}
        REPORT_P.parent.mkdir(exist_ok=True, parents=True)
        with open(REPORT_P, "w") as f: json.dump(report, f, indent=4)

if __name__ == "__main__":
    DriftChecker().run()