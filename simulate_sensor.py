import requests
import random
import time

URL = "https://health-monitoring-5.onrender.com/api/health"



while True:
    data = {
        "bpm": random.randint(60, 140),
        "spo2": round(random.uniform(92.0, 100.0), 1),
        "temperature": round(random.uniform(36.0, 39.0), 1)
    }

    try:
        response = requests.post(URL, json=data)
        print("Sent:", data, "| Server responded:", response.status_code)
    except Exception as e:
        print("Error:", e)

    time.sleep(5) 
