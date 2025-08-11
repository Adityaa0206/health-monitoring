from flask import Flask, jsonify, request, render_template
import datetime
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

app = Flask(__name__, template_folder="backend/templates", static_folder="static")

# Try to connect to MySQL, if fails, set db and cursor to None
try:
    db = mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.environ.get("MYSQLPORT", 3306))
    )
    cursor = db.cursor()
except mysql.connector.Error as err:
    print("Warning: Could not connect to MySQL database locally:", err)
    db = None
    cursor = None

@app.route("/api/health", methods=["POST"])
def receive_health_data():
    if not cursor or not db:
        return jsonify({"error": "Database not connected"}), 500

    data = request.get_json()
    bpm = data.get("bpm")
    spo2 = data.get("spo2")
    temperature = data.get("temperature")
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert into sensor_data table
    sql = "INSERT INTO sensor_data (bpm, spo2, temperature, timestamp) VALUES (%s, %s, %s, %s)"
    values = (bpm, spo2, temperature, timestamp)
    cursor.execute(sql, values)
    db.commit()

    # Check for warnings
    warnings = []
    if bpm is not None and bpm > 100:
        warnings.append("High heart rate detected!")
    if spo2 is not None and spo2 < 95:
        warnings.append("Low oxygen saturation detected!")
    if temperature is not None and temperature > 38:
        warnings.append("High temperature detected!")

    # Log warnings if any
    if warnings:
        warning_text = "; ".join(warnings)
        log_sql = "INSERT INTO warning_logs (bpm, spo2, temperature, warnings, timestamp) VALUES (%s, %s, %s, %s, %s)"
        log_values = (bpm, spo2, temperature, warning_text, timestamp)
        cursor.execute(log_sql, log_values)
        db.commit()

    return jsonify({"status": "success", "message": "Health data saved to MySQL"}), 200

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/health/latest", methods=["GET"])
def get_latest_health_data():
    if not cursor:
        return jsonify({"error": "Database not connected"}), 500

    cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1")
    latest = cursor.fetchone()
    if latest:
        data = {
            "id": latest[0],
            "bpm": latest[1],
            "spo2": latest[2],
            "temperature": latest[3],
            "timestamp": latest[4].strftime("%Y-%m-%d %H:%M:%S"),
            "warnings": []
        }

        # Generate warnings on latest data too (optional but useful)
        if data["bpm"] > 100:
            data["warnings"].append("High heart rate detected!")
        if data["spo2"] < 95:
            data["warnings"].append("Low oxygen saturation detected!")
        if data["temperature"] > 38:
            data["warnings"].append("High temperature detected!")

        return jsonify(data)
    else:
        return jsonify({"error": "No data found"}), 404

@app.route("/api/history", methods=["GET"])
def health_history():
    if not cursor:
        return jsonify({"error": "Database not connected"}), 500

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

@app.route("/api/warnings", methods=["GET"])
def get_warning_logs():
    if not cursor:
        return jsonify({"error": "Database not connected"}), 500

    cursor.execute("SELECT * FROM warning_logs ORDER BY timestamp DESC LIMIT 20")
    rows = cursor.fetchall()

    logs = []
    for row in rows:
        logs.append({
            "id": row[0],
            "bpm": row[1],
            "spo2": row[2],
            "temperature": row[3],
            "warnings": row[4],
            "timestamp": row[5].strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(logs)

if __na
