# ☀️ Solar Power Forecasting & MLOps Pipeline

[![FastAPI](https://img.shields.io/badge/FastAPI-0055ff?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Evidently AI](https://img.shields.io/badge/Evidently_AI-purple?style=for-the-badge)](https://www.evidentlyai.com/)

A professional-grade machine learning system designed to forecast solar power generation while maintaining high reliability through automated monitoring and containerized deployment.

---

## 🚀 Project Overview

This project implements a full MLOps lifecycle for renewable energy forecasting. It features a Random Forest model for solar energy prediction, integrated with **Evidently AI** for real-time data drift and model performance monitoring. The entire system is packaged as a **FastAPI** service inside a **Docker** container, ready for production-grade environments.

### 🌟 Key Features

*   **Professional Feature Engineering**: Implementation of cyclic time encoding (Sin/Cos), lag features, and rolling statistics to capture temporal dependencies.
*   **Self-Monitoring API**: A dedicated `/monitor` endpoint that triggers a real-time data drift and regression performance analysis.
*   **Production Readiness**: Fully containerized using Docker with support for both local and cloud-standard port configurations.
*   **Automated Reporting**: Generates interactive HTML reports to visualize model health and feature stability.

---

## 🏗️ System Architecture

1.  **Data Processing**: Raw sensor data (Temperature, Irradiation) is processed through `build_features.py` to create model-ready features.
2.  **Inference**: A FastAPI server provides a `/predict` endpoint for real-time forecasting.
3.  **Monitoring**: The system tracks performance by comparing current production data against a reference baseline.
4.  **Deployment**: The environment is standardized via Docker, ensuring consistency across different machines.

---

## ⚙️ Feature Engineering Details

To ensure high accuracy, the pipeline incorporates advanced feature engineering techniques:

*   **Cyclic Encoding**: Hours are mapped to Sine and Cosine components to preserve the periodic nature of time (e.g., ensuring 23:00 and 00:00 are recognized as adjacent).
*   **Lag Features**: Captures the "persistence" effect by including previous measurements of DC power and irradiation.
*   **Rolling Statistics**: Uses a 1-hour rolling average to smooth noise and identify short-term trends.

---

## 🛠️ Installation & Setup

### Prerequisites

*   Python 3.11+
*   Docker (optional, for containerized run)

### Local Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/solar-forecasting.git
    cd solar-forecasting
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the API**:
    ```bash
    uvicorn src.main:app --reload
    ```

---

## 🐳 Docker Usage

### Build the Image
To build the container locally:
```bash
docker build -t solar-app .
```

### Run the Container
```bash
docker run -d --name solar-service -p 8000:8000 solar-app
```
The API will be available at `http://localhost:8000`.

---

## 📡 API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/predict` | `POST` | Receives sensor data and returns a solar power forecast (kW). |
| `/monitor` | `GET` | Triggers the drift simulation and returns an interactive HTML report. |
| `/report-link` | `GET` | Provides a URL to view previously generated monitoring reports. |
| `/docs` | `GET` | Interactive Swagger API documentation. |

---

## 📈 Monitoring & Drift Analysis

The project uses **Evidently AI** to ensure the model remains accurate over time. By calling the `/monitor` endpoint, the system:

1.  Loads reference data and current production data.
2.  **Checks for Data Drift**: Detects if statistical properties of inputs (like irradiation) have changed significantly.
3.  **Analyzes Regression Performance**: Calculates MAE, RMSE, and visualizes error distribution.
4.  **Generates Reports**: Saves a visual interactive report at `reports/drift_report.html`.

---

## ☁️ Cloud Deployment Path

Although this project is currently configured for local use, a complete roadmap for **Google Cloud Platform (GCP)** deployment has been prepared:

*   **Cloud Run**: For serverless API hosting.
*   **Cloud Storage**: For a centralized "Data Hub" to store reference sets and reports.
*   **Cloud Scheduler**: For automated daily health checks.

For detailed, step-by-step instructions, please refer to:
📄 **[GCP_deployment_Steps.md](GCP_deployment_Steps.md)**

---

## 📂 Project Structure

```text
├── data/               # Reference and sample datasets
├── models/             # Serialized model files (.joblib)
├── reports/            # Generated monitoring HTML reports
├── src/
│   ├── main.py         # FastAPI application logic
│   ├── monitoring.py   # Evidently AI report generation logic
│   └── features/
│       └── build_features.py  # Feature engineering pipeline
├── simulate_drift.py   # Script to simulate production data & trigger monitoring
├── Dockerfile          # Containerization instructions
└── requirements.txt    # Project dependencies
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.