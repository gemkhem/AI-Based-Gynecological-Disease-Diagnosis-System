# 📦 Changelog & Release Notes

All notable releases for the **Gynaecological Disease Diagnosis Expert System (GDDES)** are documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.0.0] - 2026-10-08

### 🚀 Initial Production Release

#### ✨ Core Capabilities
- **16-Biomarker Diagnostic Matrix**: Ingests physiological indicators spanning nephrological, urinary, systemic pain, and hyperandrogenic categories.
- **Random Forest Inference Engine**: High-performance model achieving **99% test accuracy** across 3 target classifications (`Healthy`, `PCOS`, `UTI`).
- **Singleton Model Caching**: In-memory lazy loader reducing inference latency from ~350ms to **<15ms**.
- **English Clinical Review Intelligence**: Automatic symptom-to-explanation engine providing diagnostic summaries, recovery insights, and action plans.
- **Algorithm Benchmark Portal**: Comparative performance evaluator querying Random Forest, Decision Tree, SVM, KNN, and Gradient Boosting.

#### 🐳 Containerization & Packaging
- **Docker & Docker Compose**: Production-ready multi-stage Docker build running under an unprivileged `appuser` (UID 1000) with Gunicorn WSGI.
- **Python Packaging**: Configured `pyproject.toml` supporting distribution builds for GitHub Packages and PyPI.
- **GitHub Actions Automation**: Automated CI/CD pipeline for publishing container images to GitHub Container Registry (`ghcr.io`) and creating GitHub Releases.

#### 🎨 User Interface & Experience
- Modern medical design system (`modern-health.css`) with responsive cards, accessible segmented control chips, and clinical alert badges.

#### 🛡️ Security & Reliability
- Excluded virtual environments, `.env` secrets, database files, and caches via updated `.gitignore` and `.dockerignore`.
- Environment-driven configuration via `python-dotenv`.
