import requests
import time
import random

url = "http://localhost:5000/predict"

print("Starting sensor simulator... Press Ctrl+C to stop.")
try:
    while True:
        # Generate random sensor data
        # Sometimes generate a spike to trigger DANGER
        if random.random() > 0.85:
            water_level = round(random.uniform(76, 95), 2)
        else:
            water_level = round(random.uniform(40, 70), 2)
            
        data = {
            "water_level": water_level,
            "rainfall": round(random.uniform(0, 30), 2),
            "humidity": round(random.uniform(50, 95), 2),
            "soil_moisture": round(random.uniform(20, 70), 2),
            "temperature": round(random.uniform(20, 40), 2)
        }
        
        try:
            response = requests.post(url, json=data)
            res_data = response.json()
            print(f"Sent: {data} | Status: {res_data.get('prediction', 'ERR')} (Prob: {res_data.get('probability', 0):.2f})")
        except Exception as e:
            print(f"Error connecting to server: {e}. Is Flask running?")
            
        time.sleep(5)
except KeyboardInterrupt:
    print("\nSimulator stopped.")
