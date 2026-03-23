🚀 Autonomous API Failure Prediction & Contract Testing Platform

A smart API monitoring system that tracks API health, predicts failures, validates contracts, and provides real-time dashboards — inspired by modern DevOps tools like Grafana.

📌 Project Overview

This platform continuously monitors multiple APIs, logs their performance, and provides:

📡 Real-time API monitoring
⚡ Response time tracking
📊 Interactive charts & dashboards
🤖 AI-based failure prediction
🧪 Contract testing (JSON validation)
🚨 Smart alert system (Email alerts)
🔁 SRE-based alert escalation
📈 Failure history tracking
🎯 Key Features
🔹 1. Multi-API Monitoring

Monitor multiple APIs simultaneously:

Weather APIs
Public APIs
Custom APIs

🔹 2. Real-Time Dashboard

Live response time graph
API health pie chart
Latency comparison bar chart
Auto-refresh every 10 seconds

🔹 3. AI Failure Prediction

Predicts API risk level:
🟢 Low Risk
🟡 Medium Risk
🔴 High Risk
Gauge-style visualization

🔹 4. Smart Alert System

Sends email alerts on API failure
Uses SRE alert escalation logic:
Alert only after 3 consecutive failures

🔹 5. Contract Testing

Validates API response structure using JSON schema
Ensures API reliability

🔹 6. Failure History Tracking

Stores API failures in database
Displays recent failures in dashboard

🛠️ Tech Stack
🔹 Backend
Python
Flask
SQLite
🔹 Frontend
HTML, CSS
Bootstrap 5
Chart.js
🔹 Libraries
requests
jsonschema
smtplib (for alerts)

📂 Project Structure

API-Monitoring-Platform/
│
├── app.py                  # Main Flask app
├── monitor.py              # API monitoring logic
├── predictor.py            # Failure prediction logic
├── contract_test.py        # Contract validation
├── alert.py                # Email alert system
├── scheduler.py            # Background scheduler
│
├── templates/
│   └── dashboard.html      # UI Dashboard
│
├── static/
│   └── style.css           # Styling
│
├── data/
│   └── api_logs.db         # Database
│
└── README.md

⚙️ Installation & Setup
🔹 Step 1: Clone Repository
git clone https://github.com/your-username/API-Monitoring-Platform.git
cd API-Monitoring-Platform

🔹 Step 2: Install Dependencies
pip install flask requests jsonschema

🔹 Step 3: Run Application
python app.py
🔹 Step 4: Open Dashboard
http://127.0.0.1:5000

📊 How It Works
API List → Monitor → Store Logs → Analyze → Predict → Display Dashboard
APIs are monitored using requests

Response time & status are logged in SQLite
Failure prediction logic analyzes API behavior
Alerts are triggered on repeated failures
Dashboard displays real-time insights

🧪 Sample APIs for Testing

https://jsonplaceholder.typicode.com/posts
https://api.github.com/users/octocat
https://official-joke-api.appspot.com/random_joke
https://httpstat.us/500

🚨 Alert System Setup (Gmail)
Enable 2-Step Verification
Generate App Password
Add credentials in alert.py
📈 Future Enhancements
🔄 Real-time WebSocket updates
🧠 Advanced ML model for prediction
☁️ Cloud deployment (AWS/Docker)
📱 Mobile-friendly dashboard
🔔 Slack/Telegram alerts
👨‍💻 Author

Ashu
B.Tech CSE (AI & ML)
Aspiring AI/ML Engineer 🚀

⭐ Conclusion

This project demonstrates real-world DevOps monitoring concepts including:

API observability
Failure prediction
Alerting systems
Performance tracking

It is a mini version of industry tools like Grafana and Datadog, making it a strong portfolio project.

⭐ If you like this project

Give it a ⭐ on GitHub!
