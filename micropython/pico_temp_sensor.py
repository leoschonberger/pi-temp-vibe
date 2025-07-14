"""
Temperature Sensor for Raspberry Pi Pico
Sends temperature data to the monitoring API
"""

import network
import urequests
import dht
import machine
import time
import json
from machine import Pin
import gc

# Configuration - MODIFY THESE VALUES
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"
API_URL = "http://192.168.1.100:5001/api/temperature"  # Change to your Pi Zero IP
SENSOR_NAME = "pico_1"  # Unique name for this sensor
SENSOR_PIN = 15  # GPIO pin connected to DHT22 data pin
READING_INTERVAL = 60  # Send data every 5 minutes (300 seconds)
RETRY_INTERVAL = 30  # Retry interval on error (60 seconds)

# Initialize hardware
dht_sensor = dht.DHT22(Pin(SENSOR_PIN))
led = Pin("LED", Pin.OUT)  # Built-in LED for status indication

def connect_wifi():
    """Connect to WiFi network"""
    print("Connecting to WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected to WiFi")
        return True
    
    try:
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection with timeout
        max_wait = 20
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print("Waiting for connection...")
            time.sleep(1)
        
        if wlan.isconnected():
            print("WiFi connected successfully")
            print(f"IP address: {wlan.ifconfig()[0]}")
            return True
        else:
            print("WiFi connection failed")
            return False
            
    except Exception as e:
        print(f"WiFi connection error: {e}")
        return False

def read_temperature():
    """Read temperature from DHT22 sensor"""
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        print(f"Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
        return temperature
        
    except Exception as e:
        print(f"Error reading sensor: {e}")
        return None

def send_data(temperature):
    """Send temperature data to API"""
    try:
        # Prepare data payload
        data = {
            "sensor_name": SENSOR_NAME,
            "temperature": temperature,
            "timestamp": time.time()  # Unix timestamp
        }
        
        print(f"Sending data: {data}")
        
        # Send POST request
        response = urequests.post(
            API_URL,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 201:
            print("Data sent successfully")
            response.close()
            return True
        else:
            print(f"API error: {response.status_code}")
            response.close()
            return False
            
    except Exception as e:
        print(f"Error sending data: {e}")
        return False

def blink_led(times=1, duration=0.1):
    """Blink the built-in LED for status indication"""
    for _ in range(times):
        led.on()
        time.sleep(duration)
        led.off()
        time.sleep(duration)

def main():
    """Main program loop"""
    print("Temperature Sensor Starting...")
    print(f"Sensor Name: {SENSOR_NAME}")
    print(f"API URL: {API_URL}")
    print(f"Reading Interval: {READING_INTERVAL} seconds")
    
    # Initial LED blink
    blink_led(3, 0.2)
    
    # Connect to WiFi
    if not connect_wifi():
        print("Failed to connect to WiFi. Check your credentials.")
        blink_led(5, 0.5)  # Error indication
        return
    
    # Success indication
    blink_led(2, 0.1)
    
    last_send_time = 0
    
    while True:
        try:
            current_time = time.time()
            
            # Check if it's time to send data
            if current_time - last_send_time >= READING_INTERVAL:
                print(f"\n--- Reading at {time.localtime()} ---")
                
                # Read temperature
                temperature = read_temperature()
                
                if temperature is not None:
                    # Send data to API
                    if send_data(temperature):
                        last_send_time = current_time
                        blink_led(1, 0.1)  # Success blink
                    else:
                        print("Failed to send data, will retry later")
                        blink_led(2, 0.3)  # Error blink
                else:
                    print("Failed to read temperature, will retry later")
                    blink_led(2, 0.3)  # Error blink
                
                # Garbage collection to free memory
                gc.collect()
            
            # Small delay to prevent excessive CPU usage
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\nProgram interrupted by user")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(RETRY_INTERVAL)

def test_sensor():
    """Test function to verify sensor is working"""
    print("Testing DHT22 sensor...")
    
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        print(f"Temperature: {temperature:.1f}°C")
        print(f"Humidity: {humidity:.1f}%")
        print("Sensor test successful!")
        
    except Exception as e:
        print(f"Sensor test failed: {e}")

def test_wifi():
    """Test function to verify WiFi connection"""
    print("Testing WiFi connection...")
    
    if connect_wifi():
        print("WiFi test successful!")
        return True
    else:
        print("WiFi test failed!")
        return False

def test_api():
    """Test function to verify API connection"""
    print("Testing API connection...")
    
    if not connect_wifi():
        print("WiFi not connected, cannot test API")
        return False
    
    try:
        # Send test data
        test_data = {
            "sensor_name": f"{SENSOR_NAME}_test",
            "temperature": 25.0,
            "timestamp": time.time()
        }
        
        response = urequests.post(
            API_URL,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 201:
            print("API test successful!")
            response.close()
            return True
        else:
            print(f"API test failed: {response.status_code}")
            response.close()
            return False
            
    except Exception as e:
        print(f"API test error: {e}")
        return False

# Run main program
if __name__ == "__main__":
    main()

# Uncomment the following lines to run tests instead of main program
# test_sensor()
# test_wifi()
# test_api() 