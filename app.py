from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# Load model
model = joblib.load("flood_model.pkl")
scaler = joblib.load("scaler.pkl")

@app.route('/predict', methods=['POST'])
def predict():

    data = request.json

    input_data = pd.DataFrame([data])

    input_scaled = scaler.transform(input_data)

    prediction = model.predict(input_scaled)[0]

    result = "DANGER" if prediction == 1 else "SAFE"

    return jsonify({"prediction": result})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)