# AI-Based-Data-Driven-Analytics-For-Predictive-Maintenance-of-Medical-Equipment

An AI-driven system that predicts failure timelines of medical equipment using machine learning, enabling hospitals to perform proactive maintenance and reduce downtime.

This project leverages data-driven analytics to forecast equipment failures based on sensor and usage data. It helps healthcare facilities shift from reactive to predictive maintenance, improving reliability and operational efficiency.

Features
🔍 Predicts days-to-failure using Machine Learning
⚠️ Risk classification: Healthy | Warning | Critical
📊 Tracks equipment health using multiple parameters
🌐 REST API for real-time predictions
🔐 Secure authentication using JWT
💾 Stores and manages equipment & sensor data
🖥️ Simple frontend dashboard for non-technical users

Machine Learning Model
Model: Random Forest Regressor
Dataset: 3,000 equipment records
Features used:
Temperature
Voltage fluctuation
Daily usage
Other health parameters (total: 9)


📈 Performance
MAE: 4.28 days
R² Score: 0.387


Tech Stack
Backend
FastAPI
SQLAlchemy
MySQL
JWT Authentication

Frontend
HTML
CSS
JavaScript

Machine Learning
Scikit-learn
Pandas
NumPy

API Endpoints
🔹 Predict Failure
POST /predict

Input:

{
  "temperature": 45,
  "voltage": 220,
  "usage_hours": 10
}

Output:

{
  "predicted_days_to_failure": 5,
  "risk_level": "Critical"
}


System Architecture
Frontend → User interaction & dashboard
Backend (FastAPI) → API handling & business logic
Database (MySQL) → Stores equipment & sensor data
ML Model (.pkl) → Predicts failure timeline


Risk Classification Logic
Days to Failure	Risk Level
> 15 days	Healthy
7 – 15 days	Warning
< 7 days	Critical


Setup Instructions
1️⃣ Clone the Repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Setup Database
Create a MySQL database
Update database credentials in .env or config file
5️⃣ Run the Server
uvicorn main:app --reload
