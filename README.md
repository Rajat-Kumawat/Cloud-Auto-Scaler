# 🧠 AI-Driven Predictive Autoscaling System

A college project demonstrating **Predictive Autoscaling** using Machine Learning. Unlike traditional autoscalers that react *after* a crash, this system predicts traffic spikes and scales infrastructure *before* the load hits.

built for **Prayogam 2026**.

## 🚀 Overview

This project simulates a real-world cloud environment using Docker. It includes a custom AI "Brain" that monitors network traffic in real-time, forecasts future demand using a Random Forest model, and automatically adds or removes servers (containers) to handle the load efficiently.

### ✨ Key Features
* **🔮 Predictive AI:** Uses `RandomForestRegressor` to forecast traffic 1 minute into the future.
* **⚖️ Smart Load Balancing:** Nginx distributes traffic across dynamic Docker containers.
* **📈 Real-Time Monitoring:** Prometheus scrapes metrics every 5 seconds.
* **🌊 Traffic Simulation:** Locust generates realistic "Sine Wave" traffic patterns for training.
* **⚡ Autonomous Scaling:** Python script manages Docker Compose to scale up/down automatically.

---

## 🏗️ Architecture

The system consists of 5 distinct phases working in a closed control loop:

1.  **The Target:** A Flask Web App running in Docker containers behind an Nginx Load Balancer.
2.  **The Monitor:** Prometheus database collects `nginx_connections_active` metrics.
3.  **The Traffic:** Locust generates sine-wave user patterns to stress-test the system.
4.  **The Brain:** `brain.py` fetches data, trains the model on the fly, and predicts load.
5.  **The Actuator:** Docker SDK scales the web application based on the AI's recommendations.

---

## 🛠️ Tech Stack

* **Language:** Python 3.9
* **Containerization:** Docker & Docker Compose
* **AI/ML:** Scikit-Learn (Random Forest), Pandas, NumPy
* **Web Server:** Flask (Python) + Nginx (Reverse Proxy)
* **Monitoring:** Prometheus + Nginx Exporter
* **Load Testing:** Locust

---

## ⚙️ Installation & Setup

# 1. Install Project Dependencies (Brain & Simulation)
pip install -r requirements-dev.txt

# 2. Build the Docker System
docker compose up -d --build

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop) (Running)
* Python 3.x installed

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/autoscaling-project.git](https://github.com/yourusername/autoscaling-project.git)
cd autoscaling-project