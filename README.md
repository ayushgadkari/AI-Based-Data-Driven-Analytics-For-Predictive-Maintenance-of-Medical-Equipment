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
* **$R^2$ Score:** 0.387

---

## 🏗️ Tech Stack
* **Backend:** FastAPI, SQLAlchemy, MySQL
* **Frontend:** HTML, CSS, JavaScript
* **Machine Learning:** Scikit-learn, Pandas, NumPy

---

## ⚙️ Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
   cd your-repo-name
Install dependencies:

Bash
pip install -r requirements.txt
Start the backend server:

Bash
uvicorn backend.main:app --reload
📦 Model Files
Model files are not included in this repository due to size limits.

Download the pre-trained model files from [Add your link here].

Place the downloaded files inside the backend/ directory.

👨‍💻 Author
Ayush Gadkari


**Key Formatting Fixes Applied:**
* **Headers (`#`, `##`):** Converted text sections into Markdown headers so GitHub generates a clean hierarchy and table of contents.
* **Code Blocks (\`\`\`bash):** Formatted terminal setup commands so users can copy them with a single click.
* **Inline Code (`/predict`, `backend/`):** Highlighted API paths, risk levels, and folder structures for readability.
* **Visual Dividers (`---`):** Added horizontal rules to separate topics visually on Git
