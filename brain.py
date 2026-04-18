import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import time
import subprocess
import threading
from flask import Flask, jsonify, request, render_template
from datetime import datetime

PROMETHEUS_URL = "http://localhost:9090"
METRIC_NAME = "nginx_connections_active"
LOOKBACK_MINUTES = 30
SERVICE_NAME = "web_app"
COST_PER_SERVER_PER_SEC = 0.02

# Global Variables
system_state = {
    "traffic": 0,
    "prediction": 0,
    "scale": 1,
    "cost": 0.0,
    "budget_status": "OK",
    "budget_limit": 50.00,
    "capacity_per_server": 20,
    "logs": [] 
}

def log_event(message):
    """Adds a timestamped message to the logs."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    print(formatted_msg) 
    system_state["logs"].insert(0, formatted_msg)
    if len(system_state["logs"]) > 50:
        system_state["logs"].pop()


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/stats')
def stats():
    return jsonify(system_state)

@app.route('/api/reset_budget', methods=['POST'])
def reset_budget():
    system_state["cost"] = 0.0
    system_state["budget_status"] = "OK"
    log_event(" FINANCIAL RESET: Cost cleared to $0.00")
    return jsonify({"status": "reset"})

@app.route('/api/set_budget', methods=['POST'])
def set_budget():
    data = request.json
    new_limit = float(data.get('limit', 50.0))
    system_state["budget_limit"] = new_limit
    if system_state["cost"] < new_limit:
        system_state["budget_status"] = "OK"
    log_event(f" BUDGET UPDATE: New Limit is ${new_limit:.2f}")
    return jsonify({"status": "updated"})

@app.route('/api/set_sensitivity', methods=['POST'])
def set_sensitivity():
    data = request.json
    new_cap = int(data.get('capacity', 20))
    system_state["capacity_per_server"] = new_cap
    log_event(f" TUNING UPDATE: 1 Server handles {new_cap} users")
    return jsonify({"status": "updated"})

def run_dashboard():
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)


def fetch_data():
    end_time = time.time()
    start_time = end_time - (LOOKBACK_MINUTES * 60)
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params={
            'query': METRIC_NAME, 'start': start_time, 'end': end_time, 'step': '15s'
        })
        results = response.json()['data']['result']
        if not results: return pd.DataFrame()
        values = results[0]['values']
        df = pd.DataFrame(values, columns=['timestamp', 'traffic'])
        df['traffic'] = df['traffic'].astype(float)
        return df
    except:
        return pd.DataFrame()

def prepare_features(df):
    df = df.copy()
    df['lag_1m'] = df['traffic'].shift(4)
    df['velocity'] = df['traffic'].diff()
    df = df.dropna()
    return df

def scale_docker(n_containers):
    if n_containers == system_state["scale"]:
        return
    
    log_event(f"⚡ ACTION: Scaling to {n_containers} containers...")
    cmd = f"docker compose up -d --scale {SERVICE_NAME}={n_containers} --no-recreate"
    subprocess.run(cmd, shell=True)
    subprocess.run("docker compose exec nginx nginx -s reload", shell=True)
    system_state["scale"] = n_containers

def ai_loop():
    log_event("AI Autoscaler Active... (Waiting for data)")
    model = RandomForestRegressor(n_estimators=100)
    
    while True:
        system_state["cost"] += system_state["scale"] * COST_PER_SERVER_PER_SEC * 5
        df = fetch_data()
        
        if len(df) > 20:
            current_traffic = df['traffic'].iloc[-1]
            
            # Predict
            df_features = prepare_features(df)
            X = df_features[['lag_1m', 'velocity']]
            y = df_features['traffic']
            model.fit(X, y)
            current_lag = df['traffic'].iloc[-5]
            current_velocity = df['traffic'].diff().iloc[-1]
            prediction = model.predict([[current_lag, current_velocity]])[0]
            
            system_state["traffic"] = current_traffic
            system_state["prediction"] = prediction

            # Budget Logic
            if system_state["cost"] >= system_state["budget_limit"]:
                max_containers = 5
                system_state["budget_status"] = "EXCEEDED"
                prefix = " ECONOMY"
            else:
                max_containers = 10
                system_state["budget_status"] = "OK"
                prefix = " NORMAL"

            # Scaling Logic
            cap = system_state["capacity_per_server"]
            req = max(int(prediction/cap)+1, int(current_traffic/cap)+1)
            final = min(req, max_containers)
            if final < 1: final = 1
            
            log_event(f"{prefix} | Used: ${system_state['cost']:.2f} | Pred: {prediction:.0f} | Target: {final}")
            scale_docker(final)
        
        else:
            print(f" Warming up... {len(df)}/20") 
            
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_dashboard, daemon=True).start()
    ai_loop()