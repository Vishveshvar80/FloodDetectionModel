# IoT-Based Flood Monitoring & Prediction System

The system is split into two parts: a Flask backend for the ML logic + MongoDB storage, and a Vite + React frontend for real-time visualization.

## Prerequisites
- **Python 3.8+**
- **Node.js 18+**
- **MongoDB** (Ensure MongoDB is installed and running locally on the default port `27017`)

## Project Structure

```text
e:/FinalYrProject/
├── app.py                     # Flask application and API endpoints
├── requirements.txt           # Python dependencies
├── setup_dummy_files.py       # Script to generate sample ML model & dataset
├── sensor_simulator.py        # Script to simulate IoT sensor data continuously
└── frontend/                  # React Frontend App
    ├── package.json           # Node dependencies
    ├── vite.config.js         # Vite configuration
    ├── index.html             # Main HTML file
    └── src/                   # React components and styling
        ├── App.jsx
        ├── main.jsx
        ├── index.css
        └── components/
            ├── Dashboard.jsx  # Main dashboard logic and charts
            └── Dashboard.css  # Dashboard styling
```

## Step 1: Backend Setup

Open a terminal and navigate to the project root:
```bash
cd e:/FinalYrProject
```

Create a virtual environment and install dependencies:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Generate Dummy Data & Models:
(This avoids missing file errors if you don't have the real model files yet)
```bash
python setup_dummy_files.py
```

Run the Flask API Server:
```bash
python app.py
```
*The backend should now be running on `http://localhost:5000`*

## Step 2: Frontend Setup

Open a new terminal and navigate to the frontend folder:
```bash
cd e:/FinalYrProject/frontend
```

Install dependencies:
```bash
npm install
```

Run the React App:
```bash
npm run dev
```
*The frontend should now be running on `http://localhost:3000`*

## Step 3: Simulate IoT Data

To see the dashboard come to life, we need an IoT sensor to send data! I've included a script that pretends to be a sensor and streams data every 5 seconds.

Open a third terminal, navigate to the project root, and run:
```bash
cd e:/FinalYrProject
.\venv\Scripts\activate
python sensor_simulator.py
```

### Done! 🎉
Open your browser to `http://localhost:3000` to view the beautiful real-time React dashboard updating live from the simulated IoT inputs!
