from flask import Flask
import time
import random
import os

app = Flask(__name__)

@app.route('/')
def index():
    
    delay = random.uniform(0.1, 0.3)
    time.sleep(delay)
    
    container_id = os.uname()[1]
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Autoscaling Demo</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5; margin: 0; }}
            .card {{ background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; width: 300px; }}
            h1 {{ color: #0070f3; margin-top: 0; font-size: 24px; }}
            .id-box {{ background: #eef6ff; color: #0070f3; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 20px; font-weight: bold; margin: 20px 0; border: 1px solid #cce4ff; }}
            .stats {{ color: #666; font-size: 14px; }}
            .status {{ display: inline-block; width: 10px; height: 10px; background-color: #28a745; border-radius: 50%; margin-right: 5px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>☁️ AI Cloud Node</h1>
            <div><span class="status"></span>Online</div>
            <div class="id-box">{container_id}</div>
            <div class="stats">Processing Time: {delay:.2f}s</div>
        </div>
    </body>
    </html>
    """

@app.route('/status')
def status():
    return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)