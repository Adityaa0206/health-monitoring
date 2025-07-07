from flask import Flask, jsonify, request, render_template
import datetime
import os
import mysql.connector
import threading
import time
import random
import requests
from dotenv import load_dotenv

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("MYSQLHOST"),
    user=os.getenv("MYSQLUSER"),
    password=os.getenv("MYSQLPASSWORD"),
    database=os.getenv("MYSQLDATABASE"),
    port=int(os.environ.get("MYSQLPORT", 3306))
)
cursor = db.cursor()

app = Flask(__name__, template_folder="backend/templates", static_folder="static")

@app.route("/api/health", methods=["POST"])
def receive_health_data():
    data = request.get_json()
    bpm = data.get("bpm")
    spo2 = data.get("spo2")
    temperature = data.get("temperature")
    timestamp = datetime.datetime.now()

    sql = "INSERT INTO sensor_data (bpm, spo2, temperature, timestamp) VALUES (%s, %s, %s, %s)"
    values = (bpm, spo2, temperature, timestamp)
    cursor.execute(sql, values)
    db.commit()

    return jsonify({"status": "success", "message": "Health data saved to MySQL"}), 200

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/health/latest", methods=["GET"])
def get_latest_health_data():
    cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1")
    latest = cursor.fetchone()
    if latest:
        data = {
            "id": latest[0],
            "bpm": latest[1],
            "spo2": latest[2],
            "temperature": latest[3],
            "timestamp": latest[4].strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(data)
    else:
        return jsonify({"error": "No data found"}), 404

@app.route("/api/history", methods=["GET"])
def health_history():
    cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()

    history = []
    for row in rows[::-1]:
        record = {
            'id': row[0],
            'bpm': row[1],
            'spo2': row[2],
            'temperature': row[3],
            'timestamp': row[4].strftime('%H:%M:%S')
        }
        history.append(record)

    return jsonify(history)

# 🧠 Simulated data sender (runs every 10 seconds)
def simulate_data():
    while True:
        data = {
            "bpm": random.randint(60, 100),
            "spo2": random.randint(90, 100),
            "temperature": round(random.uniform(36.0, 37.5), 1)
        }

        try:
            requests.post(
                "https://health-monitoring-c45l.onrender.com" \
                "",
                json=data,
                timeout=5
            )
            print("[SIMULATION] Data sent:", data)
        except Exception as e:
            print("[SIMULATION ERROR]", e)

        time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=simulate_data, daemon=True).start()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
