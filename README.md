# 🚀 Autonomous API Testing Platform

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Flask](https://img.shields.io/badge/Framework-Flask-black?logo=flask)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?logo=sqlite)
![Status](https://img.shields.io/badge/Project-Beta-yellow)
![License](https://img.shields.io/badge/License-Educational-green)

---

## 📌 Overview

An intelligent platform that **monitors APIs, predicts failures using machine learning, and validates API contracts**.
It helps developers ensure **high availability, reliability, and early failure detection**.

---

## 🎯 Key Features

✨ **API Monitoring**

* Real-time API health tracking
* Status detection (Healthy / Failed)

🤖 **Failure Prediction**

* ML-based prediction using historical data
* Early detection of potential failures

📜 **Contract Testing**

* Validates API responses against schemas
* Prevents breaking changes

📧 **Email Alerts**

* Instant alerts for failures
* Improves response time

📊 **Interactive Dashboard**

* Visual representation of API health
* Insights into failures and trends

---

## 🛠️ Tech Stack

| Layer    | Technology            |
| -------- | --------------------- |
| Backend  | Flask (Python)        |
| Database | SQLite                |
| Frontend | HTML, CSS, JavaScript |
| ML Model | Python                |

---

## ⚙️ Installation Guide

### 🔹 Step 1: Clone Repository

```bash
git clone https://github.com/Ashu1792/Autonomous-API-Testing-Platform.git
cd Autonomous-API-Testing-Platform
```

### 🔹 Step 2: Setup Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 🔹 Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### 🔹 Step 4: Run Application

```bash
python app.py
```

### 🔹 Step 5: Access App

```
http://127.0.0.1:5000/
```

---

# 📡 API Documentation

## 🔐 Authentication

> *(If implemented)*

* Session-based login using Flask
* Only authenticated users can access dashboard

---

## 🔍 1. Monitor API

**Endpoint:**

```
GET /monitor
```

**Description:**
Checks the health status of registered APIs.

**Response:**

```json
{
  "api_url": "https://example.com",
  "status": "Healthy",
  "response_time": "120ms"
}
```

**Error Response:**

```json
{
  "status": "Failed",
  "error": "Timeout"
}
```

---

## 🤖 2. Predict API Failure

**Endpoint:**

```
POST /predict
```

**Request Body:**

```json
{
  "api_url": "https://example.com"
}
```

**Response:**

```json
{
  "prediction": "High Risk",
  "confidence": "87%"
}
```

**Description:**
Uses trained ML model to predict the likelihood of API failure.

---

## 📜 3. Contract Testing

**Endpoint:**

```
POST /contract-test
```

**Request Body:**

```json
{
  "api_url": "https://example.com",
  "expected_schema": {
    "name": "string",
    "age": "number"
  }
}
```

**Response:**

```json
{
  "status": "Valid",
  "message": "Response matches contract"
}
```

**Error Response:**

```json
{
  "status": "Invalid",
  "message": "Schema mismatch"
}
```

---

## 📧 4. Email Alerts

**Trigger:**

* Automatically triggered when API fails

**Example Output:**

```
Subject: API Failure Alert

Message:
API https://example.com is DOWN
```

---

## 📊 5. Dashboard Data

**Endpoint:**

```
GET /dashboard-data
```

**Response:**

```json
{
  "total_apis": 5,
  "healthy": 4,
  "failed": 1
}
```

---

## 🧠 System Workflow

```
User Input → API Monitoring → Data Storage → ML Prediction → Dashboard Visualization
```

---

## 📸 Screenshots

<img width="1883" height="909" alt="image" src="https://github.com/user-attachments/assets/bf93abd4-1201-4e6f-84b8-a90bfd224edd" />

<img width="1856" height="534" alt="image" src="https://github.com/user-attachments/assets/585b44f2-a676-47a0-a35d-ac9f1fbfdacb" />

<img width="1877" height="480" alt="image" src="https://github.com/user-attachments/assets/dded17fe-c3e9-4371-bcd9-22b20a4cad38" />




* Dashboard
* API monitoring
* Prediction results
* Contract testing

---

## 🔐 Security Measures

✔ Input validation
✔ Error handling
✔ Secure database queries

⚠️ Planned Improvements:

* Authentication & Authorization
* Rate limiting
* SQL Injection prevention
* XSS protection

---

## 📈 Future Enhancements

* 📊 Failure history tracking (critical feature)
* 🔐 Advanced security implementation
* 📉 Real-time analytics
* ☁️ Cloud deployment

---

## 👨‍💻 Team

* Ashu Pal
* Anamika Gupta
* Hemant Raj

---

## 📊 Project Status

🟡 **Beta Version – Actively Improving**

---

## ⭐ Support

If you like this project, consider giving it a ⭐ on GitHub!

---
