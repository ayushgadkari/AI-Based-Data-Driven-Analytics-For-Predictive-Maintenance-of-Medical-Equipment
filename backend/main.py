from __future__ import annotations

import pathlib
from datetime import datetime, timedelta
from typing import Optional

import joblib
import numpy as np
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session  # <-- Import Session here

# ---------- DB boot ----------
from .database import SessionLocal, engine
from .models import Base, Machine, FailurePrediction, User # <-- Ensure FailurePrediction is imported

# Create all database tables
Base.metadata.create_all(bind=engine)

# ---------- App initialization ----------
app = FastAPI(title="Predictive Maintenance API (Regression)")

# CORS (dev-friendly; narrow later if you deploy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # e.g., ["http://127.0.0.1:5500"] when you host frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DB dependency ----------
def get_db():
    db = SessionLocal()  # DB session to interact with your models
    try:
        yield db
    finally:
        db.close()  # Close session once request is complete

# ---------- ML artifacts ----------
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "backend" / "reg_model.pkl"
SCALER_PATH = BASE_DIR / "backend" / "reg_scaler.pkl"

model = None
scaler = None
artifacts_error: Optional[str] = None

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    artifacts_error = f"Could not load ML artifacts: {e}"

# ---------- Schemas ----------

class MachineCreate(BaseModel):
    name: str
    location: Optional[str] = None
    type: Optional[str] = None

    class Config:
        from_attributes = True  # ORM mode replaced with from_attributes in Pydantic V2

class MachineOut(BaseModel):
    id: int
    name: str
    location: Optional[str]
    type: Optional[str]

    class Config:
        from_attributes = True  # ORM mode replaced with from_attributes in Pydantic V2

# Reading schema
class ReadingCreate(BaseModel):
    machine_id: int
    temperature: float
    vibration: float
    pressure: float

    class Config:
        from_attributes = True  # ORM mode replaced with from_attributes in Pydantic V2

class ReadingOut(BaseModel):
    id: int
    machine_id: int
    temperature: float
    vibration: float
    pressure: float
    recorded_at: datetime

    class Config:
        from_attributes = True  # ORM mode replaced with from_attributes in Pydantic V2

# Prediction schema
class PredictionDBOut(BaseModel):
    id: int
    machine_id: int
    risk_score: float
    risk_level: str
    recommended_maintenance_date: Optional[str]
    message: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
      # ORM mode replaced with from_attributes in Pydantic V2

# ML input (supports optional machine_id for DB logging)
class MLReading(BaseModel):
    machine_id: Optional[int] = None  # optional link to a machine

    internal_temperature_c: float = Field(..., ge=200, le=400, description="Kelvin")
    probe_health_score_percent: float = Field(..., ge=0, le=100, description="Percent")
    error_count_30d: int = Field(..., ge=0, description="Number of errors in 30 days")
    cooling_fan_rpm: int = Field(..., ge=0, description="Cooling fan RPM")
    power_consumption_w: float = Field(..., ge=0, description="Power consumption in Watts")
    voltage_fluctuation_v: float = Field(..., ge=0, description="Voltage fluctuation in Volts")
    daily_usage_hours: float = Field(..., ge=0, description="Daily usage hours")
    image_artifact_score_0_10: float = Field(..., ge=0, le=10, description="Artifact score (0 to 10)")
    last_service_days_ago: int = Field(..., ge=0, description="Days since last service")

    class Config:
        from_attributes = True  # ORM mode replaced with from_attributes in Pydantic V2

# Prediction output for ML (days to failure)
class MLPredictionOut(BaseModel):
    predicted_days_to_failure: int
    recommended_maintenance_date: str
    status: str
    message: str

# ---------- Root / Health ----------
@app.get("/")
def root():
    return {"message": "Backend running successfully ✅"}

@app.get("/health")
def health():
    return {
        "ok": True,
        "db": "ok",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None,
        "artifacts_error": artifacts_error,
    }

# ---------- ML Predict ----------
@app.post("/predict", response_model=MLPredictionOut)
def ml_predict(payload: MLReading, db=Depends(get_db)):
    if model is None or scaler is None:
        raise HTTPException(
            status_code=500,
            detail="Model or scaler not loaded.",
        )

    # Prepare features in the same order as during training
    X = np.array([[ 
        payload.internal_temperature_c,
        payload.probe_health_score_percent,
        payload.error_count_30d,
        payload.cooling_fan_rpm,
        payload.power_consumption_w,
        payload.voltage_fluctuation_v,
        payload.daily_usage_hours,
        payload.image_artifact_score_0_10,
        payload.last_service_days_ago
    ]])

    # Scale the features
    X_scaled = scaler.transform(X)

    # Predict days to failure
    predicted_days = model.predict(X_scaled)[0]
    days_rounded = max(1, round(predicted_days))
    recommended_date = (datetime.now() + timedelta(days=days_rounded)).strftime("%Y-%m-%d")

    # Determine risk level based on predicted days
    if days_rounded <= 15:
        status = "Critical"
        message = "Immediate maintenance recommended."
    elif days_rounded <= 40:
        status = "Warning"
        message = "Plan maintenance within the next few weeks."
    else:
        status = "Healthy"
        message = "Machine is operating within safe limits."

    # Log the prediction in the database
    m = db.query(Machine).filter(Machine.id == payload.machine_id).first()
    if m:
        db_pred = FailurePrediction(
    machine_id=m.id,
    risk_score=predicted_days,
    risk_level=status,
    recommended_maintenance_date=recommended_date,
    message=message
)

        db.add(db_pred)
        db.commit()

    return MLPredictionOut(
        predicted_days_to_failure=days_rounded,
        recommended_maintenance_date=recommended_date,
        status=status,
        message=message
    )

# ---------- Machine Creation Endpoint ----------
@app.post("/machines/")
def create_machine(machine: MachineCreate, db: Session = Depends(get_db)):
    db_machine = Machine(name=machine.name, location=machine.location, type=machine.type)
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine

# ---------- Get Machines ----------
@app.get("/machines/")
def get_machines(db: Session = Depends(get_db)):
    return db.query(Machine).all()

# ---------- Fetch Predictions ----------
@app.get("/predictions")
def get_predictions(db: Session = Depends(get_db)):
    predictions = db.query(FailurePrediction).all()
    return predictions

@app.delete("/predictions/by-machine/{machine_id}")
def delete_predictions_by_machine(machine_id: int, db: Session = Depends(get_db)):
    predictions = db.query(FailurePrediction).filter(
        FailurePrediction.machine_id == machine_id
    ).all()

    if not predictions:
        return {"message": "No predictions found for this machine"}

    for p in predictions:
        db.delete(p)

    db.commit()
    return {"message": f"Deleted predictions for machine {machine_id}"}

@app.delete("/machines/{machine_id}")
def delete_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    db.delete(machine)
    db.commit()
    return {"message": f"Machine {machine_id} deleted"}



from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


from jose import jwt

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


from pydantic import BaseModel
from fastapi import HTTPException

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"sub": user.username, "role": user.role}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token}

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/predictions")
def get_predictions(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(FailurePrediction).all()
