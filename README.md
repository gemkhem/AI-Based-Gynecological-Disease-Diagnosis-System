# 🏥 Gynaecological Disease Diagnosis Expert System (GDDES)

[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Django 4.2](https://img.shields.io/badge/Django-4.2-darkgreen.svg)](https://www.djangoproject.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3.2-orange.svg)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-ready, intelligent clinical decision support web application for diagnosing gynaecological conditions (**PCOS**, **UTI**, and **Healthy Physiological Baseline**) using a trained **Random Forest Classifier** with 99% accuracy across **16 clinical symptom biomarkers**, integrated with **English Patient Review Intelligence**.

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Quick Start with Docker](#-quick-start-with-docker-recommended)
- [Local Development Setup](#-local-development-setup)
- [Environment Configuration](#-environment-configuration)
- [Application Routes](#-application-routes)
- [Machine Learning Model & Benchmarks](#-machine-learning-model--benchmarks)
- [Troubleshooting & FAQ](#-troubleshooting--faq)

---

## ✨ Key Features

| Capability | Details |
|---|---|
| 🩺 **16-Biomarker Diagnostic Matrix** | Evaluates urinary, nephrological, menstrual, and hyperandrogenic biomarkers. |
| 🤖 **Random Forest Inference** | Fast (<15ms) in-memory cached model inference achieving 99% accuracy. |
| 💬 **Review & Care Guidance** | Dynamic condition summaries, medical action plans, and verified patient reviews in English. |
| 📊 **ML Benchmark Dashboard** | Interactive accuracy query comparing Random Forest (99%), Decision Tree (99%), SVM (74%), KNN (66%), and Gradient Boosting (67%). |
| 🔐 **Authentication System** | Secure user registration and login with SQLite zero-config fallback and optional MySQL support. |
| 🐳 **Docker & Docker Compose** | Multi-stage, non-root, production-grade containerization with live reload dev mounting. |
| 🎨 **Modern Medical UI/UX** | Responsive healthcare design system with glassmorphic navigation, accessible segmented toggle chips, and clinical alert badges. |

---

## 🏗 System Architecture

```
User Input (16 Symptoms)
         │
         ▼
Random Forest Classifier (In-Memory Cached Model)
         │
         ▼
Prediction Generated (Healthy / PCOS / UTI)
         │
         ▼
Dynamic Clinical Intelligence Presentation
  ├── 1. Diagnostic Status Card (Emerald / Amber / Rose Themes)
  ├── 2. Condition Medical Summary (Physiology & Biological Causes)
  ├── 3. Patient Experience & Doctor Review (Curated Corpus)
  ├── 4. Recommended Action Plan (Lab tests, dietary guidance, red flags)
  └── 5. Interactive Patient Review Explorer (87 Curated Clinical Records)
```

---

## 📁 Project Structure

```
Gynalogical_Disease_Analysis/
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git ignore specifications
├── .dockerignore                 # Docker build exclusions
├── Dockerfile                    # Production & development container definition
├── docker-compose.yml            # Multi-service container orchestration
├── docker-entrypoint.sh          # Container startup & migration handler
├── manage.py                     # Root Django administrative wrapper
├── requirements.txt              # Pinned, locked dependencies (Python 3.10)
├── README.md                     # Comprehensive documentation
│
├── backend/                      # Research datasets, notebooks & models
│   ├── diagnosis_dataset.csv     # 16-symptom training dataset (2,000 records)
│   ├── gynecological_reviews.csv # Curated English patient reviews (87 records)
│   ├── random_forest_model.joblib# Trained ML classifier
│   ├── Disease.ipynb             # Model training & evaluation notebook
│   └── review.ipynb              # English review similarity analysis notebook
│
└── fron-end/                     # Django Web Application
    ├── manage.py                 # Inner Django management entry
    ├── app.db                    # SQLite database
    ├── random_forest_model.joblib# Production model
    ├── gddes/                    # Project settings & URL routing
    │   ├── settings.py           # Production settings with env overrides
    │   ├── urls.py               # Main URL dispatcher
    │   ├── wsgi.py               # WSGI entry for Gunicorn
    │   └── jinja2.py             # Jinja2 environment config
    │
    ├── gddes_app/                # Main clinical application
    │   ├── views.py              # Application views with model caching
    │   ├── models.py             # Database models
    │   └── urls.py               # App-level routing
    │
    ├── templates/                # Medical UI Templates
    │   ├── index.html            # Base layout & clinical landing page
    │   ├── home.html             # Authenticated user dashboard
    │   ├── Prediction.html       # 16-symptom screening & review center
    │   ├── model.html            # ML algorithm benchmark dashboard
    │   ├── about.html            # Clinical background & 16-biomarker schema
    │   ├── login.html            # Sign-in portal
    │   └── register.html         # User registration
    │
    └── static/                   # Static assets (CSS, JS, Fonts, Images)
        └── css/
            └── modern-health.css # Custom healthcare design system
```

---

## 🔧 Prerequisites

- **Option A (Docker):** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- **Option B (Local):** [Python 3.10+](https://www.python.org/) and `pip`.

---

## 🐳 Quick Start with Docker (Recommended)

1. **Clone and enter repository:**
   ```bash
   cd /path/to/Gynalogical_Disease_Analysis
   ```

2. **Copy environment variables:**
   ```bash
   cp .env.example .env
   ```

3. **Start the application with Docker Compose:**
   ```bash
   docker compose up --build
   ```

4. **Access the application:**
   Open your browser at **[http://localhost:8000](http://localhost:8000)**.

To stop the containers:
```bash
docker compose down
```

---

## 💻 Local Development Setup

1. **Create and activate a Python 3.10 virtual environment:**
   ```bash
   # On macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install locked dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Verify and apply migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Start development server:**
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

5. **Open browser:**
   Navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

---

## ⚙️ Environment Configuration

Configuration is managed via `.env` (copy from `.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | `django-insecure-...` | Cryptographic secret for sessions and CSRF |
| `DJANGO_DEBUG` | `True` | Set `False` for production deployments |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost,0.0.0.0,web` | Hostnames permitted to serve traffic |
| `PORT` | `8000` | Port exposed by web server |
| `MYSQL_HOST` | *(empty)* | Optional MySQL host (falls back to SQLite if unset) |
| `MYSQL_USER` | `root` | Optional MySQL user |
| `MYSQL_PASSWORD` | *(empty)* | Optional MySQL password |
| `MYSQL_DATABASE` | `db` | Optional MySQL database name |
| `MYSQL_PORT` | `3306` | Optional MySQL port |

---

## 🌐 Application Routes

| Route | Method | View | Description |
|---|---|---|---|
| `/` | `GET` | `index` | Public landing page with clinical overview |
| `/about` | `GET` | `about` | Clinical problem, methodology, and 16 biomarkers |
| `/register` | `GET, POST` | `register` | Patient/clinician account registration |
| `/login` | `GET, POST` | `login` | Authentication and session initiation |
| `/home` | `GET` | `home` | Authenticated clinical dashboard |
| `/prediction` | `GET, POST` | `prediction` | 16-symptom diagnosis & clinical review intelligence |
| `/model` | `GET, POST` | `model_view` | 5-algorithm ML benchmark & accuracy query |

---

## 🤖 Machine Learning Model & Benchmarks

The core diagnostic model is a **Random Forest Classifier** trained on stratified patient data with **16 clinical biomarkers**:

### Biomarker Matrix
1. **Nausea**
2. **Lumbar Pain**
3. **Urine Pushing (Frequency)**
4. **Micturition Pains (Dysuria)**
5. **Burning of Urethra**
6. **Itch (Pruritus)**
7. **Swelling of Urethra Outlet**
8. **Inflammation of Urinary Bladder**
9. **Nephritis of Renal Pelvis Origin**
10. **Irregular Periods**
11. **No Periods (Amenorrhea)**
12. **Excessive Hair Growth (Hirsutism)**
13. **Buttocks Weight Discomfort**
14. **Central Belly Fat**
15. **Hair Loss (Alopecia)**
16. **Persistent Hormonal Acne**

### Algorithm Performance Comparison

| Algorithm | Model Family | Test Accuracy | Status |
|---|---|---|---|
| **Random Forest Classifier** | Bagging Ensemble of Trees | **99%** | 🏆 **Production Engine** |
| **Decision Tree Classifier** | Single Decision Tree | **99%** | High Variance / Prone to Overfitting |
| **Support Vector Machine (SVM)** | Maximum Margin Hyperplane | **74%** | Baseline Linear Model |
| **Gradient Boosting Classifier** | Sequential Boosting | **67%** | Sub-Optimal on Sparse Features |
| **K-Nearest Neighbors (KNN)** | Instance Metric Distance | **66%** | Baseline Metric Model |

---

## ❓ Troubleshooting & FAQ

### Port 8000 already in use?
Check and terminate lingering processes:
```bash
# macOS / Linux
lsof -ti:8000 | xargs kill -9
```
Or run on an alternate port:
```bash
python manage.py runserver 127.0.0.1:8001
```

### Database reset
To reset the local SQLite database:
```bash
rm fron-end/app.db
python manage.py migrate
```

---

## 📄 License
This project is open-source under the MIT License.
