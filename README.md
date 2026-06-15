# 🏥 Hospital Audit Intelligence & AI Chatbot Suite

Welcome to the **Hospital Audit Intelligence & AI Chatbot Suite**. This repository contains a premium, full-stack application designed to revolutionize hospital operations, compliance monitoring, and audit verification:

*   **Reallist Audit (AI-Powered Assistant & Dashboard)**: An analytics panel and natural language AI assistant that parses audit logs, runs scikit-learn forecasting models, and handles complex queries locally.

---

## 🏗️ System Overview & Workflow

This system targets compliance dashboard data visualization and chatbot inquiry answering. It monitors compliance against NABH benchmarks ($\ge 80\%$) and projects hospital risk trends dynamically.

```mermaid
graph TD
    User([User / Admin]) <--> |Interacts / Queries| Frontend[React + Vite Frontend]
    Frontend <--> |HTTP API / JSON| Backend[Flask API Server]
    Backend <--> |Scikit-Learn Regression| DataAnalyzer[Hospital Audit Analyzer]
    Backend <--> |NLP Intent Classifier| NLPEngine[TF-IDF Cosine Similarity]
    DataAnalyzer <--> |Reads & Hot-reloads| CSV[(hospital_audit_500.csv)]
```

---

## ✨ Features

*   **Dynamic Analytics Dashboard**: Real-time evaluation of risk scores, compliance percentages, pending/failed audits, and open escalations.
*   **Predictive Risk Analytics**: Linear regression forecasting of hospital risk trends and compliance changes for 7-day and 30-day projection intervals.
*   **NLP Intent Classification**: Embedded chatbot recognizing and resolving queries (e.g., *"Which ward has the highest risk?"*, *"Who needs training?"*) using local TF-IDF vectorization and cosine similarity.
*   **Staff Performance Audits**: Metrics ranking staff by pass rates, tracking failed audits, and generating training recommendations.

---

## 📂 Project Structure

```
├── backend/                   # Consolidated Flask backend server and ML/CV modules
│   ├── app.py                 # Flask server routes & chat API endpoints (runs dashboard & chatbot APIs)
│   ├── data_analyzer.py       # Core analytics & scikit-learn forecasting logic
│   ├── nlp_engine.py          # TF-IDF & cosine similarity intent classification
│   ├── requirements.txt       # Python dependencies for the backend
│   └── hospital_audit_500.csv # Audit log dataset copy
├── frontend/                  # Consolidated Vite + React (v19) + Tailwind CSS (v4) frontend
│   ├── src/
│   │   ├── components/        # Active components (Chatbot window & Dashboard visualization)
│   │   │   ├── Chatbot.jsx    # Floating chatbot assistant interface
│   │   │   └── Dashboard.jsx  # Main dashboard display
│   │   ├── App.jsx            # Main app entrypoint, layout & dark mode
│   │   └── index.css          # Tailwind setup
│   └── package.json           # Frontend dependencies & run scripts
├── hospital_audit_500.csv     # Global audit logs dataset
├── generate_csv.py            # Generates mock audit log CSV data
├── verify_backend.py          # Python script verifying NLP and analytics models
└── README.md                  # Project documentation
```

---

## 🛠️ Prerequisites

*   **Python 3.10+**
*   **Node.js 18+** & **npm**

---

## 🚀 Running the Applications

### 1. Setup Backend
1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   * **Windows**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **macOS/Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch the Flask API server:
   ```bash
   python app.py
   ```
   *Runs on [http://localhost:5000](http://localhost:5000)*

### 2. Setup Frontend
1. Navigate to the frontend folder:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite dev server:
   ```bash
   npm run dev
   ```
   *Runs on [http://localhost:5173](http://localhost:5173)*

---

## 💬 Sample Chatbot Queries (Reallist Audit)

Try asking the AI Assistant queries like:
*   *“Which ward has highest risk?”*
*   *“Predict future risk”*
*   *“Show compliance score trend”*
*   *“List pending audits”*
*   *“Best performing staff”*
*   *“Who needs training or attention?”*
*   *“Is ICU hygiene risk increasing during night shifts?”*
*   *“NABH compliance score showing steady improvement this week”*

---

## 🧪 Model & Component Verification

To run automated checks on the NLP intent classifier and CSV parsing logic:
```bash
python verify_backend.py
```
This script will validate:
1. Cosine similarity classifications for chatbot queries.
2. Hospital risk scores and multi-day linear regression calculations.