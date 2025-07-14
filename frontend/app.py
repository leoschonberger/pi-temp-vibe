from flask import Flask, render_template, jsonify, request
import requests
import os

app = Flask(__name__)

# Backend API URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5001')

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/sensors')
def get_sensors():
    """Proxy to backend sensors endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/sensors")
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/temperature/history')
def get_temperature_history():
    """Proxy to backend temperature history endpoint"""
    try:
        sensor_name = request.args.get('sensor_name')
        hours = request.args.get('hours', '24')
        
        response = requests.get(
            f"{BACKEND_URL}/api/temperature/history",
            params={'sensor_name': sensor_name, 'hours': hours}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/temperature/latest')
def get_latest_temperature():
    """Proxy to backend latest temperature endpoint"""
    try:
        sensor_name = request.args.get('sensor_name')
        
        response = requests.get(
            f"{BACKEND_URL}/api/temperature/latest",
            params={'sensor_name': sensor_name}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 