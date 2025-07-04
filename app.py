from flask import Flask, jsonify, request, render_template
import datetime
import os
import mysql.connector



# Connect to MySQL
db = mysql.connector.connect(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_NAME"),
    port=int(os.environ.get("DB_PORT"))
)

cursor = db.cursor()
app = Flask(__name__, template_folder="backend/templates", static_folder="static")

# Route to receive health data (used by simulate_sensor.py)
@app.route("/api/health", methods=["POST"])
def receive_health_data():
    data = request.get_json()
    bpm = data.get("bpm")
    spo2 = data.get("spo2")
    temperature = data.get("temperature")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sql = "INSERT INTO sensor_data (bpm, spo2, temperature, timestamp) VALUES (%s, %s, %s, %s)"
    values = (bpm, spo2, temperature, timestamp)
    cursor.execute(sql, values)
    db.commit()

    print(f"[{timestamp}] Received health data: {data}")
    return jsonify({"status": "success", "message": "Health data saved to MySQL"}), 200

# Route to render dashboard.html
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# ✅ NEW: Route to serve latest health data (used by Chart.js)
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

# Run Flask app
# API to fetch last 10 sensor readings (for chart)
@app.route('/api/history', methods=["GET"])
def health_history():
    cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()

    history = []
    for row in rows[::-1]:  # reverse to get chronological order
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
    app.run(debug=True)
