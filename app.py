from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import os

from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

# MongoDB Setup
# Connecting to MongoDB Atlas cluster
client = MongoClient('mongodb+srv://floodDetection:floodDetection@cluster0.iaxod6v.mongodb.net/')
db = client['flood_db']
collection = db['sensor_data']
contacts_collection = db['contacts']

# Load Models
try:
    with open('flood_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
except Exception as e:
    model = None
    scaler = None
    print(f"Warning: Could not load model or scaler: {e}. Predictions will be simulated.")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        water_level = data.get('water_level')
        rainfall = data.get('rainfall')
        humidity = data.get('humidity')
        temperature = data.get('temperature', 25.0) # Default if missing
        soil_moisture = data.get('soil_moisture')

        if None in [water_level, rainfall, humidity, soil_moisture]:
            return jsonify({'error': 'Missing sensor data'}), 400

        # Input array
        input_data = np.array([[water_level, rainfall, humidity, soil_moisture]])
        
        if scaler and model:
            # Scale input
            scaled_input = scaler.transform(input_data)
            
            # Predict
            prediction_val = model.predict(scaled_input)[0]
            if hasattr(model, 'predict_proba'):
                probability = model.predict_proba(scaled_input)[0][1]
            else:
                probability = 0.99 if prediction_val == 1 else 0.01
            
            # Prediction logic
            status = "DANGER" if prediction_val == 1 else "SAFE"
        else:
            # Mock logic if models are not loaded
            status = "DANGER" if float(water_level) > 75 else "SAFE"
            probability = 0.85 if status == "DANGER" else 0.15
        
        doc = {
            'timestamp': datetime.utcnow(),
            'water_level': water_level,
            'rainfall': rainfall,
            'humidity': humidity,
            'soil_moisture': soil_moisture,
            'temperature': temperature,
            'prediction': status,
            'probability': float(probability)
        }
        
        # Store in MongoDB
        collection.insert_one(doc)
        
        # Clean up _id for JSON serialization
        doc['_id'] = str(doc['_id'])
        
        return jsonify({
            'prediction': status,
            'probability': probability,
            'timestamp': doc['timestamp'].isoformat(),
            'input_data': {
                'water_level': water_level,
                'rainfall': rainfall,
                'humidity': humidity,
                'soil_moisture': soil_moisture,
                'temperature': temperature
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-data', methods=['GET'])
def get_data():
    try:
        # Get last 60 entries sorted by time descending, then reverse to chronological
        data = list(collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(60))
        data.reverse()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/historical', methods=['GET'])
def get_historical():
    try:
        if os.path.exists('finalDataset.csv'):
            # Load dataset
            df = pd.read_csv('finalDataset.csv')
            # Compute averages
            averages = {
                'water_level': float(df['water_level'].mean()) if 'water_level' in df.columns else 0,
                'rainfall': float(df['rainfall'].mean()) if 'rainfall' in df.columns else 0,
                'humidity': float(df['humidity'].mean()) if 'humidity' in df.columns else 0,
                'soil_moisture': float(df['soil_moisture'].mean()) if 'soil_moisture' in df.columns else 0
            }
        else:
            averages = {
                'water_level': 45.5, 'rainfall': 20.2, 'humidity': 75.0, 'soil_moisture': 55.0
            }
        return jsonify(averages), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/compare-latest', methods=['GET'])
def compare_latest():
    try:
        # Current data
        latest = collection.find_one({}, {'_id': 0}, sort=[('timestamp', -1)])
        if not latest:
            latest = {
                'water_level': 0, 'rainfall': 0, 'humidity': 0, 'soil_moisture': 0
            }
        
        # Historical average
        try:
            if os.path.exists('finalDataset.csv'):
                df = pd.read_csv('finalDataset.csv')
                averages = {
                    'water_level': float(df['water_level'].mean()) if 'water_level' in df.columns else 0,
                    'rainfall': float(df['rainfall'].mean()) if 'rainfall' in df.columns else 0,
                    'humidity': float(df['humidity'].mean()) if 'humidity' in df.columns else 0,
                    'soil_moisture': float(df['soil_moisture'].mean()) if 'soil_moisture' in df.columns else 0
                }
            else:
                averages = {
                    'water_level': 45.5, 'rainfall': 20.2, 'humidity': 75.0, 'soil_moisture': 55.0
                }
        except Exception:
            averages = {
                'water_level': 45.5, 'rainfall': 20.2, 'humidity': 75.0, 'soil_moisture': 55.0
            }

        return jsonify({
            'current': latest,
            'historical_avg': averages
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# CONTACTS CRUD API
# ==========================================

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    try:
        contacts = list(contacts_collection.find())
        for c in contacts:
            c['_id'] = str(c['_id'])
        return jsonify(contacts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    try:
        data = request.json
        if not data or 'name' not in data or 'phone' not in data:
            return jsonify({'error': 'Name and phone required'}), 400
        
        doc = {
            'name': data['name'],
            'phone': data['phone'],
            'added_at': datetime.utcnow()
        }
        result = contacts_collection.insert_one(doc)
        doc['_id'] = str(result.inserted_id)
        return jsonify(doc), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<id>', methods=['DELETE'])
def delete_contact(id):
    try:
        contacts_collection.delete_one({'_id': ObjectId(id)})
        return jsonify({'message': 'Deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<id>', methods=['PUT'])
def update_contact(id):
    try:
        data = request.json
        update_fields = {}
        if 'name' in data:
            update_fields['name'] = data['name']
        if 'phone' in data:
            update_fields['phone'] = data['phone']
            
        contacts_collection.update_one({'_id': ObjectId(id)}, {'$set': update_fields})
        return jsonify({'message': 'Updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# ESP32 / GSM MODULE API
# ==========================================

@app.route('/api/get-alert-numbers', methods=['GET'])
def get_alert_numbers():
    try:
        # Returns just a flat array of numbers for the ESP32 GSM module
        contacts = list(contacts_collection.find({}, {'_id': 0, 'phone': 1}))
        numbers = [c['phone'] for c in contacts if 'phone' in c]
        return jsonify(numbers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)