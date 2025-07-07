from flask import Flask, jsonify, request, render_template
import datetime
import os
from dotenv import load_dotenv

import mysql.connector
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
    timestamp = datetime.datetime.fromtimestamp(row[4]).strftime('%H:%M:%S')


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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))  you can check my app.py