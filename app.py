from flask import Flask, jsonify, request, render_template
import datetime
import mysql.connector

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Adityaharsh0206",  # Replace with your actual password
    database="health_monitoring"
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
if __name__ == "__main__":
    app.run(debug=True)
