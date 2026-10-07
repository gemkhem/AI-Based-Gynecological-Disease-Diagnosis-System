# 🏥 Gynaecological Disease Diagnosis Expert System (GDDES)

A Django-based intelligent web application for diagnosing gynaecological diseases
(PCOS, UTI, or Healthy) using a trained Random Forest machine learning model.
Patients answer symptom-based questions and receive an instant AI-powered diagnosis.

---

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [Application Routes](#application-routes)
- [Technology Stack](#technology-stack)
- [ML Model Info](#ml-model-info)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 User Authentication | Register & Login with SQLite fallback (MySQL optional) |
| 🩺 Disease Prediction | Predict PCOS / UTI / Healthy via Random Forest model |
| 📊 Model Comparison | Compare accuracy of 5 classification algorithms |

---

## 📁 Project Structure

\`\`\`
Gynalogical_Disease_Analysis/
├── .venv/                        # Virtual environment (Python 3.10+)
├── requirements.txt              # All Python dependencies
├── README.md                     # This file
├── manage.py                     # Django entry point (root wrapper)
│
├── backend/                      # Jupyter notebooks & training data
│   ├── Disease.ipynb             # Model training notebook
│   ├── diagnosis_dataset.csv     # Training dataset
│   └── random_forest_model.joblib
│
└── fron-end/                     # Django application
    ├── manage.py                 # Django manage (inner)
    ├── app.db                    # SQLite database
    ├── random_forest_model.joblib # Trained ML model
    │
    ├── gddes/                    # Django project config
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── jinja2.py
    │
    ├── gddes_app/                # Main Django app
    │   ├── views.py              # All view logic
    │   ├── models.py
    │   └── urls.py
    │
    ├── templates/                # HTML templates (Jinja2)
    └── static/                   # CSS, JS, images
\`\`\`

---

## 🔧 Prerequisites

- **Python 3.10+**
- **pip** (comes with Python)
- **macOS / Linux / Windows**
- *(Optional)* MySQL Server if not using the SQLite fallback

---

## 🚀 Installation & Setup

### 1. Clone / Open the project

\`\`\`bash
cd /path/to/Gynalogical_Disease_Analysis
\`\`\`

### 2. Create & activate the virtual environment

\`\`\`bash
# Create (already done if .venv exists)
python3 -m venv .venv

# Activate on macOS / Linux
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
\`\`\`

### 3. Install dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Apply database migrations

\`\`\`bash
python manage.py migrate
\`\`\`

---

## Running the Application

\`\`\`bash
# Make sure .venv is activated
source .venv/bin/activate

# Start the development server
python manage.py runserver 8000
\`\`\`

Then open your browser at: **http://127.0.0.1:8000/**

> If port 8000 is in use, try \`python manage.py runserver 8001\`

---

## 🌐 Application Routes

| URL | View | Description |
|---|---|---|
| \`/\` | \`index\` | Landing / home page |
| \`/register\` | \`register\` | User registration |
| \`/login\` | \`login\` | User login |
| \`/home\` | \`home\` | Dashboard after login |
| \`/prediction\` | \`prediction\` | Symptom-based disease prediction |
| \`/model\` | \`model_view\` | ML algorithm accuracy comparison |
| \`/about\` | \`about\` | About the system |

---

## 🛠 Technology Stack

| Layer | Technology |
|---|---|
| **Web Framework** | Django 4.2 |
| **Database** | SQLite (default) / MySQL (optional) |
| **ML Model** | scikit-learn - Random Forest Classifier |
| **Templates** | Jinja2 + Django Templates |
| **Data** | pandas, numpy |

---

## 🤖 ML Model Info

The prediction model (\`random_forest_model.joblib\`) is a **Random Forest Classifier**
trained on a gynaecological diagnosis dataset with **16 symptom features**:

| # | Feature | # | Feature |
|---|---|---|---|
| 1 | Nausea | 9 | Nephritis |
| 2 | Lumbar Pain | 10 | Irregular Periods |
| 3 | Urine Frequency | 11 | No Periods |
| 4 | Micturition | 12 | Excessive Hair Growth |
| 5 | Urethra Burning | 13 | Buttocks Pain |
| 6 | Itching | 14 | Belly Fat |
| 7 | Skin Swelling | 15 | Hair Loss |
| 8 | Inflammation | 16 | Acne |

**Prediction Output:**
- \`0\` - **Healthy**
- \`1\` - **PCOS** (Polycystic Ovary Syndrome)
- \`2\` - **UTI** (Urinary Tract Infection)

---

## 📝 Notes

- MySQL is optional; the app falls back to SQLite automatically.
- The model is loaded once and cached for fast predictions.

---

*Built for gynaecological health awareness.*
