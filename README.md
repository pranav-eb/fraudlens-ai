🚨 FraudLens AI
Explainable Fraud Detection System for Transaction Data
<p align="center"> <b>Clean → Analyze → Detect → Explain</b><br> Production-ready fraud detection pipeline built with FastAPI & ML </p>
📌 Overview

FraudLens AI is a modular fraud detection system designed to process messy, real-world transaction data and convert it into actionable fraud insights.

Unlike toy ML projects, this system focuses on:

Handling dirty datasets
Building a reliable processing pipeline
Delivering interpretable outputs
🔥 Key Capabilities

✔ Robust CSV ingestion (handles messy data)
✔ Automated data cleaning & normalization
✔ Feature engineering for fraud signals
✔ Machine learning–based fraud detection
✔ Data quality scoring system
✔ JSON-based API responses
✔ Scalable FastAPI backend

🧠 System Architecture
                ┌────────────────────┐
                │      Client        │
                │ (Upload CSV File)  │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   FastAPI Server   │
                │     (main.py)      │
                └─────────┬──────────┘
                          │
     ┌────────────────────┼────────────────────┐
     ▼                    ▼                    ▼
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│ Data Cleaner│   │ Feature Engg │   │ ML Model     │
│ cleaner.py  │   │ features.py  │   │ ml_model.py  │
└─────┬───────┘   └──────┬───────┘   └──────┬───────┘
      │                  │                  │
      ▼                  ▼                  ▼
          ┌──────────────────────────────┐
          │   Data Quality Analyzer      │
          │      quality.py             │
          └────────────┬───────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Fraud Insights  │
              │  JSON Output    │
              └─────────────────┘
🔄 Data Flow Diagram (DFD)
Level 0
[User] → [FraudLens AI System] → [Fraud Report]
Level 1
CSV Upload → API → Cleaning → Feature Engineering → ML Model → Quality Check → Output
📂 Project Structure
fraudlens_ai/
│
├── backend/
│   ├── main.py
│   ├── generate_data.py
│   ├── sample_transactions.csv
│   ├── requirements.txt
│   │
│   └── core/
│       ├── cleaner.py
│       ├── features.py
│       ├── ml_model.py
│       ├── quality.py
│
└── start.bat
⚙️ Tech Stack
Layer	Technology
Backend	FastAPI
Language	Python
ML	Scikit-learn / Custom Logic
Data	Pandas, NumPy
API Format	JSON
▶️ Getting Started
1️⃣ Clone the repo
git clone https://github.com/your-username/fraudlens-ai.git
cd fraudlens-ai/backend
2️⃣ Install dependencies
pip install -r requirements.txt
3️⃣ Run the server
uvicorn main:app --reload
4️⃣ Access API docs
http://127.0.0.1:8000/docs
📡 API Usage
Endpoint
POST /upload
Input
CSV file containing transaction data
Output (Example)
{
  "total_transactions": 10000,
  "fraud_transactions": 245,
  "clean_transactions": 9755,
  "fraud_percentage": 2.45,
  "data_quality_score": 0.91
}
🧪 Sample Workflow
Upload dataset
System cleans corrupted/missing values
Extracts fraud-relevant features
ML model evaluates risk
Quality module validates dataset
Returns structured fraud report
⚠️ Honest Limitations (No BS)
No model training pipeline (static logic or pre-trained)
No database (stateless execution)
No authentication/security
No real-time streaming support
No explainability layer (e.g., SHAP)

If you present this as “production-ready AI,” that’s misleading. It’s a strong backend prototype, not a full product.

🚀 Future Roadmap
 Real-time fraud detection (Kafka / streaming)
 Model training & retraining pipeline
 Explainable AI (SHAP / LIME)
 Dashboard UI (React)
 Docker + cloud deployment
 Authentication & RBAC
💡 Design Philosophy
Modular over monolithic
Clarity over cleverness
Pipeline-first architecture
Real-world messy data > clean datasets
🤝 Contributing

Pull requests are welcome, but keep standards high:

Clean code only
No redundant logic
Document everything
