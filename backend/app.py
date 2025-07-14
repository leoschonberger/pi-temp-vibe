from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from models import TemperatureReading

app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://admin:tempmonitor123@localhost:27017/temperature_db?authSource=admin')
client = MongoClient(MONGODB_URI)
db = client.get_database()
temperature_collection = db.temperature_readings

@app.route('/api/temperature', methods=['POST'])
def submit_temperature():
    """Submit temperature data from a sensor"""
    try:
        data = request.get_json()
        
        if not data or 'sensor_name' not in data or 'temperature' not in data:
            return jsonify({'error': 'Missing required fields: sensor_name and temperature'}), 400
        
        # Parse timestamp if provided, otherwise use current time
        timestamp = None
        if 'timestamp' in data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid timestamp format'}), 400
        
        # Create temperature reading
        reading = TemperatureReading(
            sensor_name=data['sensor_name'],
            temperature=float(data['temperature']),
            timestamp=timestamp
        )
        
        # Store in MongoDB
        result = temperature_collection.insert_one(reading.to_dict())
        
        return jsonify({
            'message': 'Temperature data recorded successfully',
            'id': str(result.inserted_id)
        }), 201
        
    except ValueError:
        return jsonify({'error': 'Invalid temperature value'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/temperature/latest', methods=['GET'])
def get_latest_temperature():
    """Get the latest temperature reading for a specific sensor"""
    try:
        sensor_name = request.args.get('sensor_name')
        if not sensor_name:
            return jsonify({'error': 'sensor_name parameter is required'}), 400
        
        # Find the latest reading for the sensor
        latest = temperature_collection.find_one(
            {'sensor_name': sensor_name},
            sort=[('timestamp', -1)]
        )
        
        if not latest:
            return jsonify({'error': 'No data found for sensor'}), 404
        
        # Remove MongoDB _id field
        latest.pop('_id', None)
        return jsonify(latest), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/temperature/history', methods=['GET'])
def get_temperature_history():
    """Get historical temperature data for a sensor with time filtering"""
    try:
        sensor_name = request.args.get('sensor_name')
        hours = request.args.get('hours', '24')
        
        if not sensor_name:
            return jsonify({'error': 'sensor_name parameter is required'}), 400
        
        try:
            hours = int(hours)
        except ValueError:
            return jsonify({'error': 'Invalid hours parameter'}), 400
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Query MongoDB for data in the time range
        cursor = temperature_collection.find({
            'sensor_name': sensor_name,
            'timestamp': {
                '$gte': start_time.isoformat(),
                '$lte': end_time.isoformat()
            }
        }).sort('timestamp', 1)
        
        # Convert cursor to list and remove MongoDB _id fields
        readings = []
        for doc in cursor:
            doc.pop('_id', None)
            readings.append(doc)
        
        return jsonify({
            'sensor_name': sensor_name,
            'time_range_hours': hours,
            'readings': readings,
            'count': len(readings)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    """Get list of all available sensors"""
    try:
        # Get unique sensor names from the database
        sensors = temperature_collection.distinct('sensor_name')
        
        # Get latest reading for each sensor
        sensor_data = []
        for sensor_name in sensors:
            latest = temperature_collection.find_one(
                {'sensor_name': sensor_name},
                sort=[('timestamp', -1)]
            )
            if latest:
                sensor_data.append({
                    'name': sensor_name,
                    'latest_temperature': latest['temperature'],
                    'latest_timestamp': latest['timestamp']
                })
        
        return jsonify({'sensors': sensor_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        client.admin.command('ping')
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 