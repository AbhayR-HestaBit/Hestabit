import os
import uuid
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from src.utils.logger import setup_logger

load_dotenv()
logger = setup_logger("api")
BASE_PATH = Path("src")
MODEL_PATH = BASE_PATH / "models" / "best_model.pkl"
PIPELINE_PATH = BASE_PATH / "models" / "feature_pipeline.pkl"
FEATURE_LIST_PATH = BASE_PATH / "features" / "feature_list.json"
METRICS_PATH = BASE_PATH / "evaluation" / "metrics.json"
PRED_LOG_PATH = Path("prediction_logs.csv")
VERSION = os.getenv("MODEL_VERSION", "1.0.0")

model = joblib.load(MODEL_PATH)
pipeline = joblib.load(PIPELINE_PATH)
with open(FEATURE_LIST_PATH) as f: selected_features = json.load(f)
with open(METRICS_PATH) as f: m_data = json.load(f)

m_key = next((v for k, v in {"LogisticRegression": "LogisticRegression", "RandomForestClassifier": "RandomForest", "XGBClassifier": "XGBoost", "LGBMClassifier": "LightGBM", "MLPClassifier": "NeuralNetwork"}.items() if k == type(model).__name__), type(model).__name__)
THRESH = m_data.get(m_key, {}).get("optimal_threshold", 0.5)

app = FastAPI(title="Placement Predictor API", version=VERSION)

# defines input schema for student data
class StudentInput(BaseModel):
    cgpa: float = Field(..., ge=0.0, le=10.0)
    tenth_percentage: float = Field(..., ge=0.0, le=100.0)
    twelfth_percentage: float = Field(..., ge=0.0, le=100.0)
    coding_skill_rating: float = Field(..., ge=0.0, le=10.0)
    communication_skill_rating: float = Field(..., ge=0.0, le=10.0)
    aptitude_skill_rating: float = Field(..., ge=0.0, le=10.0)
    internships_completed: int = Field(..., ge=0)
    projects_completed: int = Field(..., ge=0)
    certifications_count: int = Field(..., ge=0)
    hackathons_participated: int = Field(..., ge=0)
    study_hours_per_day: float = Field(..., ge=0.0, le=24.0)
    attendance_percentage: float = Field(..., ge=0.0, le=100.0)
    backlogs: int = Field(..., ge=0)
    stress_level: float = Field(..., ge=0.0, le=10.0)
    sleep_hours: float = Field(..., ge=0.0, le=24.0)
    gender: str = Field(...)
    stream: str = Field(...)

    @field_validator("gender")
    @classmethod
    def val_gender(cls, v):
        if v not in ("Male", "Female"): raise ValueError("Male or Female")
        return v

# determines priority based on probability
def get_risk(prob, t):
    if prob < t * 0.6: return "High Risk"
    return "Medium Risk" if prob < t else "Low Risk"

# provides counseling suggestions per data
def get_tips(risk, data):
    if risk == "High Risk":
        tips = []
        if data.get("backlogs", 0) > 0: tips.append("Clear backlogs.")
        if data.get("cgpa", 0) < 6.5: tips.append("Improve CGPA.")
        if data.get("internships_completed", 0) == 0: tips.append("Get internships.")
        return "High risk. " + " ".join(tips)
    return "Medium risk." if risk == "Medium Risk" else "Low risk."

# simple health check endpoint
@app.get("/health")
def health(): return {"status": "ok", "version": VERSION}

@app.get("/")
def root(): return {"status": "Running", "message": "Placement Predictor API", "docs": "http://localhost:8000/docs"}

# main inference and logging endpoint
@app.post("/predict")
async def predict(s: StudentInput):
    rid = str(uuid.uuid4())
    try:
        data_dict = s.model_dump()
        df = pd.DataFrame([data_dict])
        X_df = pd.DataFrame(pipeline.transform(df), columns=pipeline.named_steps["preprocessing"].get_feature_names_out())
        prob = float(model.predict_proba(X_df[[f for f in selected_features if f in X_df.columns]])[0][1])
        pred, risk = int(prob >= THRESH), get_risk(prob, THRESH)
        
        row = {"request_id": rid, "timestamp": datetime.now().isoformat(), "model_version": VERSION, "prob": prob, "pred": pred, "risk": risk, **data_dict}
        pd.DataFrame([row]).to_csv(PRED_LOG_PATH, mode="a", header=not PRED_LOG_PATH.exists(), index=False)
        
        return {"request_id": rid, "prob": round(prob, 4), "prediction": "Placed" if pred == 1 else "Not Placed", "risk": risk, "recommendation": get_tips(risk, data_dict)}
    except Exception as e:
        logger.error(f"Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)