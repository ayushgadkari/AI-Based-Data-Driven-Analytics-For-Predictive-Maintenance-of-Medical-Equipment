import pathlib
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------- Paths ----------
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "backend" / "model.pkl"
SCALER_PATH = BASE_DIR / "backend" / "scaler.pkl"

# ---------- Load artifacts (fail fast at startup) ----------
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model/scaler: {e}")

# ---------- App ----------
app = FastAPI(title="ML Model API", version="1.0.0")

# Allow the browser page (file:// or 127.0.0.1:5500) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev: open. Later restrict to your origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Schemas ----------
class ReadingInput(BaseModel):
    air_temp: float = Field(..., description="Air temperature (K)")
    process_temp: float = Field(..., description="Process temperature (K)")
    rpm: float = Field(..., description="Rotational speed (rpm)")
    torque: float = Field(..., description="Torque (Nm)")
    tool_wear: float = Field(..., description="Tool wear (min)")

class PredictionOut(BaseModel):
    predicted_failure: bool
    failure_probability: float
    risk_level: str

# ---------- Health ----------
@app.get("/", tags=["health"])
def root():
    return {"message": "ML Model API ready ✅"}

# ---------- Predict ----------
@app.post("/predict", response_model=PredictionOut, tags=["predict"])
def predict_failure(data: ReadingInput):
    try:
        features = np.array([[
            float(data.air_temp),
            float(data.process_temp),
            float(data.rpm),
            float(data.torque),
            float(data.tool_wear),
        ]], dtype=np.float64)

        # guard against NaNs/Infs
        if not np.isfinite(features).all():
            raise HTTPException(status_code=422, detail="Inputs must be finite numbers")

        X = scaler.transform(features)
        # Some models don’t implement predict_proba
        if hasattr(model, "predict_proba"):
            prob = float(model.predict_proba(X)[0][1])
        else:
            # fallback: map decision_function to [0,1]
            if hasattr(model, "decision_function"):
                s = float(model.decision_function(X)[0])
                prob = 1.0 / (1.0 + np.exp(-s))
            else:
                # bare minimum: 0/1 prediction only
                prob = float(model.predict(X)[0])

        pred = int(model.predict(X)[0])

        if prob > 0.7:
            risk = "HIGH"
        elif prob > 0.4:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return PredictionOut(
            predicted_failure=bool(pred),
            failure_probability=round(prob, 3),
            risk_level=risk,
        )
    except HTTPException:
        raise
    except Exception as e:
        # surfaces a clear error to /docs and the frontend
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")
