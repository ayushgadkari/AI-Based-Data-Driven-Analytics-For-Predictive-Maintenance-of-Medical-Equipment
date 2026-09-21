# AI-Based Data-Driven Analytics for Predictive Maintenance of Medical Equipment

An AI-powered system that predicts equipment failures before they occur using machine learning, helping hospitals perform proactive maintenance and significantly reduce downtime.

---

## 🚀 Features
* **Failure Prediction:** Forecasts days-to-failure using a Random Forest model.
* **Risk Level Classification:** Categorizes equipment state into `Healthy`, `Warning`, or `Critical`.
* **REST API:** Serves real-time inference via a `/predict` endpoint.
* **Authentication:** Secure backend access using JWT tokens.
* **Interactive Frontend:** Simple web interface for live monitoring and data entry.

---

## 🧠 Model Performance
* **Training Data:** 3,000+ medical equipment records
* **Mean Absolute Error (MAE):** 4.28 days
* **R² Score:** 0.387 *(Realistic baseline reflecting real-world variance)*

---

## 🏗️ Tech Stack
* **Backend:** FastAPI, SQLAlchemy, MySQL
* **Frontend:** HTML, CSS, JavaScript
* **Machine Learning:** Scikit-learn, Pandas, NumPy

---

## ⚙️ Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ayushgadkari/AI-Based-Data-Driven-Analytics-For-Predictive-Maintenance-of-Medical-Equipment.git](https://github.com/ayushgadkari/AI-Based-Data-Driven-Analytics-For-Predictive-Maintenance-of-Medical-Equipment.git)
   cd AI-Based-Data-Driven-Analytics-For-Predictive-Maintenance-of-Medical-Equipment

2. Install dependencies:
    ```bash
   pip install -r requirements.txt

3. Start the backend server:
    ```bash
   uvicorn backend.main:app --reload

Model Files
Model files are not included in this repository due to size limits.

Please place your trained model files inside the backend/ directory before running the server.

👨‍💻 Author
Ayush Gadkari
