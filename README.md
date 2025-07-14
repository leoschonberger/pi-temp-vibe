# Temperature Monitoring System

A comprehensive temperature monitoring system built with Python Flask backend, MongoDB database, and a web-based dashboard. Designed to collect temperature data from multiple Raspberry Pi Pico devices and visualize it in real-time.

## AI Disclaimer

This project is largely build using Cursor AI. The quality of the code is not guaranteed and is not intended for use in any serious capacity. This project was created for personal use and learning purposes. It is not intended to be a representation of my coding skills or abilities.

## Features

- **Multi-source data collection**: Support for multiple Raspberry Pi Pico devices
- **Real-time visualization**: Interactive line charts with time-based filtering
- **Docker-based deployment**: Easy setup with Docker Compose
- **MongoDB storage**: Persistent data storage with no automatic deletion
- **RESTful API**: Simple endpoints for data submission and retrieval
- **Responsive web interface**: Works on desktop and mobile devices

## Project Structure

```
temp-monitor/
├── docker-compose.yml          # Main Docker Compose configuration
├── backend/
│   ├── Dockerfile             # Backend API container
│   ├── requirements.txt       # Python dependencies
│   ├── app.py                 # Flask API server
│   └── models.py              # Data models
├── frontend/
│   ├── Dockerfile             # Frontend container
│   ├── requirements.txt       # Flask web dependencies
│   ├── app.py                 # Flask web server
│   ├── templates/
│   │   └── index.html         # Main dashboard template
│   └── static/
│       ├── css/
│       │   └── style.css      # Dashboard styles
│       └── js/
│           └── dashboard.js   # Chart and interaction logic
├── micropython/
│   └── pico_temp_sensor.py    # Sample MicroPython code for Pico
└── README.md                  # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed on your Raspberry Pi Zero W
- Raspberry Pi Pico with MicroPython firmware
- Temperature sensor (DHT22, DS18B20, or similar)

### Installation

1. **Clone or download this project to your Raspberry Pi Zero W**

2. **Start the services**:

   ```bash
   docker-compose up -d
   ```

3. **Access the dashboard**:

   - Open your browser and go to `http://your-pi-zero-ip:5000`
   - The API will be available at `http://your-pi-zero-ip:5001`

4. **Upload MicroPython code to your Pico**:
   - Copy the code from `micropython/pico_temp_sensor.py`
   - Modify the `API_URL` and `SENSOR_NAME` variables
   - Upload to your Pico using Thonny or your preferred IDE

## API Endpoints

### Submit Temperature Data

```
POST /api/temperature
Content-Type: application/json

{
  "sensor_name": "pico_1",
  "temperature": 23.5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Get Latest Reading

```
GET /api/temperature/latest?sensor_name=pico_1
```

### Get Historical Data

```
GET /api/temperature/history?sensor_name=pico_1&hours=24
```

## MicroPython Setup for Raspberry Pi Pico

### Hardware Requirements

- Raspberry Pi Pico or Pico W
- Temperature sensor (DHT22 recommended)
- Breadboard and jumper wires

### Wiring (DHT22)

- VCC → 3.3V
- GND → GND
- Data → GP15 (or any digital pin)

### Software Setup

1. **Install MicroPython firmware** on your Pico
2. **Copy the sensor code** from `micropython/pico_temp_sensor.py`
3. **Modify configuration**:
   - Set `WIFI_SSID` and `WIFI_PASSWORD`
   - Set `API_URL` to your Pi Zero's IP address
   - Set `SENSOR_NAME` to a unique identifier
4. **Upload and run** the code

### Sample MicroPython Code

```python
# See micropython/pico_temp_sensor.py for complete code
import network
import urequests
import dht
import machine
import time

# Configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"
API_URL = "http://192.168.1.100:5001/api/temperature"
SENSOR_NAME = "pico_1"

# Initialize sensor
dht_sensor = dht.DHT22(machine.Pin(15))

def connect_wifi():
    # WiFi connection code here
    pass

def read_temperature():
    # Temperature reading code here
    pass

def send_data(temperature):
    # API submission code here
    pass

# Main loop
while True:
    try:
        temp = read_temperature()
        send_data(temp)
        time.sleep(300)  # Send data every 5 minutes
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
```

## Configuration

### Environment Variables

You can modify the following in `docker-compose.yml`:

- `MONGO_INITDB_ROOT_USERNAME`: MongoDB admin username
- `MONGO_INITDB_ROOT_PASSWORD`: MongoDB admin password
- `MONGO_DB_NAME`: Database name for temperature data

### Port Configuration

- **Frontend**: Port 5000 (http://your-pi-ip:5000)
- **Backend API**: Port 5001 (http://your-pi-ip:5001)
- **MongoDB**: Port 27017 (internal only)

## Data Visualization

The dashboard provides:

- **Line charts** for each sensor showing temperature over time
- **Time filters**: 6 hours, 1 day, 1 week, 1 month, 3 months, 6 months, 1 year
- **Auto-refresh**: Charts update automatically every 30 seconds
- **Responsive design**: Works on mobile and desktop

## Troubleshooting

### Common Issues

1. **Pico can't connect to WiFi**

   - Check SSID and password
   - Ensure Pico W is being used (regular Pico has no WiFi)

2. **API connection fails**

   - Verify Pi Zero IP address in Pico code
   - Check if Docker containers are running: `docker-compose ps`

3. **No data showing in dashboard**
   - Check MongoDB connection
   - Verify API endpoints are working
   - Check browser console for JavaScript errors

### Logs

View container logs:

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb
```

## Performance Considerations

- **Storage**: Data is kept indefinitely, monitor disk space
- **Memory**: MongoDB may use significant RAM with large datasets
- **Network**: Consider data transmission frequency for battery-powered Picos

## Security Notes

- This setup is designed for local network use
- No authentication is implemented
- Consider adding authentication for production use
- Change default MongoDB credentials

## Contributing

Feel free to submit issues and enhancement requests! This is a work in progress and is provide as is without any warranty. The code is not production ready and is not intended for use in a production environment.
